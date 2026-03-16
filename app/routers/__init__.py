from .auth import router as auth_router
from .item import router as item_router
from .shop import router as shop_router

from .users import router as user_router

from .order import router as order_router

from .payment import router as payment_router
from .Comment import router as comment_router
from .shop_comment import router as shop_comment_router
from .location import router as location_router
from .discount import router as discount_router
from .statistics import router as statistics_router


__all__ = [
    "auth_router",
    "item_router",
    "shop_router",
    "order_router",
    "user_router",
    "payment_router",
    "comment_router",
    "shop_comment_router",
    "location_router",
    "discount_router",
    "statistics_router",
]
