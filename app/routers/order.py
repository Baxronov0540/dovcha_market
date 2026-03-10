from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.database import db_dep
from app.dependencies import current_user_jwt_dep
from app.schemas import OrderCreateRequest
from app.models import Order, OrderItem


router = APIRouter(prefix="/order", tags=["Order"])


@router.post("/create/")
async def order_create(
    db: db_dep, current_user: current_user_jwt_dep, order_data: OrderCreateRequest
):
    if not current_user.user_cart.item_carts:
        raise HTTPException(status_code=400, detail="Cart None")
    order = Order(
        user_card_id=current_user.user_cart.id,
        user_id=current_user.id,
        promokod_id=order_data.promokod_id,
        location_id=order_data.location_id,
    )
    db.add(order)
    db.flush()

    item_carts = current_user.user_cart.item_carts
    for item_cart in item_carts:
        item_cart.item.quantity -= item_cart.quantity
        or_item = OrderItem(
            order_id=order.id,
            item_id=item_cart.item_id,
            quantity=item_cart.quantity,
            price_snapshot=item_cart.item.price,
        )
        db.add(or_item)

    for item_cart in item_carts:
        db.delete(item_cart)

    db.commit()
    db.refresh(order)

    return order


@router.get("/list")
async def list_order(session: db_dep, current_user: current_user_jwt_dep):
    stmt = (
        select(Order).where(Order.user_id == current_user.id).order_by(Order.created_at)
    )
    res = session.execute(stmt).scalars().all()

    return res
