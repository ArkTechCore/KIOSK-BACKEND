from pydantic import BaseModel
from typing import Optional


class PosLookupOut(BaseModel):
    found: bool
    order_number: Optional[int] = None
    barcode_value: Optional[str] = None
    total_cents: Optional[int] = None
    payment_status: Optional[str] = None
    status: Optional[str] = None


class PosMarkPaidIn(BaseModel):
    barcode: str
    pos_txn_id: str
    paid_amount_cents: int
