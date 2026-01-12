from sqlalchemy import String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class StoreCategoryOverride(Base):
    __tablename__ = "store_category_overrides"

    store_id: Mapped[str] = mapped_column(String(20), ForeignKey("stores.id"), primary_key=True)
    category_id: Mapped[str] = mapped_column(String(64), ForeignKey("catalog_categories.id"), primary_key=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_override: Mapped[int | None] = mapped_column(Integer, nullable=True)


class StoreProductOverride(Base):
    __tablename__ = "store_product_overrides"

    store_id: Mapped[str] = mapped_column(String(20), ForeignKey("stores.id"), primary_key=True)
    product_id: Mapped[str] = mapped_column(String(64), ForeignKey("catalog_products.id"), primary_key=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    price_cents_override: Mapped[int | None] = mapped_column(Integer, nullable=True)


class StoreOptionOverride(Base):
    __tablename__ = "store_option_overrides"

    store_id: Mapped[str] = mapped_column(String(20), ForeignKey("stores.id"), primary_key=True)
    option_id: Mapped[str] = mapped_column(String(64), ForeignKey("catalog_modifier_options.id"), primary_key=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    delta_cents_override: Mapped[int | None] = mapped_column(Integer, nullable=True)
