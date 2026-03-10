from pydantic import BaseModel


class PaymentCreate(BaseModel):
    order_id: int
    payment_type: str
