from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.admin_deps import db, require_admin_token
from app.models.catalog import (
    CatalogCategory, CatalogProduct, CatalogModifierGroup, CatalogModifierOption
)
from app.schemas.admin_catalog import CatalogImportIn

router = APIRouter()


@router.post("/admin/catalog/import")
def import_catalog(body: CatalogImportIn, session: Session = Depends(db), admin=Depends(require_admin_token)):
    # Upsert style: delete and re-insert for simplicity (fast + clean for MVP)
    session.query(CatalogModifierOption).delete()
    session.query(CatalogModifierGroup).delete()
    session.query(CatalogProduct).delete()
    session.query(CatalogCategory).delete()
    session.commit()

    for c in body.categories:
        session.add(CatalogCategory(
            id=c.id, name=c.name, sort=c.sort, image_url=c.imageUrl, active=c.active
        ))

    for p in body.products:
        session.add(CatalogProduct(
            id=p.id,
            category_id=p.categoryId,
            name=p.name,
            description=p.description,
            base_price_cents=p.basePriceCents,
            image_url=p.imageUrl,
            active=p.active
        ))

    for g in body.modifierGroups:
        session.add(CatalogModifierGroup(
            id=g.id,
            product_id=g.productId,
            title=g.title,
            required=g.required,
            min_select=g.minSelect,
            max_select=g.maxSelect,
            ui_type=g.uiType,
            active=g.active
        ))

    for o in body.modifierOptions:
        session.add(CatalogModifierOption(
            id=o.id,
            group_id=o.groupId,
            name=o.name,
            delta_cents=o.deltaCents,
            active=o.active
        ))

    session.commit()
    return {"ok": True}


@router.get("/admin/catalog/export")
def export_catalog(session: Session = Depends(db), admin=Depends(require_admin_token)):
    cats = session.query(CatalogCategory).order_by(CatalogCategory.sort.asc()).all()
    prods = session.query(CatalogProduct).all()
    groups = session.query(CatalogModifierGroup).all()
    opts = session.query(CatalogModifierOption).all()

    return {
        "categories": [
            {"id": c.id, "name": c.name, "sort": c.sort, "imageUrl": c.image_url, "active": c.active}
            for c in cats
        ],
        "products": [
            {"id": p.id, "categoryId": p.category_id, "name": p.name, "description": p.description,
             "basePriceCents": p.base_price_cents, "imageUrl": p.image_url, "active": p.active}
            for p in prods
        ],
        "modifierGroups": [
            {"id": g.id, "productId": g.product_id, "title": g.title, "required": g.required,
             "minSelect": g.min_select, "maxSelect": g.max_select, "uiType": g.ui_type, "active": g.active}
            for g in groups
        ],
        "modifierOptions": [
            {"id": o.id, "groupId": o.group_id, "name": o.name, "deltaCents": o.delta_cents, "active": o.active}
            for o in opts
        ],
    }
