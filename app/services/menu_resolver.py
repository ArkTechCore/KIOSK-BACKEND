from sqlalchemy.orm import Session
from app.models.catalog import (
    CatalogCategory, CatalogProduct, CatalogModifierGroup, CatalogModifierOption
)
from app.models.overrides import StoreCategoryOverride, StoreProductOverride, StoreOptionOverride


def resolved_menu(session: Session, store_id: str) -> dict:
    cats = session.query(CatalogCategory).filter(CatalogCategory.active == True).all()
    prods = session.query(CatalogProduct).filter(CatalogProduct.active == True).all()
    groups = session.query(CatalogModifierGroup).filter(CatalogModifierGroup.active == True).all()
    opts = session.query(CatalogModifierOption).filter(CatalogModifierOption.active == True).all()

    cat_ov = {o.category_id: o for o in session.query(StoreCategoryOverride).filter(StoreCategoryOverride.store_id == store_id).all()}
    prod_ov = {o.product_id: o for o in session.query(StoreProductOverride).filter(StoreProductOverride.store_id == store_id).all()}
    opt_ov = {o.option_id: o for o in session.query(StoreOptionOverride).filter(StoreOptionOverride.store_id == store_id).all()}

    # Categories
    out_cats = []
    active_cat_ids = set()
    for c in cats:
        ov = cat_ov.get(c.id)
        active = ov.active if ov else True
        if not active:
            continue
        sort_val = ov.sort_override if (ov and ov.sort_override is not None) else c.sort
        out_cats.append({
            "id": c.id,
            "name": c.name,
            "sort": int(sort_val),
            "imageUrl": c.image_url
        })
        active_cat_ids.add(c.id)

    out_cats.sort(key=lambda x: x["sort"])

    # Group/option mapping
    groups_by_product = {}
    for g in groups:
        groups_by_product.setdefault(g.product_id, []).append(g)

    opts_by_group = {}
    for o in opts:
        opts_by_group.setdefault(o.group_id, []).append(o)

    # Products
    out_products = []
    for p in prods:
        if p.category_id not in active_cat_ids:
            continue

        pov = prod_ov.get(p.id)
        p_active = pov.active if pov else True
        if not p_active:
            continue

        price_cents = pov.price_cents_override if (pov and pov.price_cents_override is not None) else p.base_price_cents

        mg_out = []
        for g in groups_by_product.get(p.id, []):
            if not g.active:
                continue

            options_out = []
            for o in opts_by_group.get(g.id, []):
                ov = opt_ov.get(o.id)
                o_active = ov.active if ov else True
                if not o_active:
                    continue
                delta = ov.delta_cents_override if (ov and ov.delta_cents_override is not None) else o.delta_cents
                options_out.append({
                    "id": o.id,
                    "name": o.name,
                    "deltaCents": int(delta)
                })

            mg_out.append({
                "id": g.id,
                "title": g.title,
                "required": g.required,
                "minSelect": int(g.min_select),
                "maxSelect": int(g.max_select),
                "uiType": g.ui_type,
                "options": options_out
            })

        out_products.append({
            "id": p.id,
            "categoryId": p.category_id,
            "name": p.name,
            "description": p.description,
            "priceCents": int(price_cents),
            "imageUrl": p.image_url,
            "available": True,
            "modifierGroups": mg_out
        })

    return {"categories": out_cats, "products": out_products}
