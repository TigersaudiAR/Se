from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..db.session import get_session
from ..dependencies.auth import get_current_user, get_current_admin
from ..models import Product, User
from ..schemas import ProductCreate, ProductRead, ProductUpdate
from ..services import audit, zid

router = APIRouter(prefix="/api/v1/products", tags=["products"])

DEFAULT_DENOMS = ["2$", "5$", "10$", "25$", "50$", "100$"]


@router.get("", response_model=list[ProductRead])
async def list_products(
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
) -> list[Product]:
    result = await session.exec(select(Product).order_by(Product.created_at.desc()))
    return result.all()


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(
    payload: ProductCreate,
    auto_categories: bool = Query(default=False, description="تفعيل الفئات الافتراضية"),
    push_to_zid: bool = Query(default=True),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_admin),
) -> Product:
    product = Product(**payload.model_dump())
    if auto_categories and not product.categories:
        product.categories = DEFAULT_DENOMS.copy()
    session.add(product)
    await session.commit()
    await session.refresh(product)

    zid_id: str | None = None
    if push_to_zid:
        zid_id = await zid.create_product(session, product)
        if zid_id:
            product.zid_product_id = zid_id
            product.last_synced_at = datetime.utcnow()
            await session.commit()
            await session.refresh(product)

    await audit.log_action(
        session,
        action="products.create",
        user_id=current_user.id,
        details={"product_id": product.id, "zid_id": zid_id},
    )
    return product


@router.put("/{product_id}", response_model=ProductRead)
async def update_product(
    product_id: int,
    payload: ProductUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_admin),
) -> Product:
    result = await session.exec(select(Product).where(Product.id == product_id))
    product = result.one_or_none()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="المنتج غير موجود")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    product.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(product)
    await audit.log_action(
        session,
        action="products.update",
        user_id=current_user.id,
        details={"product_id": product.id},
    )
    return product


@router.post("/{product_id}/push", response_model=ProductRead)
async def push_product(
    product_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_admin),
) -> Product:
    result = await session.exec(select(Product).where(Product.id == product_id))
    product = result.one_or_none()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="المنتج غير موجود")
    success = await zid.update_product(session, product)
    if not success:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="تعذر التزامن مع زد")
    await audit.log_action(
        session,
        action="products.push",
        user_id=current_user.id,
        details={"product_id": product.id},
    )
    return product
