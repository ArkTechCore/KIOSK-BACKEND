from datetime import datetime
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.deps import db, require_device_token
from app.models.menu import Product, Category, ModifierGroup, ModifierOption
from app.models.orders import Order, OrderLine, OrderLineMod
from app.schemas.orders import CreateOrderIn, CreateOrderOut

router = APIRouter()

def _barcode(store_id: str, order_number: int) -> str:
    tail = uuid.uuid4().hex[:4].upper()
    return f"{store_id}-{order_number:06d}-{tail}"

@router.post("/stores/{store_id}/orders", response_model=CreateOrderOut)
def create_order(store_id: str, body: CreateOrderIn, session: Session = Depends(db), auth=Depends(require_device_token)):
    # next order number per store
    max_no = session.query(func.max(Order.order_number)).filter(Order.store_id == store_id).scalar() or 0
    order_number = int(max_no) + 1

    order_id = uuid.uuid4().hex
    barcode_value = _barcode(store_id, order_number)

    # load menu maps
    products = {p.id: p for p in session.query(Product).filter(Product.store_id==store_id).all()}
    categories = {c.id: c for c in session.query(Category).filter(Category.store_id==store_id).all()}

    groups = {g.id: g for g in session.query(ModifierGroup).filter(ModifierGroup.store_id==store_id).all()}
    options = {o.id: o for o in session.query(ModifierOption).filter(ModifierOption.store_id==store_id).all()}

    subtotal = 0
    line_rows = []
    mod_rows = []

    for ln in body.lines:
        p = products.get(ln.productId)
        if not p or not p.active:
            raise HTTPException(status_code=400, detail=f"Invalid product {ln.productId}")

        cat = categories.get(p.category_id)
        cat_name = cat.name if cat else "Unknown"

        base = p.price_cents

        # mods
        mods_total = 0
        for group_id, opt_ids in (ln.selected or {}).items():
            g = groups.get(group_id)
            if not g or g.product_id != p.id:
                continue
            for opt_id in opt_ids:
                o = options.get(opt_id)
                if not o or o.group_id != g.id:
                    continue
                mods_total += o.delta_cents

        unit = base + mods_total
        qty = max(1, int(ln.qty))
        line_total = unit * qty
        subtotal += line_total

        line_id = uuid.uuid4().hex
        line_rows.append(OrderLine(
            id=line_id,
            order_id=order_id,
            product_id=p.id,
            product_name_snapshot=p.name,
            category_name_snapshot=cat_name,
            qty=qty,
            base_price_cents=base,
            line_total_cents=line_total,
            note=(ln.note.strip() if ln.note else None),
        ))

        # store each selected mod as snapshot rows
        for group_id, opt_ids in (ln.selected or {}).items():
            g = groups.get(group_id)
            if not g or g.product_id != p.id:
                continue
            for opt_id in opt_ids:
                o = options.get(opt_id)
                if not o or o.group_id != g.id:
                    continue
                mod_rows.append(OrderLineMod(
                    id=uuid.uuid4().hex,
                    order_line_id=line_id,
                    group_title_snapshot=g.title,
                    option_name_snapshot=o.name,
                    delta_cents=o.delta_cents,
                ))

    # tax rate: later store setting; for now 8.875%
    tax = round(subtotal * 0.08875)
    total = subtotal + tax

    order = Order(
        id=order_id,
        store_id=store_id,
        order_number=order_number,
        barcode_value=barcode_value,
        status="PLACED",
        payment_status="UNPAID",
        subtotal_cents=subtotal,
        tax_cents=tax,
        total_cents=total,
        created_at=datetime.utcnow(),
    )

    session.add(order)
    for r in line_rows: session.add(r)
    for r in mod_rows: session.add(r)
    session.commit()

    return CreateOrderOut(
        order_id=order_id,
        order_number=order_number,
        barcode_value=barcode_value,
        totals={"subtotalCents": subtotal, "taxCents": tax, "totalCents": total},
    )

@router.get("/stores/{store_id}/orders")
def list_orders(store_id: str, status: str = "PLACED", session: Session = Depends(db), auth=Depends(require_device_token)):
    rows = session.query(Order).filter(Order.store_id==store_id, Order.status==status).order_by(Order.created_at.asc()).limit(200).all()
    return [{
        "order_id": o.id,
        "order_number": o.order_number,
        "barcode_value": o.barcode_value,
        "status": o.status,
        "payment_status": o.payment_status,
        "total_cents": o.total_cents,
        "created_at": o.created_at.isoformat(),
    } for o in rows]

@router.patch("/stores/{store_id}/orders/{order_id}")
def update_order(store_id: str, order_id: str, body: dict, session: Session = Depends(db), auth=Depends(require_device_token)):
    o = session.get(Order, order_id)
    if not o or o.store_id != store_id:
        raise HTTPException(status_code=404, detail="Not found")
    status = body.get("status")
    if status:
        o.status = status
    session.commit()
    return {"ok": True}
