from pydantic import BaseModel


class ItemCartsIn(BaseModel):
    # user_cart_id: int
    item_id: int
    quantity: int | None = 0


class UserCartCreateResponset(BaseModel):
    id: int
    user_id: int
    item_carts: list[ItemCartsIn]
    total_price: int
