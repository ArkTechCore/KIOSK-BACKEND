from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import db, require_device_token
from app.models.orders import Order
from app.schemas.pos import PosLookupOut, PosMarkPaidIn

router = APIRouter()


@router.get("/pos/lookup", response_model=PosLookupOut)
def pos_lookup(barcode: str, session: Session = Depends(db), auth=Depends(require_device_token)):
    o = session.query(Order).filter(Order.barcode_value == barcode).first()
    if not o:
        return PosLookupOut(found=False)

    return PosLookupOut(
        found=True,
        order_number=o.order_number,
        barcode_value=o.barcode_value,
        total_cents=o.total_cents,
        payment_status=o.payment_status,
        status=o.status,
    )


@router.post("/pos/mark-paid")
def pos_mark_paid(body: PosMarkPaidIn, session: Session = Depends(db), auth=Depends(require_device_token)):
    o = session.query(Order).filter(Order.barcode_value == body.barcode).first()
    if not o:
        raise HTTPException(status_code=404, detail="Not found")

    if o.payment_status == "PAID":
        return {"ok": True, "already_paid": True}

    o.payment_status = "PAID"
    o.paid_amount_cents = body.paid_amount_cents
    o.pos_txn_id = body.pos_txn_id
    o.paid_at = datetime.utcnow()
    session.commit()
    return {"ok": True}
