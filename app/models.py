from datetime import datetime

from sqlalchemy import (
    String,
    BigInteger,
    Integer,
    Boolean,
    DateTime,
    func,
    ForeignKey,
    Text,
    Numeric,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class BaseModel(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )


class User(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(80), unique=True)
    password_hash: Mapped[str] = mapped_column(String(100))
    first_name: Mapped[str] = mapped_column(String(50), nullable=True)
    last_name: Mapped[str] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_staff: Mapped[bool] = mapped_column(Boolean, default=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self):
        return f"User(id={self.id})"


class Shop(BaseModel):
    __tablename__ = "shops"

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE")
    )
    image_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("images.id", ondelete="SET NULL")
    )
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text, nullable=True)
    rating: Mapped[int] = mapped_column(Integer, default=0)
    order_count: Mapped[int] = mapped_column(BigInteger, default=0)

    def __repr__(self):
        return f"Shop(id={self.id})"


class Image(Base):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    url: Mapped[str] = mapped_column(String(100))

    def __repr__(self):
        return f"IMAGE(id={self.id})"


class Item(BaseModel):
    __tablename__ = "items"

    shop_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("shops.id", ondelete="CASCADE")
    )
    subcategory_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("subcategories.id", ondelete="CASCADE")
    )
    discount_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("discounts.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(Text, nullable=True)
    price: Mapped[int] = mapped_column(BigInteger)
    quantity: mapped_column[int] = mapped_column(BigInteger)
    rating: Mapped[int] = mapped_column(Integer, default=0)
    old_price: Mapped[int] = mapped_column(BigInteger, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self):
        return f"Item(id={self.id})"


class SubCategory(Base):
    __tablename__ = "subcategories"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    category_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("categories.id", ondelete="SET NULL")
    )
    name: Mapped[str] = mapped_column(String(50))

    def __repr__(self):
        return f"SubCategory(id={self.id})"


class Category(Base):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    def __repr__(self):
        return f"Category(id={self.id})"


class ImageItem(Base):
    __tablename__ = "image_items"

    image_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("images.id"), primary_key=True
    )
    item_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("items.id"), primary_key=True
    )

    def __repr__(self):
        return f"ImageItem(item_id={self.item_id} , image_id={self.image_id})"


class Like(Base):
    __tablename__ = "likes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.is", ondelete="CASCADE")
    )
    item_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("items.id"))

    def __repr__(self):
        return f"Like(id={self.id})"


class ItemBucket(Base):
    __tablename__ = "item_buckets"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    bucket_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("buckets.id", ondelete="CASCADE")
    )
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    quantity: Mapped[int] = mapped_column(BigInteger, default=0)

    def __repr__(self):
        return f"ItemBucekt(id={self.id})"


class Bucket(Base):
    __tablename__ = "buckets"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE")
    )
    total_price: Mapped[int] = mapped_column(BigInteger, default=0)

    def __repr__(self):
        return f"Bucket(id={self.id})"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    bucket_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("orders.id", ondelete="SET NULL")
    )
    item_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("items.id"))
    promokod_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("promokods.id", ondelete="SET NULL"), nullable=True
    )
    location_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("Deliveries.id"))
    status: Mapped[str] = mapped_column(String(50), default="pending")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self):
        return f"Order(id={self.id})"


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    order_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("orders.id", ondelete="SET NULL")
    )
    payment_type: Mapped[str] = mapped_column(String(50))
    amount: Mapped[int] = mapped_column(BigInteger)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )

    def __repr__(self):
        return f"Payment(id={self.id})"


class OrderItem(BaseModel):
    __tablename__ = "order_items"

    order_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("orders.id"))
    item_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("items.id", ondelete="SET NULL")
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer)
    price_snapshot: Mapped[int] = mapped_column(BigInteger)

    def __repr__(self):
        return f"OrderItem(id={self.id})"


class DeliveryPoint(BaseModel):
    __tablename__ = "delivery_points"

    country: Mapped[str] = mapped_column(String(100), nullable=False)
    region: Mapped[str] = mapped_column(String(100), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    district: Mapped[str] = mapped_column(String(100), nullable=False)

    house: Mapped[str] = mapped_column(String(50), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(20), nullable=False)

    latitude: Mapped[float] = mapped_column(Numeric(9, 6), nullable=False)
    longitude: Mapped[float] = mapped_column(Numeric(9, 6), nullable=False)

    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    working_hours: Mapped[str] = mapped_column(String(100), nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self) -> str:
        return f"<DeliveryPoint id={self.id} name={self.name}>"


class Comment(BaseModel):
    __tablename__ = "comments"

    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    description: Mapped[str] = mapped_column(Text, nullable=False)
    advantages: Mapped[str] = mapped_column(Text)
    disadvantages: Mapped[str] = mapped_column(Text)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self) -> str:
        return f"Comment(id={self.id!r}, user_id={self.user_id!r})"


class Promokod(BaseModel):
    __tablename__ = "promokods"

    discount_type: Mapped[str] = mapped_column(String(50), nullable=False)

    discount_value: Mapped[int] = mapped_column(BigInteger, nullable=False)

    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    usage_limit: Mapped[int] = mapped_column(Integer, default=1)

    def __repr__(self) -> str:
        return f"Promokod(id={self.id}, type='{self.discount_type}')"


class Discount(Base):
    __tablename__ = "discounts"

    id: Mapped[int] = mapped_column(primary_key=True)

    shop_id: Mapped[int] = mapped_column(ForeignKey("shops.id"))

    name: Mapped[str] = mapped_column(String(255))
    percent: Mapped[int] = mapped_column(BigInteger)

    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self) -> str:
        return f"<Discount(name='{self.name}', percent={self.percent})>"


class Size(Base):
    __tablename__ = "sizes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    size: Mapped[str] = mapped_column(String(20))


class ItemSize(Base):
    __tablename__ = "item_sizes"

    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), primary_key=True)
    size_id: Mapped[int] = mapped_column(ForeignKey("size.id"), primary_key=True)
