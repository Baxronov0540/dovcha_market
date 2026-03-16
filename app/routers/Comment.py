from fastapi import APIRouter, HTTPException
from sqlalchemy import select, func, update
from sqlalchemy.orm import joinedload

from app.database import db_dep
from app.models import Comment, OrderItem, Order, Item
from app.dependencies import current_user_jwt_dep
from app.schemas import CommentCreateRequest, CommentCreateResponse

router = APIRouter(prefix="/comment", tags=["Comment"])


@router.post("/create/{item_id}", response_model=CommentCreateResponse)
async def comment_write(
    session: db_dep,
    current_user: current_user_jwt_dep,
    data: CommentCreateRequest,
    item_id: int,
):
    # Foydalanuvchining buyurtmalarini tekshirish
    stmt = (
        select(OrderItem)
        .options(joinedload(OrderItem.order))
        .where(Order.user_id == current_user.id, OrderItem.item_id == item_id)
    )

    res = session.execute(stmt).scalars().first()

    if not res:
        raise HTTPException(status_code=404, detail="user not order items")

    existing_comment_stmt = select(Comment).where(
        Comment.user_id == current_user.id, Comment.item_id == item_id
    )
    existing_comment = session.execute(existing_comment_stmt).scalar_one_or_none()

    if existing_comment:
        existing_comment.text = data.text
        existing_comment.rating = data.rating
        session.add(existing_comment)
    else:
        comment = Comment(
            item_id=item_id, user_id=current_user.id, text=data.text, rating=data.rating
        )
        session.add(comment)

    session.commit()

    # Mahsulot reitingini qayta hisoblash
    rating_stmt = select(
        func.coalesce(func.round(func.avg(Comment.rating)), 0)
    ).where(Comment.item_id == item_id, Comment.is_active == True)

    avg_rating = session.execute(rating_stmt).scalar()

    item_update_stmt = update(Item).where(Item.id == item_id).values(rating=avg_rating)
    session.execute(item_update_stmt)
    session.commit()

    session.refresh(existing_comment if existing_comment else comment)

    return existing_comment if existing_comment else comment


@router.get("/list/{item_id}", response_model=list[CommentCreateResponse])
async def review_list(session: db_dep, item_id: int, skip: int = 0, limit: int = 10):
    stmt = (
        select(Comment)
        .where(Comment.item_id == item_id, Comment.is_active == True)
        .order_by(Comment.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    res = session.execute(stmt).scalars().all()

    return res


@router.get("/{comment_id}", response_model=CommentCreateResponse)
async def comment_detail(session: db_dep, comment_id: int):
    stmt = select(Comment).where(Comment.id == comment_id)
    comment = session.execute(stmt).scalar_one_or_none()

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    return comment


@router.delete("/{comment_id}")
async def comment_delete(
    session: db_dep, current_user: current_user_jwt_dep, comment_id: int
):
    stmt = select(Comment).where(Comment.id == comment_id)
    comment = session.execute(stmt).scalar_one_or_none()

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to delete this comment")

    comment.is_active = False
    session.add(comment)
    session.commit()

    # Mahsulot reitingini qayta hisoblash
    rating_stmt = select(
        func.coalesce(func.round(func.avg(Comment.rating)), 0)
    ).where(Comment.item_id == comment.item_id, Comment.is_active == True)

    avg_rating = session.execute(rating_stmt).scalar()

    item_update_stmt = update(Item).where(Item.id == comment.item_id).values(rating=avg_rating)
    session.execute(item_update_stmt)
    session.commit()

    return {"message": "Comment deleted successfully"}


@router.patch("/rating/update")
async def product_rating_update(session: db_dep):
    # Barcha mahsulotlar reitingini qayta hisoblash
    stmt = update(Item).values(
        rating=select(
            func.coalesce(func.round(func.avg(Comment.rating)), 0)
        )
        .where(Comment.item_id == Item.id, Comment.is_active == True)
        .scalar_subquery()
    )
    session.execute(stmt)

    session.commit()
    
    return {"message": "Product ratings updated successfully"}
