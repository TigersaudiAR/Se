from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..db.session import get_session
from ..dependencies.auth import get_current_user, get_current_admin
from ..models import Product, User, Voucher
from ..schemas import VoucherImport, VoucherRead
from ..services import audit, zid

router = APIRouter(prefix="/api/v1/vouchers", tags=["vouchers"])


@router.get("", response_model=list[VoucherRead])
async def list_vouchers(
    product_id: int | None = None,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
) -> list[Voucher]:
    query = select(Voucher)
    if product_id:
        query = query.where(Voucher.product_id == product_id)
    result = await session.exec(query)
    return result.all()


@router.post("/import", status_code=status.HTTP_201_CREATED)
async def import_vouchers(
    payload: VoucherImport,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_admin),
) -> dict[str, int]:
    result = await session.exec(select(Product).where(Product.id == payload.product_id))
    product = result.one_or_none()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="المنتج غير موجود")
    created = 0
    vouchers: list[Voucher] = []
    for code in payload.codes:
        voucher = Voucher(product_id=payload.product_id, code=code, notes=payload.notes)
        session.add(voucher)
        vouchers.append(voucher)
        created += 1
    await session.commit()
    for voucher in vouchers:
        await session.refresh(voucher)

    if payload.also_push_to_zid and product.zid_product_id:
        await zid.import_vouchers(session, product=product, codes=[v.code for v in vouchers])

    await audit.log_action(
        session,
        action="vouchers.import",
        user_id=current_user.id,
        details={"product_id": product.id, "count": created},
    )
    return {"imported": created}
