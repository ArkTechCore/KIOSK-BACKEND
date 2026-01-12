from sqlalchemy import String, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.db.base import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    store_id: Mapped[str] = mapped_column(String(20), ForeignKey("stores.id"), index=True)

    order_number: Mapped[int] = mapped_column(Integer, index=True)
    barcode_value: Mapped[str] = mapped_column(String(80), unique=True, index=True)

    status: Mapped[str] = mapped_column(String(30), default="PLACED")
    payment_status: Mapped[str] = mapped_column(String(20), default="UNPAID")

    subtotal_cents: Mapped[int] = mapped_column(Integer, default=0)
    tax_cents: Mapped[int] = mapped_column(Integer, default=0)
    total_cents: Mapped[int] = mapped_column(Integer, default=0)

    paid_amount_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pos_txn_id: Mapped[str | None] = mapped_column(String(80), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class OrderLine(Base):
    __tablename__ = "order_lines"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    order_id: Mapped[str] = mapped_column(String(64), ForeignKey("orders.id"), index=True)

    product_id: Mapped[str] = mapped_column(String(64))
    product_name_snapshot: Mapped[str] = mapped_column(String(160))
    category_name_snapshot: Mapped[str] = mapped_column(String(120))

    qty: Mapped[int] = mapped_column(Integer, default=1)
    base_price_cents: Mapped[int] = mapped_column(Integer, default=0)
    line_total_cents: Mapped[int] = mapped_column(Integer, default=0)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)


class OrderLineMod(Base):
    __tablename__ = "order_line_mods"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    order_line_id: Mapped[str] = mapped_column(String(64), ForeignKey("order_lines.id"), index=True)

    group_title_snapshot: Mapped[str] = mapped_column(String(120))
    option_name_snapshot: Mapped[str] = mapped_column(String(120))
    delta_cents: Mapped[int] = mapped_column(Integer, default=0)
