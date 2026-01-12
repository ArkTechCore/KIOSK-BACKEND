from pydantic import BaseModel

class KioskConfigOut(BaseModel):
    theme: dict
    screensaver: dict
    kiosk: dict
