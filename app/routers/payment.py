from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from app.database import db_dep
from app.schemas import PaymentCreate
from app.models import Payment, Order
from app.dependencies import current_user_jwt_dep


router = APIRouter(prefix="/payments", tags=["Payment"])


@router.post("/create")
async def create_payment(
    payload: PaymentCreate, db: db_dep, current_user: current_user_jwt_dep
):

    stmt = select(Order).where(
        Order.id == payload.order_id, Order.user_id == current_user.id
    )
    order = db.execute(stmt).scalars().first()

    if not order:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi!")

    new_payment = Payment(
        order_id=payload.order_id,
        payment_type=payload.payment_type,
        amount=order.user_cart.total_price,
        status="pending",
    )

    try:
        db.add(new_payment)
        db.commit()
        db.refresh(new_payment)

        return {
            "status": "success",
            "message": "To'lov muvaffaqiyatli yaratildi",
            "payment": {
                "id": new_payment.id,
                "amount": new_payment.amount,
                "status": new_payment.status,
            },
        }
    except Exception as e:
        db.rollback()  # Xatolik bo'lsa ortga qaytarish
        raise HTTPException(status_code=500, detail=f"Xatolik yuz berdi: {str(e)}")
