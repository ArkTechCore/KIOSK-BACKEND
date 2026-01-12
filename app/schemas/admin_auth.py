from pydantic import BaseModel, EmailStr


class AdminBootstrapIn(BaseModel):
    bootstrap_key: str
    email: EmailStr
    password: str


class AdminLoginIn(BaseModel):
    email: EmailStr
    password: str


class AdminLoginOut(BaseModel):
    token: str
    email: EmailStr
    role: str
