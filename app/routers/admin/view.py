import os
import uuid
import pathlib
from starlette_admin.contrib.sqla import ModelView
from starlette_admin import FileField
from fastapi import Request,UploadFile
from typing import Dict,Any
from app.models import Image
from app.utils import password_hash

UPLOAD_DIR="media_data"


def looks_hashed(p: str):
    return p.startswith("$argon2")

def extract_upload(v) -> UploadFile | None:
    if v is None:
        return None
    if isinstance(v, UploadFile):
        return v
    if isinstance(v, tuple):
        for item in v:
            if isinstance(item, UploadFile):
                return item
    return None

def _safe_ext(filename: str) -> str:
    _, ext = os.path.splitext(filename or "")
    return (ext.lower()[:10] if ext else "")
class UserAdmin(ModelView):
    identity = "user"
    fields = [
        "id",
        "email",
        "password_hash",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "is_admin",
        "is_deleted",
        "deleted_email",
        "created_at",
        "updated_at",
    ]
    exclude_fields_from_create = ["id", "created_at", "updated_at", "deleted_email"]
    exclude_fields_from_edit = ["id", "created_at", "updated_at"]
    exclude_fields_from_list = ["password_hash", "deleted_email"]

    async def before_edit(
        self, request: Request, data: Dict[str, Any], obj: Any
    ) -> None:
        if "password_hash" in data:
            pwd = data.get("password_hash")
            if not pwd:
                return  
            if not looks_hashed(pwd):
                obj.password_hash = password_hash(pwd)
    async def before_create(
        self, request: Request, data: Dict[str, Any], obj: Any
    ) -> None:
        pwd = data.get("password_hash")
        if pwd and not looks_hashed(pwd):
            obj.password_hash = password_hash(pwd)  # ASOSIY FIX
    


class ShopAdmin(ModelView):
    identity = "shop"
    fields = [
        "id",
        "user",
        FileField("img_file",label="image"),
        "name",
        "description",
        "rating",
        "order_count",
        "created_at",
        "updated_at",
    ]
    exclude_fields_from_create = [
        "id",
        "rating",
        "order_count",
        "created_at",
        "updated_at",
    ]
    exclude_fields_from_edit = ["id", "created_at", "updated_at"]
    async def before_create(
        self, request: Request, data: Dict[str, Any], obj: Any
    ) -> None:
        
        session = request.state.session
        
        up: UploadFile | None = extract_upload(data.get("img_file"))
        if up:
            os.makedirs(UPLOAD_DIR, exist_ok=True)

            filename = f"{uuid.uuid4().hex}{_safe_ext(up.filename)}"
            path = os.path.join(UPLOAD_DIR, filename)

            content = await up.read()
            with open(path, "wb") as f:
                f.write(content)

        
            url = f"/{UPLOAD_DIR}/{filename}"

            media = Image(url=url)
            session.add(media)
            session.flush([media])   # media.id olish uchun

            obj.avatar_id = media.id

        data.pop("img_file", None)


    async def before_edit(
        self, request: Request, data: Dict[str, Any], obj: Any
    ) -> None:

        session = request.state.session
        
        up: UploadFile | None = extract_upload(data.get("img_file"))
        if up:
            os.makedirs(UPLOAD_DIR, exist_ok=True)

            filename = f"{uuid.uuid4().hex}{_safe_ext(up.filename)}"
            path = os.path.join(UPLOAD_DIR, filename)

            content = await up.read()
            with open(path, "wb") as f:
                f.write(content)

            url = f"/static/uploads/{filename}"

            media = Image(url=url)
            session.add(media)
            session.flush([media])

            obj.avatar_id = media.id
    
        data.pop("img_file", None)


class ImageAdmin(ModelView):
    identity = "image"
    fields = ["id", "url"]
    exclude_fields_from_create = ["id"]
    exclude_fields_from_edit = ["id"]


