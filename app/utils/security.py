import hashlib
from passlib.context import CryptContext

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _safe(raw: str) -> str:
    b = raw.encode("utf-8")
    if len(b) > 72:
        return hashlib.sha256(b).hexdigest()
    return raw

def hash_password(raw: str) -> str:
    return pwd.hash(_safe(raw))

def verify_password(raw: str, hashed: str) -> bool:
    return pwd.verify(_safe(raw), hashed)
