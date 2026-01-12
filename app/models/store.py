from sqlalchemy import String, Boolean, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Store(Base):
    __tablename__ = "stores"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)  # e.g. S001
    name: Mapped[str] = mapped_column(String(100))
    password_hash: Mapped[str] = mapped_column(String(255))
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Sales tax rate (example: NJ = 8.875% → 0.08875)
    tax_rate: Mapped[float] = mapped_column(Float, default=0.08875)
