from pydantic import BaseModel


class LikeCreateRequest(BaseModel):
    item_id: int


class LikeCreateResponse(BaseModel):
    id: int
    user_id: int
    item_id: int
