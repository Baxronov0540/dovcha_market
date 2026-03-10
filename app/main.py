from fastapi import FastAPI

from app.routers.admin import admin
from app.routers import (
    auth_router,
    item_router,
    shop_router,
    user_router,
    order_router,
    payment_router,
    comment_router,
    location_router,
    discount_router,
)
from app.middleware import DBSessionMiddleware

app = FastAPI(
    title="DOVCHA MARKET ", description="Dovcha Market Uzum marketning copy versiyasi"
)


app.include_router(auth_router)
app.include_router(user_router)
app.include_router(shop_router)
app.include_router(item_router)
app.include_router(order_router)
app.include_router(payment_router)
app.include_router(comment_router)
app.include_router(location_router)
app.include_router(discount_router)
app.add_middleware(DBSessionMiddleware)


admin.mount_to(app=app)
