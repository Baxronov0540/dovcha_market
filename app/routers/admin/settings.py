from starlette_admin.contrib.sqla import Admin


from app.database import engine
from app.models import (
    User,
    Shop,
    Image,
    Item,
    ItemDiscount,
    SubCategory,
    Category,
    Like,
    ItemCart,
    UserCart,
    Order,
    Payment,
    OrderItem,
    DeliveryPoint,
    Region,
    Comment,
    Promokod,
    Discount,
)
from app.routers.admin.view import *  # noqa
from app.routers.admin.auth import JSONAuthProvider

admin = Admin(
    engine=engine,
    title="Dovcha market",
    base_url="/admin",
    auth_provider=JSONAuthProvider(login_path="/login", logout_path="/logout"),
)


admin.add_view(UserAdmin(User, icon="fa fa-users"))
admin.add_view(ShopAdmin(Shop, icon="fa fa-shop"))
admin.add_view(ImageAdmin(Image, icon="fa fa-image"))
admin.add_view(ItemAdmin(Item, icon="fa fa-apple"))
admin.add_view(SubCategoryAdmin(SubCategory, icon="fa fa-tag"))
admin.add_view(CategoryAdmin(Category, icon="fa fa-pen"))
admin.add_view(LikeAdmin(Like, icon="fa fa-heart"))
admin.add_view(ItemCartAdmin(ItemCart, icon="fa fa-cart-plus"))
admin.add_view(UserCartAdmin(UserCart, icon="fa fa-shopping-basket"))
admin.add_view(OrderAdmin(Order, icon="fa fa-truck"))
admin.add_view(PaymentAdmin(Payment, icon="fa fa-vcard"))
admin.add_view(OrderItemAdmin(OrderItem, icon="fa fa-window-restore"))
admin.add_view(DeliveryPointAdmin(DeliveryPoint, icon="fa fa-map-marker"))
admin.add_view(RegionAdmin(Region, icon="fa fa-map-signs"))
admin.add_view(CommentAdmin(Comment, icon="fa fa-comments"))
admin.add_view(PromokodAdmin(Promokod, icon="fa fa-qrcode"))
admin.add_view(DiscountAdmin(Discount, icon="fa fa-percent"))
admin.add_view(ItemDiscountAdmin(ItemDiscount, icon="fa fa-pie-chart"))
