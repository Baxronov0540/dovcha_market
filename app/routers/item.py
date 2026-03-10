from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import joinedload


from app.database import db_dep
from app.models import Item, Shop
from app.schemas import ItemCreateRequest, ItemCreateResponse, ItemUpdateRequest
from app.dependencies import current_user_jwt_dep

router = APIRouter(prefix="/product", tags=["Product"])


@router.post("/create", response_model=ItemCreateResponse)
async def item_create(
    session: db_dep, current_user: current_user_jwt_dep, create_data: ItemCreateRequest
):
    # TODO: remove admin check. Users can also add
    # TODO: check if user has any shop. Link product to shop
    stmt = select(Shop).where(
        Shop.id == create_data.shop_id, Shop.user_id == current_user.id
    )
    shop = session.execute(stmt).scalars().first()
    if not shop:
        raise HTTPException(status_code=404, detail="User shop not found")
    item = Item(
        shop_id=create_data.shop_id,
        subcategory_id=create_data.subcategory_id,
        name=create_data.name,
        price=create_data.price,
        description=create_data.description,
        quantity=create_data.quantity,
    )

    session.add(item)
    session.commit()
    session.refresh(item)

    return item


from enum import Enum


class ItemOrderEnum(str, Enum):
    rating = "rating"
    price = "price"
    name = "name"
    category = "category"


class ItemOrderEnum(str, Enum):
    rating = "rating"
    price = "price"
    name = "name"


@router.get("/list", response_model=list[ItemCreateResponse])
async def product_list(
    session: db_dep,
    limit: int = 10,
    offset: int = 0,
    category_id: int | None = None,
    order_by: ItemOrderEnum = Query(default=ItemOrderEnum.rating),
):

    stmt = select(Item)

    if category_id:
        stmt = stmt.where(Item.subcategory_id == category_id)

    if order_by == ItemOrderEnum.price:
        stmt = stmt.order_by(Item.price)

    if order_by == ItemOrderEnum.rating:
        stmt = stmt.order_by(Item.rating.desc())

    if order_by == ItemOrderEnum.name:
        stmt = stmt.order_by(Item.name)

    stmt = stmt.where(Item.is_active == True)

    stmt = stmt.limit(limit).offset(offset)

    res = session.execute(stmt).scalars().all()

    return res


@router.get("/one/{item_id}/", response_model=ItemCreateResponse)
async def item_one(session: db_dep, item_id: int):
    # TODO: move item_id to path param
    # TODO: so only admins can see the item detail?
    # TODO: admin checks should be in dependency\

    stmt = select(Item).where(Item.id == item_id)
    res = session.execute(stmt).scalars().first()
    if not res:
        raise HTTPException(status_code=404, detail="Item not found")

    return res


@router.put("/update")
async def update_product(
    session: db_dep, current_user: current_user_jwt_dep, data: ItemUpdateRequest
):
    stmt = (
        select(Item)
        .options(joinedload(Item.shop))
        .where(Shop.user_id == current_user.id)
    )
    item = session.execute(stmt).scalars().first()
    update_data = data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(item, key, value)

    session.commit()
    session.refresh(item)

    return item
