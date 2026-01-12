from fastapi import FastAPI
from app.core.config import settings

from app.db.session import engine
from app.db.base import Base

# IMPORTANT: import models so SQLAlchemy registers tables
from app.models.store import Store
from app.models.config import KioskConfig
from app.models.menu import Category, Product, ModifierGroup, ModifierOption
from app.models.orders import Order, OrderLine, OrderLineMod

from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.api.kiosk import router as kiosk_router
from app.api.orders import router as orders_router
from app.api.pos import router as pos_router
from app.api.reports import router as reports_router
from app.api.admin import router as admin_router

app = FastAPI(title=settings.APP_NAME)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

app.include_router(health_router, prefix="/api/v1", tags=["health"])
app.include_router(auth_router, prefix="/api/v1", tags=["auth"])
app.include_router(admin_router, prefix="/api/v1", tags=["admin"])
app.include_router(kiosk_router, prefix="/api/v1", tags=["kiosk"])
app.include_router(orders_router, prefix="/api/v1", tags=["orders"])
app.include_router(pos_router, prefix="/api/v1", tags=["pos"])
app.include_router(reports_router, prefix="/api/v1", tags=["reports"])
