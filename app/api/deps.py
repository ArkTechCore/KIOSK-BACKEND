from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.store import Store
from app.models.admin_user import AdminUser

bearer = HTTPBearer()


def db():
    s = SessionLocal()
    try:
        yield s
    finally:
        s.close()


def require_device_token(
    cred: HTTPAuthorizationCredentials = Depends(bearer),
    session: Session = Depends(db),
):
    token = cred.credentials
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("type") != "device":
        raise HTTPException(status_code=401, detail="Not a device token")

    store_id = payload.get("store_id")
    role = payload.get("role")
    device_id = payload.get("device_id")
    if not store_id or not role or not device_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    store = session.get(Store, store_id)
    if not store or not store.active:
        raise HTTPException(status_code=401, detail="Store inactive")

    return {"store_id": store_id, "role": role, "device_id": device_id}


def require_admin_token(
    cred: HTTPAuthorizationCredentials = Depends(bearer),
    session: Session = Depends(db),
):
    token = cred.credentials
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("type") != "admin":
        raise HTTPException(status_code=401, detail="Not an admin token")

    admin_id = payload.get("admin_id")
    role = payload.get("role")
    if not admin_id or not role:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    # Enforce platform admin only for admin APIs
    if role != "PLATFORM_ADMIN":
        raise HTTPException(status_code=403, detail="Insufficient role")

    admin = session.get(AdminUser, admin_id)
    if not admin:
        raise HTTPException(status_code=401, detail="Admin not found")

    # If your AdminUser model has active/status fields, enforce them safely:
    if hasattr(admin, "active") and not getattr(admin, "active"):
        raise HTTPException(status_code=401, detail="Admin inactive")
    if hasattr(admin, "status") and getattr(admin, "status") not in (None, "ACTIVE"):
        raise HTTPException(status_code=401, detail="Admin inactive")

    return {"admin_id": admin_id, "role": role}
