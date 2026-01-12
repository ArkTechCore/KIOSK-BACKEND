from pydantic import BaseModel
from typing import Optional


class CategoryOverrideIn(BaseModel):
    categoryId: str
    active: bool = True
    sortOverride: Optional[int] = None


class ProductOverrideIn(BaseModel):
    productId: str
    active: bool = True
    priceCentsOverride: Optional[int] = None


class OptionOverrideIn(BaseModel):
    optionId: str
    active: bool = True
    deltaCentsOverride: Optional[int] = None


class StoreOverridesIn(BaseModel):
    categories: list[CategoryOverrideIn] = []
    products: list[ProductOverrideIn] = []
    options: list[OptionOverrideIn] = []
