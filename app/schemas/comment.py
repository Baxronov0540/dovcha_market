from pydantic import BaseModel


class CommentCreateRequest(BaseModel):
    text: str | None = None

    rating: int | None = None


class CommentCreateResponse(BaseModel):
    user_id: int
    item_id: int
    text: str
    rating: int
