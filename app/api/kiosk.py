import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import db, require_device_token
from app.models.config import KioskConfig
from app.services.menu_resolver import resolved_menu

router = APIRouter()


@router.get("/stores/{store_id}/kiosk-config")
def kiosk_config(store_id: str, session: Session = Depends(db), auth=Depends(require_device_token)):
    cfg = session.get(KioskConfig, store_id)
    if not cfg:
        cfg = KioskConfig(
            store_id=store_id,
            theme_json=json.dumps({
                "primary": "#D32F2F",
                "background": "#F7F7F9",
                "surface": "#FFFFFF",
                "text": "#111111",
                "mutedText": "#5B5B66"
            }),
            screensaver_json=json.dumps({"intervalSeconds": 4, "slides": []}),
            idle_reset_seconds=45,
            product_grid_columns=4,
        )
        session.add(cfg)
        session.commit()

    return {
        "theme": json.loads(cfg.theme_json or "{}"),
        "screensaver": json.loads(cfg.screensaver_json or "{}"),
        "kiosk": {
            "idleResetSeconds": cfg.idle_reset_seconds,
            "productGridColumns": cfg.product_grid_columns
        }
    }


# Existing endpoint (keep)
@router.get("/stores/{store_id}/menu")
def store_menu(store_id: str, session: Session = Depends(db), auth=Depends(require_device_token)):
    return resolved_menu(session, store_id)


# New, stable payload endpoint (use this in Flutter)
@router.get("/stores/{store_id}/menu-v2")
def store_menu_v2(store_id: str, session: Session = Depends(db), auth=Depends(require_device_token)):
    """
    v2 returns a predictable payload and is safe for backend-driven kiosk UI.
    """
    menu = resolved_menu(session, store_id)

    # Normalize small things so Flutter can depend on them
    # (we don't change your resolver internals here)
    return {
        "storeId": store_id,
        "currency": "USD",
        "menu": menu,
    }
