from sqlalchemy import String, Integer, Boolean, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Category(Base):
    __tablename__ = "categories"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    store_id: Mapped[str] = mapped_column(String(20), ForeignKey("stores.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    sort: Mapped[int] = mapped_column(Integer, default=0)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

class Product(Base):
    __tablename__ = "products"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    store_id: Mapped[str] = mapped_column(String(20), ForeignKey("stores.id"), index=True)
    category_id: Mapped[str] = mapped_column(String(64), ForeignKey("categories.id"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(Text, default="")
    price_cents: Mapped[int] = mapped_column(Integer, default=0)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

class ModifierGroup(Base):
    __tablename__ = "modifier_groups"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    store_id: Mapped[str] = mapped_column(String(20), ForeignKey("stores.id"), index=True)
    product_id: Mapped[str] = mapped_column(String(64), ForeignKey("products.id"), index=True)

    title: Mapped[str] = mapped_column(String(120))
    required: Mapped[bool] = mapped_column(Boolean, default=False)
    min_select: Mapped[int] = mapped_column(Integer, default=0)
    max_select: Mapped[int] = mapped_column(Integer, default=1)
    ui_type: Mapped[str] = mapped_column(String(20), default="radio")  # radio/chips
    active: Mapped[bool] = mapped_column(Boolean, default=True)

class ModifierOption(Base):
    __tablename__ = "modifier_options"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    store_id: Mapped[str] = mapped_column(String(20), ForeignKey("stores.id"), index=True)
    group_id: Mapped[str] = mapped_column(String(64), ForeignKey("modifier_groups.id"), index=True)

    name: Mapped[str] = mapped_column(String(120))
    delta_cents: Mapped[int] = mapped_column(Integer, default=0)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
