from fastapi import FastAPI
from app.core.config import settings
from app.api.health import router as health_router
from app.api.auth import router as auth_router

app = FastAPI(title=settings.APP_NAME)

app.include_router(health_router, prefix="/api/v1", tags=["health"])
app.include_router(auth_router, prefix="/api/v1", tags=["auth"])
