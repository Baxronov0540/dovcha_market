from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.database import db_dep
from app.schemas import UserLoginRequest, UserProfilResponse, current_user_jwt_dep
from app.models import User
from app.utils import verify_password, generate_jwt_tokens

router = APIRouter(prefix="/login", tags=["Auth"])


@router.post("/")
async def login_user(db: db_dep, login_data: UserLoginRequest):
    stmt = select(User).where(User.email == login_data.email)
    user = db.execute(stmt).scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(user.password_hash, login_data.password_hash):
        raise HTTPException(status_code=401, detail="Invalid password")

    access_token, refresh_toekn = generate_jwt_tokens(user.id)

    return {"access_token": access_token, "refresh_token": refresh_toekn}


@router.post("/me", response_model=UserProfilResponse)
async def user_profil(current_user: current_user_jwt_dep):
    return current_user
