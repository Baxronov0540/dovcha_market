from fastapi import FastAPI


from app.routers import auth_router,item_router

app = FastAPI(
    title="DOVCHA MARKET ", description="Dovcha Market Uzum marketning copy versiyasi"
)


app.include_router(auth_router)
app.include_router(item_router)
