from sqlalchemy import String, Integer, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class KioskConfig(Base):
    __tablename__ = "store_kiosk_config"

    store_id: Mapped[str] = mapped_column(String(20), ForeignKey("stores.id"), primary_key=True)

    theme_json: Mapped[str] = mapped_column(Text, default='{}')
    screensaver_json: Mapped[str] = mapped_column(Text, default='{}')

    idle_reset_seconds: Mapped[int] = mapped_column(Integer, default=45)
    product_grid_columns: Mapped[int] = mapped_column(Integer, default=4)
