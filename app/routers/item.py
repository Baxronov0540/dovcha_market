from fastapi import APIRouter, HTTPException
from sqlalchemy import select


from app.database import db_dep
from app.models import Item
from app.schemas import current_user_jwt_dep, ItemCreateRequest, ItemCreateResponse


router = APIRouter(prefix="/item", tags=["Item"])


@router.post("/create", response_model=ItemCreateResponse)
async def item_create(
    session: db_dep, current_user: current_user_jwt_dep, create_data: ItemCreateRequest
):
    if (
        not current_user.is_active
        or not current_user.is_admin
        or not current_user.is_staff
    ):
        raise HTTPException(status_code=403, detail="sizda bunday huquq yuq!")

    item = Item(
        shop_id=create_data.shop_id,
        subcategory_id=create_data.subcategory_id,
        name=create_data.name,
        price=create_data.price,
        description=create_data.description,
        quantity=create_data.quantity,
    )

    session.add(item)
    session.commit()
    session.refresh(item)

    return item


@router.get("/list", response_model=list[ItemCreateResponse])
async def item_list(session: db_dep, current_user: current_user_jwt_dep):

    if not current_user.is_active:
        raise HTTPException(status_code=404, detail="User is not acitve ")

    stmt = select(Item)
    res = session.execute(stmt).scalars()

    return res

@router.get("/one",response_model=ItemCreateResponse)
async def item_one(session:db_dep,current_user:current_user_jwt_dep,item_id:int):
     

    if (
        not current_user.is_active
        or not current_user.is_admin
        or not current_user.is_staff
    ):
        raise HTTPException(status_code=403,detail="user is not active ")
    
    stmt=select(Item).where(Item.id==item_id)
    res=session.execute(stmt).scalars().first()
    if not res:
        raise HTTPException(status_code=404,detail="Item not found")
    
    return res


     