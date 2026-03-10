from datetime import datetime
from pydantic import BaseModel


class ShopCreateRequest(BaseModel):
    # image_id: int | None = None
    name: str
    # description: str | None = None


class ShopCreateResponse(BaseModel):
    id: int
    user_id: int
    image_id: int | None
    name: str
    description: str | None
    rating: int
    order_count: int
    created_at: datetime


class ShopUpdateRequest(BaseModel):
    # image_id: int | None = None
    name: str | None
    description: str | None = None
