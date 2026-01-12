from pydantic import BaseModel
from typing import Optional

class MenuCategoryOut(BaseModel):
    id: str
    name: str
    sort: int
    imageUrl: Optional[str] = None

class MenuModifierOptionOut(BaseModel):
    id: str
    name: str
    deltaCents: int

class MenuModifierGroupOut(BaseModel):
    id: str
    title: str
    required: bool
    minSelect: int
    maxSelect: int
    uiType: str
    options: list[MenuModifierOptionOut]

class MenuProductOut(BaseModel):
    id: str
    categoryId: str
    name: str
    description: str
    priceCents: int
    available: bool
    imageUrl: Optional[str] = None
    modifierGroups: list[MenuModifierGroupOut]

class MenuOut(BaseModel):
    categories: list[MenuCategoryOut]
    products: list[MenuProductOut]
