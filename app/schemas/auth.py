from pydantic import BaseModel


class DeviceLoginIn(BaseModel):
    store_id: str
    device_id: str
    password: str
    role: str  # KIOSK / KITCHEN / POSHELPER


class DeviceLoginOut(BaseModel):
    token: str
    store_id: str
    role: str
