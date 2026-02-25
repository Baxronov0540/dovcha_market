from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password_hash: str


class UserLoginRequest(BaseModel):
    email: EmailStr
    password_hash: str


class UserRegisterResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime


class UserProfilResponse(BaseModel):
    id: int
    email: EmailStr
    first_name: str | None
    last_name: str | None
    is_active: bool
    is_staff: bool
    is_admin: bool
