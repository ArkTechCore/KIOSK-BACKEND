from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime

from app.api.deps import db, require_device_token
from app.models.orders import Order, OrderLine
from app.schemas.reports import DailyReportOut

router = APIRouter()


@router.get("/stores/{store_id}/reports/daily", response_model=DailyReportOut)
def daily_report(store_id: str, date_str: str, session: Session = Depends(db), auth=Depends(require_device_token)):
    d = date.fromisoformat(date_str)
    start = datetime(d.year, d.month, d.day, 0, 0, 0)
    end = datetime(d.year, d.month, d.day, 23, 59, 59)

    paid_orders = session.query(Order.id).filter(
        Order.store_id == store_id,
        Order.payment_status == "PAID",
        Order.paid_at >= start,
        Order.paid_at <= end,
    ).subquery()

    total_orders = session.query(func.count()).select_from(paid_orders).scalar() or 0

    total_sales = session.query(func.coalesce(func.sum(Order.total_cents), 0)).filter(
        Order.store_id == store_id,
        Order.payment_status == "PAID",
        Order.paid_at >= start,
        Order.paid_at <= end
    ).scalar() or 0

    rows = session.query(
        OrderLine.category_name_snapshot,
        func.coalesce(func.sum(OrderLine.qty), 0),
        func.coalesce(func.sum(OrderLine.line_total_cents), 0),
    ).join(paid_orders, OrderLine.order_id == paid_orders.c.id).group_by(OrderLine.category_name_snapshot).all()

    by_cat = [{"category": r[0], "qty": int(r[1]), "sales_cents": int(r[2])} for r in rows]

    return DailyReportOut(
        date=date_str,
        total_orders=int(total_orders),
        total_sales_cents=int(total_sales),
        by_category=by_cat
    )
