from fastapi import APIRouter, HTTPException
from sqlalchemy import select, func, update

from app.database import db_dep
from app.models import ShopComment, Shop, Order, OrderItem, Item
from app.dependencies import current_user_jwt_dep
from app.schemas import (
    ShopCommentCreateRequest,
    ShopCommentCreateResponse,
    ShopCommentListResponse,
)

router = APIRouter(prefix="/shop-comments", tags=["Shop Comments"])


@router.post("/create/{shop_id}", response_model=ShopCommentCreateResponse)
async def shop_comment_create(
    session: db_dep,
    current_user: current_user_jwt_dep,
    data: ShopCommentCreateRequest,
    shop_id: int,
):
    shop_stmt = select(Shop).where(Shop.id == shop_id)
    shop = session.execute(shop_stmt).scalar_one_or_none()

    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")

    # Do'kon buyumalarini topish va foydalanuvchining buyurtmasi borligini tekshirish
    shop_items_stmt = select(Item.id).where(Item.shop_id == shop_id)
    shop_items = session.execute(shop_items_stmt).scalars().all()

    if shop_items:
        order_item_stmt = select(OrderItem).where(
            OrderItem.item_id.in_(shop_items)
        ).limit(1)
        
        has_order = session.execute(order_item_stmt).scalar_one_or_none()
        
        if not has_order:
            raise HTTPException(
                status_code=400, 
                detail="You must have ordered from this shop to leave a comment"
            )

    existing_comment_stmt = select(ShopComment).where(
        ShopComment.user_id == current_user.id, ShopComment.shop_id == shop_id
    )
    existing_comment = session.execute(existing_comment_stmt).scalar_one_or_none()

    if existing_comment:
        existing_comment.text = data.text
        existing_comment.rating = data.rating
        session.add(existing_comment)
    else:
        comment = ShopComment(
            shop_id=shop_id,
            user_id=current_user.id,
            text=data.text,
            rating=data.rating,
        )
        session.add(comment)

    session.commit()

    # Do'kon reitingini qayta hisoblash
    rating_stmt = select(
        func.coalesce(func.round(func.avg(ShopComment.rating)), 0)
    ).where(ShopComment.shop_id == shop_id, ShopComment.is_active == True)

    avg_rating = session.execute(rating_stmt).scalar()

    shop_update_stmt = update(Shop).where(Shop.id == shop_id).values(rating=avg_rating)
    session.execute(shop_update_stmt)
    session.commit()

    session.refresh(existing_comment if existing_comment else comment)

    return existing_comment if existing_comment else comment


@router.get("/list/{shop_id}", response_model=list[ShopCommentListResponse])
async def shop_comments_list(session: db_dep, shop_id: int, skip: int = 0, limit: int = 10):
    stmt = (
        select(ShopComment)
        .where(ShopComment.shop_id == shop_id, ShopComment.is_active == True)
        .order_by(ShopComment.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    comments = session.execute(stmt).scalars().all()

    return comments


@router.get("/{comment_id}", response_model=ShopCommentListResponse)
async def shop_comment_detail(session: db_dep, comment_id: int):
    stmt = select(ShopComment).where(ShopComment.id == comment_id)
    comment = session.execute(stmt).scalar_one_or_none()

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    return comment


@router.delete("/{comment_id}")
async def shop_comment_delete(
    session: db_dep, current_user: current_user_jwt_dep, comment_id: int
):
    stmt = select(ShopComment).where(ShopComment.id == comment_id)
    comment = session.execute(stmt).scalar_one_or_none()

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to delete this comment")

    comment.is_active = False
    session.add(comment)
    session.commit()

    # Do'kon reitingini qayta hisoblash
    rating_stmt = select(
        func.coalesce(func.round(func.avg(ShopComment.rating)), 0)
    ).where(ShopComment.shop_id == comment.shop_id, ShopComment.is_active == True)

    avg_rating = session.execute(rating_stmt).scalar()

    shop_update_stmt = update(Shop).where(Shop.id == comment.shop_id).values(rating=avg_rating)
    session.execute(shop_update_stmt)
    session.commit()

    return {"message": "Comment deleted successfully"}


@router.patch("/rating/update")
async def shop_rating_update(session: db_dep):
    # Barcha do'konlar reitingini qayta hisoblash
    stmt = update(Shop).values(
        rating=select(
            func.coalesce(func.round(func.avg(ShopComment.rating)), 0)
        )
        .where(ShopComment.shop_id == Shop.id, ShopComment.is_active == True)
        .scalar_subquery()
    )
    session.execute(stmt)
    session.commit()

    return {"message": "Shop ratings updated successfully"}
