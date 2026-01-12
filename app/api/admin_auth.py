import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import jwt

from app.core.config import settings
from app.api.admin_deps import db
from app.models.admin_user import AdminUser
from app.utils.security import hash_password, verify_password
from app.schemas.admin_auth import AdminBootstrapIn, AdminLoginIn, AdminLoginOut

router = APIRouter()


@router.post("/admin/auth/bootstrap")
def bootstrap_admin(body: AdminBootstrapIn, session: Session = Depends(db)):
    if body.bootstrap_key != settings.ADMIN_BOOTSTRAP_KEY:
        raise HTTPException(status_code=403, detail="Invalid bootstrap key")

    existing = session.query(AdminUser).filter(AdminUser.email == body.email.lower()).first()
    if existing:
        return {"ok": True, "already_exists": True}

    admin = AdminUser(
        id=uuid.uuid4().hex,
        email=body.email.lower(),
        password_hash=hash_password(body.password),
        role="PLATFORM_ADMIN",
        active=True,
    )
    session.add(admin)
    session.commit()
    return {"ok": True}


@router.post("/admin/auth/login", response_model=AdminLoginOut)
def admin_login(body: AdminLoginIn, session: Session = Depends(db)):
    admin = session.query(AdminUser).filter(AdminUser.email == body.email.lower()).first()
    if not admin or not admin.active:
        raise HTTPException(status_code=401, detail="Invalid login")

    if not verify_password(body.password, admin.password_hash):
        raise HTTPException(status_code=401, detail="Invalid login")

    exp = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRES_MIN)
    token = jwt.encode(
        {"type": "admin", "admin_id": admin.id, "role": admin.role, "exp": exp},
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALG,
    )
    return AdminLoginOut(token=token, email=admin.email, role=admin.role)
