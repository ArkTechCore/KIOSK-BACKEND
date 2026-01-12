from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

from app.db.session import SessionLocal
from app.core.config import settings
from app.models.store import Store
from app.schemas.auth import DeviceLoginIn, DeviceLoginOut

router = APIRouter()
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def db():
    s = SessionLocal()
    try:
        yield s
    finally:
        s.close()

@router.post("/auth/device-login", response_model=DeviceLoginOut)
def device_login(payload: DeviceLoginIn, session: Session = Depends(db)):
    store = session.get(Store, payload.store_id)
    if not store or not store.active:
        raise HTTPException(status_code=401, detail="Invalid store")

    if not pwd.verify(payload.password, store.password_hash):
        raise HTTPException(status_code=401, detail="Invalid password")

    exp = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRES_MIN)
    token = jwt.encode(
        {"store_id": store.id, "role": payload.role, "device_id": payload.device_id, "exp": exp},
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALG,
    )
    return DeviceLoginOut(token=token, store_id=store.id, role=payload.role)
