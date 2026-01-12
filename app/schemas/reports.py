from pydantic import BaseModel

class DailyReportOut(BaseModel):
    date: str
    total_orders: int
    total_sales_cents: int
    by_category: list[dict]  # {category, qty, sales_cents}
