import secrets
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from fastapi.responses import JSONResponse

from app.database import db_dep
from app.schemas import (
    UserLoginRequest,
    UserRegisterRequest,
    UserRegisterResponse,
    RefreshTokenRequest,
)
from app.models import User, TokenBlancList, UserCart
from app.utils import (
    verify_password,
    generate_jwt_tokens,
    password_hash,
    redis_client,
    decode_jwt_token,
)
from app.celery import send_email_celery
from app.dependencies import current_user_jwt_dep, credentials_dep

router = APIRouter(prefix="/auth", tags=["Auth"])

# TODO: merge into a single routers/auth.py file.


@router.post("/register")
async def register_user(db: db_dep, create_data: UserRegisterRequest):
    stmt = select(User).where(User.email == create_data.email)
    user = db.execute(stmt).scalars().first()

    if not user:
        user = User(
            email=create_data.email,
            password_hash=password_hash(create_data.password_hash),
            is_active=False,
        )
    if user.is_active:
        raise HTTPException(status_code=400, detail="User  already exsist")

    secret_code = secrets.token_hex(16)
    send_email_celery(
        create_data.email,
        "Email confiramtion",
        f"Your confirmation code is {secret_code}",
    )
    redis_client.setex(secret_code, 120, create_data.email)

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
    cart = UserCart(user_id=user.id)

    db.add(cart)
    db.commit()
    db.refresh(cart)
    return JSONResponse(
        status_code=200, content={"message": "User registered successfully"}
    )


@router.post("/login/")
async def login_user(db: db_dep, login_data: UserLoginRequest):
    stmt = select(User).where(User.email == login_data.email)
    user = db.execute(stmt).scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(user.password_hash, login_data.password_hash):
        raise HTTPException(status_code=401, detail="Invalid password")

    access_token, refresh_token = generate_jwt_tokens(user.id)
    t = TokenBlancList(token=access_token)
    db.add(t)
    db.commit()

    return {"access_token": access_token, "refresh_token": refresh_token}


@router.post("/refresh")
async def refresh_token(session: db_dep, data: RefreshTokenRequest):
    decoded_data = decode_jwt_token(data.refresh_token)

    user_id, exp = (
        decoded_data["user_id"],
        datetime.fromtimestamp(decoded_data["exp"], tz=timezone.utc),
    )

    if exp < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=401, detail="Refresh token expired.Please log in"
        )
    access_token = generate_jwt_tokens(user_id, True)

    return {"access_token": access_token}


@router.post("/logout/")
async def logout(
    current_user: current_user_jwt_dep, credentials: credentials_dep, db: db_dep
):
    # TODO: implement logout with token blacklisting
    token = credentials.credentials
    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    stmt = select(TokenBlancList).where(TokenBlancList.token == token)
    token = db.execute(stmt).scalars().first()
    db.delete(token)
    db.commit()


@router.post("/change/password/")
async def change_password(
    db: db_dep, current_user: current_user_jwt_dep, password: str
):

    if not current_user.is_active and not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    current_user.password_hash = password_hash(password)

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user
