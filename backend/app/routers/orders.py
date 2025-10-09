from typing import List
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from ..database import get_session
from ..models import Order, OrderItem, OrderCreate, OrderRead

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=OrderRead)
def create_order(payload: OrderCreate, session: Session = Depends(get_session)):
    order = Order(
        customer_name=payload.customer_name,
        customer_phone=payload.customer_phone,
        status="new",
    )
    session.add(order)
    session.flush()
    for it in payload.items:
        session.add(
            OrderItem(
                order_id=order.id,
                product_id=it.product_id,
                quantity=it.quantity,
                unit_price=it.unit_price,
            )
        )
    session.commit()
    session.refresh(order)
    return order


@router.get("/", response_model=List[OrderRead])
def list_orders(session: Session = Depends(get_session)):
    return session.exec(select(Order)).all()
