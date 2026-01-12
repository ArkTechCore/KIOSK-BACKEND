import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import db, require_device_token
from app.models.config import KioskConfig
from app.models.menu import Category, Product, ModifierGroup, ModifierOption
from app.schemas.config import KioskConfigOut
from app.schemas.menu import MenuOut, MenuCategoryOut, MenuProductOut, MenuModifierGroupOut, MenuModifierOptionOut

router = APIRouter()

@router.get("/stores/{store_id}/kiosk-config", response_model=KioskConfigOut)
def kiosk_config(store_id: str, session: Session = Depends(db), auth=Depends(require_device_token)):
    cfg = session.get(KioskConfig, store_id)
    if not cfg:
        cfg = KioskConfig(store_id=store_id, theme_json="{}", screensaver_json="{}", idle_reset_seconds=45, product_grid_columns=4)
        session.add(cfg)
        session.commit()

    return KioskConfigOut(
        theme=json.loads(cfg.theme_json or "{}"),
        screensaver=json.loads(cfg.screensaver_json or "{}"),
        kiosk={"idleResetSeconds": cfg.idle_reset_seconds, "productGridColumns": cfg.product_grid_columns},
    )

@router.get("/stores/{store_id}/menu", response_model=MenuOut)
def menu(store_id: str, session: Session = Depends(db), auth=Depends(require_device_token)):
    cats = session.query(Category).filter(Category.store_id==store_id, Category.active==True).order_by(Category.sort.asc()).all()
    prods = session.query(Product).filter(Product.store_id==store_id, Product.active==True).all()

    # preload groups/options
    groups = session.query(ModifierGroup).filter(ModifierGroup.store_id==store_id, ModifierGroup.active==True).all()
    opts = session.query(ModifierOption).filter(ModifierOption.store_id==store_id, ModifierOption.active==True).all()

    groups_by_product: dict[str, list] = {}
    for g in groups:
        groups_by_product.setdefault(g.product_id, []).append(g)

    opts_by_group: dict[str, list] = {}
    for o in opts:
        opts_by_group.setdefault(o.group_id, []).append(o)

    out_cats = [
        MenuCategoryOut(id=c.id, name=c.name, sort=c.sort, imageUrl=c.image_url)
        for c in cats
    ]

    out_products = []
    for p in prods:
        mg = []
        for g in groups_by_product.get(p.id, []):
            mg.append(MenuModifierGroupOut(
                id=g.id,
                title=g.title,
                required=g.required,
                minSelect=g.min_select,
                maxSelect=g.max_select,
                uiType=g.ui_type,
                options=[MenuModifierOptionOut(id=o.id, name=o.name, deltaCents=o.delta_cents) for o in opts_by_group.get(g.id, [])]
            ))
        out_products.append(MenuProductOut(
            id=p.id,
            categoryId=p.category_id,
            name=p.name,
            description=p.description,
            priceCents=p.price_cents,
            available=p.active,
            imageUrl=p.image_url,
            modifierGroups=mg
        ))

    return MenuOut(categories=out_cats, products=out_products)
