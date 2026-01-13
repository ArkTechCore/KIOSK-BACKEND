from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import db, require_admin
from app.models.catalog import (
    CatalogCategory,
    CatalogProduct,
    CatalogModifierGroup,
    CatalogModifierOption,
)

router = APIRouter()


def _cat_row(x: dict) -> CatalogCategory:
    return CatalogCategory(
        id=x["id"],
        name=x["name"],
        sort=int(x.get("sort", 0)),
        image_url=x.get("imageUrl") or None,
        active=bool(x.get("active", True)),
    )


def _prod_row(x: dict) -> CatalogProduct:
    return CatalogProduct(
        id=x["id"],
        category_id=x["categoryId"],
        name=x["name"],
        description=x.get("description", "") or "",
        base_price_cents=int(x.get("basePriceCents", 0)),
        image_url=x.get("imageUrl") or None,
        active=bool(x.get("active", True)),
    )


def _group_row(x: dict) -> CatalogModifierGroup:
    return CatalogModifierGroup(
        id=x["id"],
        product_id=x["productId"],
        title=x["title"],
        required=bool(x.get("required", False)),
        min_select=int(x.get("minSelect", 0)),
        max_select=int(x.get("maxSelect", 1)),
        ui_type=x.get("uiType", "radio"),
        active=bool(x.get("active", True)),
        sort=int(x.get("sort", 0)),
    )


def _opt_row(x: dict) -> CatalogModifierOption:
    return CatalogModifierOption(
        id=x["id"],
        group_id=x["groupId"],
        name=x["name"],
        delta_cents=int(x.get("deltaCents", 0)),
        active=bool(x.get("active", True)),
        sort=int(x.get("sort", 0)),
    )


@router.post("/admin/catalog/import")
def import_catalog(
    body: dict,
    session: Session = Depends(db),
    admin=Depends(require_admin),
):
    # Expecting:
    # body = { categories:[], products:[], modifierGroups:[], modifierOptions:[] }

    categories = body.get("categories") or []
    products = body.get("products") or []
    groups = body.get("modifierGroups") or []
    options = body.get("modifierOptions") or []

    # wipe existing catalog (simple + safe with FK order)
    session.query(CatalogModifierOption).delete()
    session.query(CatalogModifierGroup).delete()
    session.query(CatalogProduct).delete()
    session.query(CatalogCategory).delete()
    session.commit()

    # insert new catalog
    for c in categories:
        session.add(_cat_row(c))
    for p in products:
        session.add(_prod_row(p))
    session.commit()

    for g in groups:
        session.add(_group_row(g))
    session.commit()

    for o in options:
        session.add(_opt_row(o))
    session.commit()

    return {"ok": True, "counts": {
        "categories": len(categories),
        "products": len(products),
        "modifierGroups": len(groups),
        "modifierOptions": len(options),
    }}


@router.get("/admin/catalog/export")
def export_catalog(
    session: Session = Depends(db),
    admin=Depends(require_admin),
):
    cats = session.query(CatalogCategory).order_by(CatalogCategory.sort.asc(), CatalogCategory.id.asc()).all()
    prods = session.query(CatalogProduct).order_by(CatalogProduct.category_id.asc(), CatalogProduct.id.asc()).all()
    groups = session.query(CatalogModifierGroup).order_by(CatalogModifierGroup.product_id.asc(), CatalogModifierGroup.sort.asc()).all()
    opts = session.query(CatalogModifierOption).order_by(CatalogModifierOption.group_id.asc(), CatalogModifierOption.sort.asc()).all()

    return {
        "categories": [
            {
                "id": c.id,
                "name": c.name,
                "sort": c.sort,
                "imageUrl": c.image_url,
                "active": c.active,
            } for c in cats
        ],
        "products": [
            {
                "id": p.id,
                "categoryId": p.category_id,
                "name": p.name,
                "description": p.description,
                "basePriceCents": p.base_price_cents,
                "imageUrl": p.image_url,
                "active": p.active,
            } for p in prods
        ],
        "modifierGroups": [
            {
                "id": g.id,
                "productId": g.product_id,
                "title": g.title,
                "required": g.required,
                "minSelect": g.min_select,
                "maxSelect": g.max_select,
                "uiType": g.ui_type,
                "active": g.active,
                "sort": g.sort,
            } for g in groups
        ],
        "modifierOptions": [
            {
                "id": o.id,
                "groupId": o.group_id,
                "name": o.name,
                "deltaCents": o.delta_cents,
                "active": o.active,
                "sort": o.sort,
            } for o in opts
        ],
    }
