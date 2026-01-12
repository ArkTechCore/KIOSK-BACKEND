from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.admin_user import AdminUser

bearer = HTTPBearer()


def db():
    s = SessionLocal()
    try:
        yield s
    finally:
        s.close()


def require_admin_token(
    cred: HTTPAuthorizationCredentials = Depends(bearer),
    session: Session = Depends(db),
):
    token = cred.credentials
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid admin token")

    if payload.get("type") != "admin":
        raise HTTPException(status_code=401, detail="Not an admin token")

    admin_id = payload.get("admin_id")
    if not admin_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    admin = session.get(AdminUser, admin_id)
    if not admin or not admin.active:
        raise HTTPException(status_code=401, detail="Admin inactive")

    return {"admin_id": admin_id, "email": admin.email, "role": admin.role}
