from fastapi import APIRouter
from sqlalchemy import select, func
from pydantic import BaseModel

from app.database import db_dep
from app.models import Shop, Item, ShopComment, Comment

router = APIRouter(prefix="/api/statistics", tags=["Statistics"])


class RatingStatistics(BaseModel):
    average_rating: float
    total_comments: int
    rating_distribution: dict


@router.get("/shop/{shop_id}/rating", response_model=RatingStatistics)
async def get_shop_rating_stats(session: db_dep, shop_id: int):
    avg_rating_stmt = select(
        func.coalesce(func.round(func.avg(ShopComment.rating), 2), 0)
    ).where(ShopComment.shop_id == shop_id, ShopComment.is_active == True)

    avg_rating = session.execute(avg_rating_stmt).scalar()

    count_stmt = select(func.count(ShopComment.id)).where(
        ShopComment.shop_id == shop_id, ShopComment.is_active == True
    )

    total_comments = session.execute(count_stmt).scalar()

    # Reitinglarning taqsimotini hisoblash
    distribution = {}
    for rating in range(1, 6):
        rating_count_stmt = select(func.count(ShopComment.id)).where(
            ShopComment.shop_id == shop_id,
            ShopComment.rating == rating,
            ShopComment.is_active == True,
        )
        rating_count = session.execute(rating_count_stmt).scalar()
        if rating_count > 0:
            distribution[str(rating)] = rating_count

    return RatingStatistics(
        average_rating=avg_rating,
        total_comments=total_comments,
        rating_distribution=distribution,
    )


@router.get("/item/{item_id}/rating", response_model=RatingStatistics)
async def get_item_rating_stats(session: db_dep, item_id: int):
    avg_rating_stmt = select(
        func.coalesce(func.round(func.avg(Comment.rating), 2), 0)
    ).where(Comment.item_id == item_id, Comment.is_active == True)

    avg_rating = session.execute(avg_rating_stmt).scalar()

    count_stmt = select(func.count(Comment.id)).where(
        Comment.item_id == item_id, Comment.is_active == True
    )

    total_comments = session.execute(count_stmt).scalar()

    # Reitinglarning taqsimotini hisoblash
    distribution = {}
    for rating in range(1, 6):
        rating_count_stmt = select(func.count(Comment.id)).where(
            Comment.item_id == item_id,
            Comment.rating == rating,
            Comment.is_active == True,
        )
        rating_count = session.execute(rating_count_stmt).scalar()
        if rating_count > 0:
            distribution[str(rating)] = rating_count

    return RatingStatistics(
        average_rating=avg_rating,
        total_comments=total_comments,
        rating_distribution=distribution,
    )


@router.get("/top-shops")
async def get_top_shops(session: db_dep, limit: int = 10):
    stmt = (
        select(Shop.id, Shop.name, Shop.rating)
        .where(Shop.is_active == True)
        .order_by(Shop.rating.desc())
        .limit(limit)
    )

    shops = session.execute(stmt).fetchall()

    return [{"id": shop[0], "name": shop[1], "rating": shop[2]} for shop in shops]


@router.get("/top-items")
async def get_top_items(session: db_dep, limit: int = 10):
    stmt = (
        select(Item.id, Item.name, Item.rating)
        .where(Item.is_active == True)
        .order_by(Item.rating.desc())
        .limit(limit)
    )

    items = session.execute(stmt).fetchall()

    return [{"id": item[0], "name": item[1], "rating": item[2]} for item in items]
