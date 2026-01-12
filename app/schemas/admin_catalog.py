from pydantic import BaseModel
from typing import Optional


class ImportCategory(BaseModel):
    id: str
    name: str
    sort: int = 0
    imageUrl: Optional[str] = None
    active: bool = True


class ImportProduct(BaseModel):
    id: str
    categoryId: str
    name: str
    description: str = ""
    basePriceCents: int
    imageUrl: Optional[str] = None
    active: bool = True


class ImportModifierGroup(BaseModel):
    id: str
    productId: str
    title: str
    required: bool = False
    minSelect: int = 0
    maxSelect: int = 1
    uiType: str = "radio"
    active: bool = True


class ImportModifierOption(BaseModel):
    id: str
    groupId: str
    name: str
    deltaCents: int = 0
    active: bool = True


class CatalogImportIn(BaseModel):
    categories: list[ImportCategory]
    products: list[ImportProduct]
    modifierGroups: list[ImportModifierGroup]
    modifierOptions: list[ImportModifierOption]
