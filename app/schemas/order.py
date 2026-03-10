from pydantic import BaseModel


class OrderCreateRequest(BaseModel):
    promokod_id: int | None = None
    location_id: int
