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
    __tablename__="subcategories"

    id:Mapped[int]=mapped_column(BigInteger,primary_key=True)
    category_id:Mapped[int]=mapped_column(BigInteger,ForeignKey("categories.id",ondelete="SET NULL"))
    name:Mapped[str]=mapped_column(String(50))

    def __repr__(self):
        return f"SubCategory(id={self.id})"
    
class Category(Base):
    id:Mapped[int]=mapped_column(BigInteger,primary_key=True)
    name:Mapped[str]=mapped_column(String(100))

    def __repr__(self):
        return f"Category(id={self.id})"

class  ImageItem(Base):
    __tablename__="image_items"

    image_id:Mapped[int]=mapped_column(BigInteger,ForeignKey("images.id"),primary_key=True)
    item_id:Mapped[int]=mapped_column(BigInteger,ForeignKey("items.id"),primary_key=True)

    def __repr__(self):
        return f"ImageItem(item_id={self.item_id} , image_id={self.image_id})"

class Like(Base):
    __tablename__="likes"

    id:Mapped[int]=mapped_column(BigInteger,primary_key=True)
    user_id:Mapped[int]=mapped_column(BigInteger,ForeignKey("users.is",ondelete="CASCADE"))
    item_id:Mapped[int]=mapped_column(BigInteger,ForeignKey("items.id"))


    def __repr__(self):
        return f"Like(id={self.id})"

class ItemBucket(Base):
    __tablename__="item_buckets"

    id:Mapped[int]=mapped_column(BigInteger,primary_key=True)
    bucket_id:Mapped[int]=mapped_column(BigInteger,ForeignKey("buckets.id",ondelete="CASCADE")) 
    user_id:Mapped[int]=mapped_column(BigInteger,ForeignKey("users.id"))
    quantity:Mapped[int]=mapped_column(BigInteger,default=0) 

    def __repr__(self):
        return f"ItemBucekt(id={self.id})"

class Bucket(Base):
    __tablename__="buckets"

    id:Mapped[int]=mapped_column(BigInteger,primary_key=True)
    user_id:Mapped[int]=mapped_column(BigInteger,ForeignKey("users.id",ondelete="CASCADE"))
    total_price:Mapped[int]=mapped_column(BigInteger,default=0)


    def __repr__(self):
        return f"Bucket(id={self.id})"
    

class Order(Base):
    __tablename__="orders"

    id:Mapped[int]=mapped_column(BigInteger,primary_key=True)
    bucket_id:Mapped[int]=mapped_column(BigInteger,ForeignKey("orders.id",ondelete="SET NULL"))    
    item_id:Mapped[int]=mapped_column(BigInteger,ForeignKey("items.id"))
    promokod_id:Mapped[int]=mapped_column(BigInteger,ForeignKey("promokod.id",ondelete="SET NULL"),nullable=True)
    location_id:Mapped[int]=mapped_column(BigInteger,ForeignKey("Deliveries.id"))
    status:Mapped[str]=mapped_column(String(50),default="pending")
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=func.now())
    is_active:Mapped[bool]=mapped_column(Boolean,default=True)


    def __repr__(self):
        return f"Order(id={self.id})"


class Payment(Base):
    __tablename__="payments"

    id:Mapped[int]=mapped_column(BigInteger,primary_key=True)
    order_id:Mapped[int]=mapped_column(BigInteger,ForeignKey("orders.id",ondelete="SET NULL"))
    payment_type:Mapped[str]=mapped_column(String(50))
    amount:Mapped[int]=mapped_column(BigInteger)
    status:Mapped[str]=mapped_column(String(50),default="pending")
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=func.now())

    def __repr__(self):
        return f"Payment(id={self.id})"


class OrderItem(BaseModel):
    __tablename__="order_items"

    order_id:Mapped[int]=mapped_column(BigInteger,ForeignKey("orders.id"))
    item_id:Mapped[int]=mapped_column(BigInteger,ForeignKey("items.id",ondelete="SET NULL"))
    quantity:Mapped[int]=mapped_column(Integer)
    price_snapshot:Mapped[int]=mapped_column(BigInteger)

    def __repr__(self):
        return f"OrderItem(id={self.id})"
     
    

    #SDSD