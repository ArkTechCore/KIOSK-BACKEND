from pydantic import BaseModel


class DailyReportOut(BaseModel):
    date: str
    total_orders: int
    total_sales_cents: int
    by_category: list[dict]  # {category, qty, sales_cents}


class AdminDailyAllStoresOut(BaseModel):
    date: str
    stores: list[dict]  # {store_id, store_name, total_orders, total_sales_cents}
