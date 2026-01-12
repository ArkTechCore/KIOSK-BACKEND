from pydantic import BaseModel


class AdminCreateStoreIn(BaseModel):
    store_id: str
    name: str
    password: str


class AdminStoreOut(BaseModel):
    store_id: str
    name: str
    active: bool
