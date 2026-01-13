from fastapi import FastAPI
from app.core.config import settings
from app.db.session import engine
from app.db.base import Base

# Import models so tables register
from app.models.store import Store
from app.models.admin_user import AdminUser
from app.models.config import KioskConfig
from app.models.catalog import CatalogCategory, CatalogProduct, CatalogModifierGroup, CatalogModifierOption
from app.models.overrides import StoreCategoryOverride, StoreProductOverride, StoreOptionOverride
from app.models.orders import Order, OrderLine, OrderLineMod
from fastapi.middleware.cors import CORSMiddleware

# Routers
from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.api.admin_auth import router as admin_auth_router
from app.api.admin_stores import router as admin_stores_router
from app.api.admin_catalog import router as admin_catalog_router
from app.api.admin_overrides import router as admin_overrides_router
from app.api.kiosk import router as kiosk_router
from app.api.orders import router as orders_router
from app.api.pos import router as pos_router
from app.api.reports import router as reports_router
from app.api.admin_reports import router as admin_reports_router

app = FastAPI(title=settings.APP_NAME)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


app.include_router(health_router, prefix="/api/v1", tags=["health"])
app.include_router(auth_router, prefix="/api/v1", tags=["device-auth"])

app.include_router(admin_auth_router, prefix="/api/v1", tags=["admin-auth"])
app.include_router(admin_stores_router, prefix="/api/v1", tags=["admin-stores"])
app.include_router(admin_catalog_router, prefix="/api/v1", tags=["admin-catalog"])
app.include_router(admin_overrides_router, prefix="/api/v1", tags=["admin-overrides"])
app.include_router(admin_reports_router, prefix="/api/v1", tags=["admin-reports"])

app.include_router(kiosk_router, prefix="/api/v1", tags=["kiosk"])
app.include_router(orders_router, prefix="/api/v1", tags=["orders"])
app.include_router(pos_router, prefix="/api/v1", tags=["pos"])
app.include_router(reports_router, prefix="/api/v1", tags=["reports"])

app.add_middleware(
    CORSMiddleware,
   allow_origins=[
  "http://localhost:3000",
  "https://kiosk-admin-axtb.onrender.com",
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from app.db.session import engine
from app.db.base import Base

Base.metadata.create_all(bind=engine)
