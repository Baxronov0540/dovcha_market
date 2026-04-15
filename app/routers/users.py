from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from app.schemas import (
    UserProfilResponse,
    UserProfilUpdateRequest,
    ItemCartsIn,
    UserCartCreateResponset,
)
from app.dependencies import current_user_jwt_dep
from app.models import ItemCart, UserCart, Item,Order,OrderItem
from app.database import db_dep
from pathlib import Path
from fastapi import UploadFile
import uuid
from app.config import settings
from app.models import Image

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserProfilResponse)
async def user_profile(current_user: current_user_jwt_dep):
    return current_user


@router.get("/me/update/")
async def profile_update(
    session: db_dep,
    current_user: current_user_jwt_dep,
    update_data: UserProfilUpdateRequest,
):
    # Done: update profile

    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(current_user, key, value)
    session.commit()
    session.refresh(current_user)
    return current_user


@router.post("/avatar/upload/")
async def avatar_upload(
    file: UploadFile, session: db_dep, current_user: current_user_jwt_dep
):
    file_ext = Path(file.filename).suffix.lower()

    if file_ext not in [".jpg", ".png", ".jpeg"]:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    content = await file.read()
    if len(content) > 2 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Max size 2 mb")

    path = Path(settings.MEDIA_PATH)
    path.mkdir(exist_ok=True)

    filename = f"{uuid.uuid4()}{file_ext}"
    res = path / filename

    with open(res, "wb") as buffer:
        buffer.write(content)

    image = Image(url=f"{settings.MEDIA_PATH}/{filename}")
    session.add(image)
    session.flush()

    current_user.avatar_id = image.id
    session.commit()
    session.refresh(current_user)
    return current_user


@router.delete("/avatar/delete/")
async def avatar_delete(session: db_dep, current_user: current_user_jwt_dep):
    if not current_user.avatar_id:
        raise HTTPException(status_code=400, detail="User has no avatar")
    
    current_user.avatar_id = None
    session.commit()
    return {"message": "Avatar deleted"}


@router.post("/me/deactivate/")
async def deactivate_account(session: db_dep, current_user: current_user_jwt_dep):
    # TODO: deactivate account. Set is_deleted=True, change email to preserve unique=True
    current_user.is_active = False
    current_user.is_deleted = True

    session.commit()
    session.refresh(current_user)
    return current_user


@router.post("/cart/items")
async def cart_add(
    session: db_dep, current_user: current_user_jwt_dep, create_data: ItemCartsIn
):

    if create_data.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")

    stmt = select(Item).where(Item.id == create_data.item_id)
    item = session.execute(stmt).scalars().first()
    if item.quantity < create_data.quantity:
        raise HTTPException(status_code=400, detail="data.quantity > item.quantity")

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if item.quantity < create_data.quantity:
        raise HTTPException(status_code=400, detail="data.quantity > item.quantity")

    user_cart = current_user.user_cart

    stmt = select(ItemCart).where(
        ItemCart.user_cart_id == user_cart.id, ItemCart.item_id == create_data.item_id
    )
    existing_item = session.execute(stmt).scalars().first()

    if existing_item:
        existing_item.quantity += create_data.quantity
        item_cart = existing_item
    else:
        item_cart = ItemCart(
            user_cart_id=user_cart.id,
            item_id=create_data.item_id,
            quantity=create_data.quantity,
        )
        session.add(item_cart)
        session.flush()

    stmt = select(ItemCart).where(ItemCart.user_cart_id == user_cart.id)
    cart_items = session.execute(stmt).scalars().all()

    total = 0
    for cart_item in cart_items:
        stmt = select(Item).where(Item.id == cart_item.item_id)
        db_item = session.execute(stmt).scalars().first()
        total += db_item.price * cart_item.quantity
    print(">>", total)
    user_cart.total_price = total

    session.commit()
    session.refresh(item_cart)

    return item_cart


@router.get("cart/list", response_model=UserCartCreateResponset)
async def cart_list(db: db_dep, current_user: current_user_jwt_dep):
    stmt = select(UserCart).where(UserCart.user_id == current_user.id)
    res = db.execute(stmt).scalars().first()
    return res

@router.patch("/cart/clear")
async def cart_clear(current_user:current_user_jwt_dep,session:db_dep):
    
    stmt=select(UserCart).where