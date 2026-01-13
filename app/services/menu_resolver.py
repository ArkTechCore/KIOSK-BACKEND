from sqlalchemy.orm import Session
from app.models.catalog import (
    CatalogCategory,
    CatalogProduct,
    CatalogModifierGroup,
    CatalogModifierOption,
)
from app.models.overrides import (
    StoreCategoryOverride,
    StoreProductOverride,
    StoreOptionOverride,
)


def _normalize_group_rules(required: bool, min_select: int, max_select: int) -> tuple[int, int]:
    """
    Kiosk-safe rules:
    - If required=True, min_select must be at least 1
    - max_select must be >= min_select
    - max_select must be at least 1 for any selectable group
    """
    if required and min_select < 1:
        min_select = 1
    if max_select < 1:
        max_select = 1
    if max_select < min_select:
        max_select = min_select
    return int(min_select), int(max_select)


def resolved_menu(session: Session, store_id: str) -> dict:
    # Load active catalog
    cats = session.query(CatalogCategory).filter(CatalogCategory.active == True).all()
    prods = session.query(CatalogProduct).filter(CatalogProduct.active == True).all()
    groups = session.query(CatalogModifierGroup).filter(CatalogModifierGroup.active == True).all()
    opts = session.query(CatalogModifierOption).filter(CatalogModifierOption.active == True).all()

    # Overrides (store scoped)
    cat_ov = {
        o.category_id: o
        for o in session.query(StoreCategoryOverride)
        .filter(StoreCategoryOverride.store_id == store_id)
        .all()
    }
    prod_ov = {
        o.product_id: o
        for o in session.query(StoreProductOverride)
        .filter(StoreProductOverride.store_id == store_id)
        .all()
    }
    opt_ov = {
        o.option_id: o
        for o in session.query(StoreOptionOverride)
        .filter(StoreOptionOverride.store_id == store_id)
        .all()
    }

    # ----------------------------
    # Categories (sorted)
    # ----------------------------
    out_cats = []
    active_cat_ids = set()

    for c in cats:
        ov = cat_ov.get(c.id)
        active = ov.active if ov else True
        if not active:
            continue

        sort_val = ov.sort_override if (ov and ov.sort_override is not None) else c.sort

        out_cats.append(
            {
                "id": c.id,
                "name": c.name,
                "sort": int(sort_val),
                "imageUrl": c.image_url,
            }
        )
        active_cat_ids.add(c.id)

    out_cats.sort(key=lambda x: (x["sort"], x["name"].lower()))

    # ----------------------------
    # Group/option mapping + sorting
    # ----------------------------
    groups_by_product: dict[str, list[CatalogModifierGroup]] = {}
    for g in groups:
        groups_by_product.setdefault(g.product_id, []).append(g)

    # Sort groups per product by (sort, title)
    for pid, glist in groups_by_product.items():
        # If your DB doesn't have sort yet, getattr fallback keeps it safe
        glist.sort(key=lambda gg: (int(getattr(gg, "sort", 0)), gg.title.lower()))

    opts_by_group: dict[str, list[CatalogModifierOption]] = {}
    for o in opts:
        opts_by_group.setdefault(o.group_id, []).append(o)

    # Sort options per group by (sort, name)
    for gid, olist in opts_by_group.items():
        olist.sort(key=lambda oo: (int(getattr(oo, "sort", 0)), oo.name.lower()))

    # ----------------------------
    # Products (sorted by category then name)
    # ----------------------------
    out_products = []

    # Optional: stable product sort by (categoryId, name)
    prods_sorted = sorted(prods, key=lambda p: (p.category_id, p.name.lower()))

    for p in prods_sorted:
        if p.category_id not in active_cat_ids:
            continue

        pov = prod_ov.get(p.id)
        p_active = pov.active if pov else True
        if not p_active:
            continue

        price_cents = (
            pov.price_cents_override
            if (pov and pov.price_cents_override is not None)
            else p.base_price_cents
        )

        mg_out = []
        for g in groups_by_product.get(p.id, []):
            # group is already active-filtered in query, but keep safe
            if not g.active:
                continue

            options_out = []
            for o in opts_by_group.get(g.id, []):
                ov = opt_ov.get(o.id)
                o_active = ov.active if ov else True
                if not o_active:
                    continue

                delta = (
                    ov.delta_cents_override
                    if (ov and ov.delta_cents_override is not None)
                    else o.delta_cents
                )

                options_out.append(
                    {
                        "id": o.id,
                        "name": o.name,
                        "deltaCents": int(delta),
                    }
                )

            # Normalize selection rules for kiosk safety
            min_sel, max_sel = _normalize_group_rules(
                bool(g.required),
                int(g.min_select),
                int(g.max_select),
            )

            mg_out.append(
                {
                    "id": g.id,
                    "title": g.title,
                    "required": bool(g.required),
                    "minSelect": min_sel,
                    "maxSelect": max_sel,
                    "uiType": g.ui_type,
                    "sort": int(getattr(g, "sort", 0)),  # helpful for UI
                    "options": options_out,
                }
            )

        # Ensure modifierGroups order is stable even after normalization
        mg_out.sort(key=lambda x: (x.get("sort", 0), x["title"].lower()))

        out_products.append(
            {
                "id": p.id,
                "categoryId": p.category_id,
                "name": p.name,
                "description": p.description,
                "priceCents": int(price_cents),
                "imageUrl": p.image_url,
                "available": True,
                "modifierGroups": mg_out,
            }
        )

    return {"categories": out_cats, "products": out_products}
