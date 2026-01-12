from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.admin_deps import db, require_admin_token
from app.models.overrides import StoreCategoryOverride, StoreProductOverride, StoreOptionOverride
from app.schemas.admin_overrides import StoreOverridesIn

router = APIRouter()


@router.put("/admin/stores/{store_id}/overrides")
def set_overrides(store_id: str, body: StoreOverridesIn, session: Session = Depends(db), admin=Depends(require_admin_token)):
    session.query(StoreCategoryOverride).filter(StoreCategoryOverride.store_id == store_id).delete()
    session.query(StoreProductOverride).filter(StoreProductOverride.store_id == store_id).delete()
    session.query(StoreOptionOverride).filter(StoreOptionOverride.store_id == store_id).delete()
    session.commit()

    for c in body.categories:
        session.add(StoreCategoryOverride(
            store_id=store_id,
            category_id=c.categoryId,
            active=c.active,
            sort_override=c.sortOverride
        ))

    for p in body.products:
        session.add(StoreProductOverride(
            store_id=store_id,
            product_id=p.productId,
            active=p.active,
            price_cents_override=p.priceCentsOverride
        ))

    for o in body.options:
        session.add(StoreOptionOverride(
            store_id=store_id,
            option_id=o.optionId,
            active=o.active,
            delta_cents_override=o.deltaCentsOverride
        ))

    session.commit()
    return {"ok": True}
