from sqlalchemy import String, Integer, Boolean, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class CatalogCategory(Base):
    __tablename__ = "catalog_categories"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    sort: Mapped[int] = mapped_column(Integer, default=0)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class CatalogProduct(Base):
    __tablename__ = "catalog_products"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    category_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("catalog_categories.id"),
        index=True,
    )

    name: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(Text, default="")
    base_price_cents: Mapped[int] = mapped_column(Integer, default=0)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class CatalogModifierGroup(Base):
    __tablename__ = "catalog_modifier_groups"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    product_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("catalog_products.id"),
        index=True,
    )

    title: Mapped[str] = mapped_column(String(120))
    required: Mapped[bool] = mapped_column(Boolean, default=False)
    min_select: Mapped[int] = mapped_column(Integer, default=0)
    max_select: Mapped[int] = mapped_column(Integer, default=1)
    ui_type: Mapped[str] = mapped_column(String(20), default="radio")  # radio/chips
    sort: Mapped[int] = mapped_column(Integer, default=0)  # <-- NEW
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class CatalogModifierOption(Base):
    __tablename__ = "catalog_modifier_options"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    group_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("catalog_modifier_groups.id"),
        index=True,
    )

    name: Mapped[str] = mapped_column(String(120))
    delta_cents: Mapped[int] = mapped_column(Integer, default=0)
    sort: Mapped[int] = mapped_column(Integer, default=0)  # <-- NEW
    active: Mapped[bool] = mapped_column(Boolean, default=True)
