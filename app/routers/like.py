from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.database import db_dep
from app.dependencies import current_user_jwt_dep
from app.models import Like
from app.schemas import LikeCreateRequest, LikeCreateResponse

router = APIRouter(prefix="/like", tags=["Like"])


@router.post("/create", response_model=LikeCreateResponse)
async def like(
    session: db_dep, data: LikeCreateRequest, current_user: current_user_jwt_dep
):
    stmt = select(Like).where(
        Like.user_id == current_user.id, Like.item_id == data.item_id
    )

    existing = session.execute(stmt).scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=400, detail="Already liked")

    l = Like(user_id=current_user.id, item_id=data.item_id)

    session.add(l)
    session.commit()
    session.refresh(l)

    return l


@router.get("/list", response_model=list[LikeCreateResponse])
async def get_list(session: db_dep, current_user: current_user_jwt_dep):
    stmt = (
        select(Like)
        .where(Like.user_id == current_user.id)
        .order_by(Like.created_at.desc())
    )
    res = session.execute(stmt).scalars().all()

    return res


@router.delete("/{item_id}")
async def unlike(item_id: int, session: db_dep, current_user: current_user_jwt_dep):

    stmt = select(Like).where(Like.user_id == current_user.id, Like.item_id == item_id)

    like = session.execute(stmt).scalar_one_or_none()

    if not like:
        raise HTTPException(status_code=404, detail="Like not found")

    session.delete(like)
    session.commit()

    return {"message": "Like removed"}
