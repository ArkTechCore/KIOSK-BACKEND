from pydantic import BaseModel
from typing import Optional

class OrderLineIn(BaseModel):
    productId: str
    qty: int
    selected: dict[str, list[str]]  # groupId -> optionIds
    note: Optional[str] = None

class CreateOrderIn(BaseModel):
    deviceId: str
    lines: list[OrderLineIn]

class CreateOrderOut(BaseModel):
    order_id: str
    order_number: int
    barcode_value: str
    totals: dict
