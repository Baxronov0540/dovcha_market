from datetime import datetime
from pydantic import BaseModel


class DiscountCreateRequest(BaseModel):
    name: str
    percent: int


class ItemDiscountCreateRequest(BaseModel):
    item_id: int
    discount_id: int
    start_date: datetime
    end_date: datetime
