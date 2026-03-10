import secrets

from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile
from sqlalchemy import select
from app.database import db_dep
from app.models import Shop, Image
from app.schemas import ShopCreateResponse, ShopCreateRequest, ShopUpdateRequest
from app.dependencies import current_user_jwt_dep
from app.config import settings
from app.celery import send_email_celery
from app.utils import redis_client

router = APIRouter(prefix="/shop", tags=["Shop"])


@router.post("/create")
async def shop_create(
    session: db_dep, current_user: current_user_jwt_dep, create_data: ShopCreateRequest
):
    shop = Shop(user_id=current_user.id, name=create_data.name)
    session.add(shop)
    session.commit()
    session.refresh(shop)

    token = secrets.token_hex(16)
    send_email_celery(
        current_user.email,
        "Email confiramtion",
        f"Your confirmation code is for shop {token}",
    )
    redis_client.setex(token, 120, shop.id)

    return "email user code"


@router.post("/verify/{secret_code}", response_model=ShopCreateResponse)
async def verify_shop(db: db_dep, secret_code: str, current_user: current_user_jwt_dep):

    shop_id = int(redis_client.get(secret_code))
    print(">>", shop_id)
    stmt = select(Shop).where(Shop.id == shop_id, Shop.user_id == current_user.id)
    shop = db.execute(stmt).scalars().first()
    shop.is_active = True
    db.commit()
    db.refresh(shop)

    return shop


@router.patch("/image/{shop_id}")
async def shop_update(
    shop_id: int, file: UploadFile, db: db_dep, current_user: current_user_jwt_dep
):

    stmt = select(Shop).where(Shop.user_id == current_user.id, Shop.id == shop_id)
    shop = db.execute(stmt).scalars().first()

    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")

    file_ext = Path(file.filename).suffix.lower()

    if file_ext not in [".jpg", ".png", ".jpeg"]:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    content = await file.read()

    if len(content) > 1024 * 1024:
        raise HTTPException(status_code=400, detail="Max size 1 mb")

    path = Path(settings.MEDIA_PATH)
    path.mkdir(exist_ok=True)

    import uuid

    filename = f"{uuid.uuid4()}{file_ext}"

    res = path / filename

    with open(res, "wb") as buffer:
        buffer.write(content)

    image = Image(url=f"{settings.MEDIA_PATH}/{filename}")

    db.add(image)
    db.flush()

    shop.image_id = image.id


@router.patch("/{shop_id}", response_model=ShopCreateResponse)
async def shop_update(
    shop_id: int,
    db: db_dep,
    update_data: ShopUpdateRequest,
    current_user: current_user_jwt_dep,
):

    stmt = select(Shop).where(Shop.user_id == current_user.id, Shop.id == shop_id)
    shop = db.execute(stmt).scalars().first()

    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")

    if update_data.description:
        shop.description = update_data.description

    if update_data.name:
        shop.name = update_data.name

    db.commit()
    db.refresh(shop)

    return shop


@router.get("/list", response_model=list[ShopCreateResponse])
async def shop_list(
    db: db_dep,
    current_user: current_user_jwt_dep,
    name: str | None = None,
    rating: float | None = None,
    limit: int = 20,
    offset: int = 0,
):
    stmt = select(Shop).where(Shop.user_id == current_user.id)
    if name:
        stmt = stmt.where(Shop.name.ilike(f"%{name}%"))

    if rating:
        stmt = stmt.where(Shop.rating >= rating)

    stmt = stmt.order_by(Shop.rating.desc())

    stmt = stmt.limit(limit).offset(offset)

    res = db.execute(stmt).scalars().all()

    return res
