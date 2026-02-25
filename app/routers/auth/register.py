import secrets

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from fastapi.responses import JSONResponse
from app.database import db_dep
from app.schemas import UserRegisterRequest, UserRegisterResponse
from app.models import User
from app.utils import password_hash, send_email, redis_client

router = APIRouter(prefix="/register", tags=["Auth"])


@router.post("/")
async def register_user(db: db_dep, create_data: UserRegisterRequest):
    stmt = select(User).where(User.email == create_data.email)
    user = db.execute(stmt).scalars().first()

    if user:
        raise HTTPException(status_code=400, detail="User  already exsist")
    user = User(
        email=create_data.email,
        password_hash=password_hash(create_data.password_hash),
        is_active=False,
    )

    secret_code = secrets.token_hex(16)
    send_email(
        create_data.email,
        "Email confiramtion",
        f"Your confirmation code is {secret_code}",
    )
    redis_client.setex(secret_code, 60, create_data.email)

    stmt = select(User)
    exsisting_user = db.execute(stmt).scalars().first()

    if not exsisting_user:
        user.is_active = True
        user.is_staff = True
        user.is_admin = True

    db.add(user)
    db.commit()

    return JSONResponse(
        status_code=201, content={"message": "Email confirmation sent to your email."}
    )


@router.post("/verify/{secret_code}/", response_model=UserRegisterResponse)
async def verify_register(db: db_dep, secret_code: str):
    email = redis_client.get(secret_code)
    print(email.decode("utf-8"))

    if not email:
        raise HTTPException(status_code=400, detail="Invalid code")

    stmt = select(User).where(User.email == email.decode("utf-8"))
    user = db.execute(stmt).scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = True
    db.commit()

    return JSONResponse(
        status_code=200, content={"message": "User registered successfully"}
    )
