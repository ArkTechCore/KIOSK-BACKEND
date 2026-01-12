from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.admin_deps import db, require_admin_token
from app.models.store import Store
from app.schemas.admin_store import AdminCreateStoreIn, AdminStoreOut
from app.utils.security import hash_password

router = APIRouter()


@router.get("/admin/stores", response_model=list[AdminStoreOut])
def list_stores(session: Session = Depends(db), admin=Depends(require_admin_token)):
    rows = session.query(Store).order_by(Store.id.asc()).all()
    return [AdminStoreOut(store_id=s.id, name=s.name, active=s.active) for s in rows]


@router.post("/admin/stores", response_model=AdminStoreOut)
def create_store(body: AdminCreateStoreIn, session: Session = Depends(db), admin=Depends(require_admin_token)):
    if session.get(Store, body.store_id):
        raise HTTPException(status_code=400, detail="Store already exists")

    s = Store(
        id=body.store_id,
        name=body.name,
        password_hash=hash_password(body.password),
        active=True,
    )
    session.add(s)
    session.commit()
    return AdminStoreOut(store_id=s.id, name=s.name, active=s.active)


@router.post("/admin/stores/{store_id}/reset-password")
def reset_store_password(store_id: str, body: dict, session: Session = Depends(db), admin=Depends(require_admin_token)):
    new_pass = body.get("password")
    if not new_pass:
        raise HTTPException(status_code=400, detail="password required")

    s = session.get(Store, store_id)
    if not s:
        raise HTTPException(status_code=404, detail="Not found")

    s.password_hash = hash_password(new_pass)
    session.commit()
    return {"ok": True}
