from datetime import datetime, timezone
from enum import Enum

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.database import db_dep
from app.models import Item, Shop, ItemDiscount, Discount
from app.schemas import ItemCreateRequest, ItemCreateResponse, ItemUpdateRequest
from app.dependencies import current_user_jwt_dep

router = APIRouter(prefix="/product", tags=["Product"])


def _compute_discounted_price(item: Item) -> int | None:
    """Itemga tegishli faol chegirmani topib, chegirma narxini qaytaradi."""
    now = datetime.now(timezone.utc)
    for item_discount in item.item_discounts:
        discount: Discount = item_discount.discount
        if not discount.is_active:
            continue
        start = item_discount.start_date
        end = item_discount.end_date
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        if end.tzinfo is None:
            end = end.replace(tzinfo=timezone.utc)
        if start <= now <= end:
            # chegirma narxi = narx * (1 - percent/100)
            return int(item.price * (100 - discount.percent) / 100)
    return None


def _as_response(item: Item) -> ItemCreateResponse:
    """Item ORM obyektini pydantic response schemaga o'giradi."""
    return ItemCreateResponse(
        id=item.id,
        shop_id=item.shop_id,
        subcategory_id=item.subcategory_id,
        name=item.name,
        description=item.description,
        price=item.price,
        discounted_price=_compute_discounted_price(item),
        quantity=item.quantity,
        rating=item.rating,
        is_active=item.is_active,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


class ItemOrderEnum(str, Enum):
    rating = "rating"
    price = "price"
    item_name = "name"


@router.post("/create", response_model=ItemCreateResponse)
async def item_create(
    session: db_dep, current_user: current_user_jwt_dep, create_data: ItemCreateRequest
):
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
    return _as_response(item)


@router.get("/list", response_model=list[ItemCreateResponse])
async def product_list(
    session: db_dep,
    limit: int = 10,
    offset: int = 0,
    category_id: int | None = None,
    order_by: ItemOrderEnum = Query(default=ItemOrderEnum.rating),
):
    stmt = (
        select(Item)
        .options(joinedload(Item.item_discounts).joinedload(ItemDiscount.discount))
        .where(Item.is_active == True)
    )

    if category_id:
        stmt = stmt.where(Item.subcategory_id == category_id)

    if order_by == ItemOrderEnum.price:
        stmt = stmt.order_by(Item.price)
    elif order_by == ItemOrderEnum.rating:
        stmt = stmt.order_by(Item.rating.desc())
    elif order_by == ItemOrderEnum.item_name:
        stmt = stmt.order_by(Item.name)

    stmt = stmt.limit(limit).offset(offset)

    items = session.execute(stmt).unique().scalars().all()
    return [_as_response(item) for item in items]


@router.get("/one/{item_id}", response_model=ItemCreateResponse)
async def item_one(session: db_dep, item_id: int):
    stmt = (
        select(Item)
        .options(joinedload(Item.item_discounts).joinedload(ItemDiscount.discount))
        .where(Item.id == item_id)
    )
    item = session.execute(stmt).unique().scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return _as_response(item)


@router.put("/update/{item_id}", response_model=ItemCreateResponse)
async def update_product(
    item_id: int,
    session: db_dep,
    current_user: current_user_jwt_dep,
    data: ItemUpdateRequest,
):
    stmt = (
        select(Item)
        .options(joinedload(Item.shop))
        .where(Item.id == item_id, Shop.user_id == current_user.id)
        .join(Shop, Item.shop_id == Shop.id)
    )
    item = session.execute(stmt).unique().scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found or not your shop")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)

    session.commit()
    session.refresh(item)
    return _as_response(item)
