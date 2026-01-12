from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime

from app.api.admin_deps import db, require_admin_token
from app.models.orders import Order
from app.models.store import Store
from app.schemas.reports import AdminDailyAllStoresOut

router = APIRouter()


@router.get("/admin/reports/daily", response_model=AdminDailyAllStoresOut)
def admin_daily_all_stores(date_str: str, session: Session = Depends(db), admin=Depends(require_admin_token)):
    d = date.fromisoformat(date_str)
    start = datetime(d.year, d.month, d.day, 0, 0, 0)
    end = datetime(d.year, d.month, d.day, 23, 59, 59)

    rows = session.query(
        Store.id,
        Store.name,
        func.coalesce(func.count(Order.id), 0),
        func.coalesce(func.sum(Order.total_cents), 0)
    ).outerjoin(
        Order,
        (Order.store_id == Store.id) &
        (Order.payment_status == "PAID") &
        (Order.paid_at >= start) &
        (Order.paid_at <= end)
    ).group_by(Store.id, Store.name).order_by(Store.id.asc()).all()

    stores = [{
        "store_id": r[0],
        "store_name": r[1],
        "total_orders": int(r[2]),
        "total_sales_cents": int(r[3] or 0)
    } for r in rows]

    return AdminDailyAllStoresOut(date=date_str, stores=stores)
