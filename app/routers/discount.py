from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.database import db_dep
from app.models import ItemDiscount, Item, Discount, Shop
from app.dependencies import current_user_jwt_dep
from app.schemas import DiscountCreateRequest, ItemDiscountCreateRequest

router = APIRouter(prefix="/discount", tags=["Discount"])


@router.post("/create")
async def discount_create(
    session: db_dep, data: DiscountCreateRequest, current_user: current_user_jwt_dep
):

    discount = Discount(name=data.name, percent=data.percent)

    session.add(discount)
    session.commit()
    session.refresh(discount)


@router.post("/item")
async def item_discount(
    session: db_dep, data: ItemDiscountCreateRequest, current_user: current_user_jwt_dep
):
    stmt = (
        select(Item)
        .join(Shop)
        .where(data.item_id == Item.id, Shop.user_id == current_user.id)
    )
    item = session.execute(stmt).scalars().first()
    stmt = select(Discount).where(Discount.id == data.discount_id)
    discount = session.execute(stmt).scalars().first()

    if not item:
        raise HTTPException(status_code=404, detail="user shop in item not found")

    if not discount:
        raise HTTPException(404, "discount not found")

    t = ItemDiscount(
        item_id=data.item_id,
        discount_id=data.discount_id,
        start_date=data.start_date,
        end_date=data.end_date,
    )

    session.add(t)
    session.commit()
    session.refresh(t)

    return t
