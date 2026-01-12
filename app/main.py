from fastapi import FastAPI
from app.core.config import settings
from app.api.health import router as health_router
from app.api.auth import router as auth_router

app = FastAPI(title=settings.APP_NAME)

app.include_router(health_router, prefix="/api/v1", tags=["health"])
app.include_router(auth_router, prefix="/api/v1", tags=["auth"])
from app.db.session import engine
from app.db.base import Base
from app.models.store import Store  # make sure models are imported so tables register

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