class ItemAdmin(ModelView):
    identity = "item"
    fields = [
        "id",
        "shop",
        "subcategory",
        "name",
        "description",
        "price",
        "quantity",
        "rating",
        "is_active",
        "created_at",
        "updated_at",
    ]
    exclude_fields_from_create = ["id", "rating", "created_at", "updated_at"]
    exclude_fields_from_edit = ["id", "created_at", "updated_at"]
    # related_views = [SubCategoryAdmin]  # SubCategory uchun view


class CategoryAdmin(ModelView):
    identity = "category"
    fields = ["id", "name"]
    exclude_fields_from_create = ["id"]
    exclude_fields_from_edit = ["id"]


class SubCategoryAdmin(ModelView):
    identity = "sub-category"
    fields = ["id", "category", "name"]
    exclude_fields_from_create = ["id"]
    exclude_fields_from_edit = ["id"]


class OrderAdmin(ModelView):
    identity = "order"
    fields = [
        "id",
        "user_cart",
        "user",
        "promokod",
        "location",
        "status",
        "created_at",
        "is_active",
    ]
    exclude_fields_from_create = ["id", "created_at"]
    exclude_fields_from_edit = ["id", "created_at"]


class PaymentAdmin(ModelView):
    identity = "payment"
    fields = ["id", "order", "payment_type", "amount", "status", "created_at"]
    exclude_fields_from_create = ["id", "created_at"]
    exclude_fields_from_edit = ["id", "created_at"]


class DeliveryPointAdmin(ModelView):
    identity = "delivery-point"
    fields = [
        "id",
        "region",
        "district",
        "house",
        "postal_code",
        "latitude",
        "longitude",
        "phone",
        "working_hours",
        "is_active",
        "created_at",
        "updated_at",
    ]
    exclude_fields_from_create = ["id", "created_at", "updated_at"]
    exclude_fields_from_edit = ["id", "created_at", "updated_at"]


class RegionAdmin(ModelView):
    identity = "region"
    fields = ["id", "name"]
    exclude_fields_from_create = ["id"]
    exclude_fields_from_edit = ["id"]


class CommentAdmin(ModelView):
    identity = "comment"
    fields = ["id", "item", "user", "text", "is_active", "created_at", "updated_at"]
    exclude_fields_from_create = ["id", "created_at", "updated_at"]
    exclude_fields_from_edit = ["id", "created_at", "updated_at"]


class PromokodAdmin(ModelView):
    identity = "promokod"
    fields = [
        "id",
        "discount_type",
        "discount_value",
        "expires_at",
        "usage_limit",
        "usage_count",
        "created_at",
        "updated_at",
    ]
    exclude_fields_from_create = ["id", "usage_count", "created_at", "updated_at"]
    exclude_fields_from_edit = ["id", "created_at", "updated_at"]


class DiscountAdmin(ModelView):
    identity = "discount"
    fields = ["id", "name", "percent", "is_active"]
    exclude_fields_from_create = ["id"]
    exclude_fields_from_edit = ["id"]


class LikeAdmin(ModelView):
    identity = "like"
    fields = ["id", "user", "item"]
    exclude_fields_from_create = ["id"]
    exclude_fields_from_edit = ["id"]


class ItemCartAdmin(ModelView):
    identity = "item_cart"
    fields = ["id", "user_cart", "item", "quantity"]
    exclude_fields_from_create = ["id"]
    exclude_fields_from_edit = ["id"]


class UserCartAdmin(ModelView):
    identity = "user-cart"
    fields = ["id", "user", "total_price"]
    exclude_fields_from_create = ["id"]
    exclude_fields_from_edit = ["id"]


class OrderItemAdmin(ModelView):
    identity = "order_item"
    fields = ["id", "order", "item", "quantity", "price_snapshot"]
    exclude_fields_from_create = ["id"]
    exclude_fields_from_edit = ["id"]


class ItemDiscountAdmin(ModelView):
    identity = "item_discount"
    fields = ["id", "item", "discount", "start_date", "end_date"]
    exclude_fields_from_create = ["id"]
    exclude_fields_from_edit = ["id"]
