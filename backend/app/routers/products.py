from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..database import get_session
from ..models import Product, ProductCreate, ProductRead
from ..deps import get_current_admin

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=List[ProductRead])
def list_products(session: Session = Depends(get_session)):
    return session.exec(select(Product)).all()


@router.post("/", response_model=ProductRead, dependencies=[Depends(get_current_admin)])
def create_product(payload: ProductCreate, session: Session = Depends(get_session)):
    prod = Product(**payload.dict())
    session.add(prod)
    session.commit()
    session.refresh(prod)
    return prod


@router.get("/{product_id}", response_model=ProductRead)
def get_product(product_id: int, session: Session = Depends(get_session)):
    prod = session.get(Product, product_id)
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    return prod
