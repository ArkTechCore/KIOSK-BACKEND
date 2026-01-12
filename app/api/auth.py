from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import jwt
from datetime import datetime, timedelta

from app.core.config import settings
from app.api.deps import db
from app.models.store import Store
from app.schemas.auth import DeviceLoginIn, DeviceLoginOut
from app.utils.security import verify_password

router = APIRouter()


@router.post("/auth/device-login", response_model=DeviceLoginOut)
def device_login(payload: DeviceLoginIn, session: Session = Depends(db)):
    store = session.get(Store, payload.store_id)
    if not store or not store.active:
        raise HTTPException(status_code=401, detail="Invalid store")

    if not verify_password(payload.password, store.password_hash):
        raise HTTPException(status_code=401, detail="Invalid password")

    exp = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRES_MIN)
    token = jwt.encode(
        {
            "type": "device",
            "store_id": store.id,
            "role": payload.role,
            "device_id": payload.device_id,
            "exp": exp,
        },
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALG,
    )
    return DeviceLoginOut(token=token, store_id=store.id, role=payload.role)
