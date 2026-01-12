import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import db
from app.models.store import Store
from app.models.config import KioskConfig
from app.utils.security import hash_password

router = APIRouter()

@router.post("/admin/bootstrap-store")
def bootstrap_store(payload: dict, session: Session = Depends(db)):
    # protect with a shared secret header later; for now do ONE time and delete
    store_id = payload.get("store_id")
    password = payload.get("password")
    name = payload.get("name", store_id)

    if not store_id or not password:
        raise HTTPException(status_code=400, detail="store_id and password required")

    store = session.get(Store, store_id)
    if not store:
        store = Store(id=store_id, name=name, password_hash=hash_password(password), active=True)
        session.add(store)

    cfg = session.get(KioskConfig, store_id)
    if not cfg:
        cfg = KioskConfig(
            store_id=store_id,
            theme_json=json.dumps({"primary":"#D32F2F","background":"#F7F7F9","surface":"#FFFFFF","text":"#111111","mutedText":"#5B5B66"}),
            screensaver_json=json.dumps({"intervalSeconds":4,"slides":[]}),
            idle_reset_seconds=45,
            product_grid_columns=4,
        )
        session.add(cfg)

    session.commit()
    return {"ok": True, "store_id": store_id}
