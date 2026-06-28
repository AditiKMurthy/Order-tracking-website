# The "Rules" for user data (Pydantic validation).
from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class VerifyOTP(BaseModel):
    email: str
    code: str
    purpose: str  # "register" or "reset"

class ForgotPassword(BaseModel):
    email: str

class ResetPassword(BaseModel):
    email: str
    code: str
    new_password: str

class GoogleLoginRequest(BaseModel):
    id_token: str

class Token(BaseModel):
    access_token: str
    token_type: str

class OrderCreate(BaseModel):
    item_name: str
    destination: str

class OrderResponse(BaseModel):
    id: int
    item_name: str
    destination: str
    status: str
    delivery_date: Optional[str] = None

    class Config:
        from_attributes = True