from datetime import datetime

from pydantic import BaseModel


class ItemCreateRequest(BaseModel):
    shop_id: int
    subcategory_id: int
    name: str
    description: str | None
    price: int
    quantity: int


class ItemCreateResponse(BaseModel):
    id: int
    shop_id: int
    subcategory_id: int
    name: str
    description: str | None
    price: int
    quantity: int
    rating: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ItemUpdateRequest(BaseModel):
    shop_id: int | None
    subcategory_id: int | None
    name: str | None
    description: str | None
    price: int | None
    quantity: int | None
    rating: int | None
    is_active: bool | None
