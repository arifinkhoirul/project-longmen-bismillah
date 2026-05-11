from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    company_name: str
    company_email: EmailStr
    company_phone: Optional[str] = None
    company_address: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    recaptcha_token: Optional[str] = None  # ← tambah ini


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    role_id: Optional[int] = None
    company_id: Optional[uuid.UUID] = None

    model_config = {"from_attributes": True}


class RegisterResponse(BaseModel):
    user: UserResponse
    tokens: TokenResponse


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str