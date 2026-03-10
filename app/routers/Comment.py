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
    stmt = (
        select(OrderItem)
        .options(joinedload(OrderItem.order))
        .where(Order.user_id == current_user.id, OrderItem.item_id == item_id)
    )

    res = session.execute(stmt).scalars().first()

    if not res:
        raise HTTPException(status_code=404, detail="user not order items")

    comment = Comment(
        item_id=item_id, user_id=current_user.id, text=data.text, rating=data.rating
    )

    session.add(comment)
    session.commit()
    session.refresh(comment)

    return comment


@router.get("/list/{item_id}", response_model=list[CommentCreateResponse])
async def review_list(session: db_dep, item_id: int):
    stmt = (
        select(Comment)
        .where(Comment.item_id == item_id, Comment.is_active == True)
        .order_by(Comment.created_at.desc())
    )
    res = session.execute(stmt).scalars().all()

    return res


@router.patch("/rating/update")
async def product_rating_update(session: db_dep):

    stmt = update(Item).values(
        rating=select(
            func.coalesce(func.sum(Comment.rating) / func.count(Comment.rating), 0)
        )
        .where(Comment.item_id == Item.id)
        .scalar_subquery()
    )
    session.execute(stmt)

    session.commit()
