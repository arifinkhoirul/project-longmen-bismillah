import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional


class InviteUserRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role_id: int

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v):
        if len(v) < 8:
            raise ValueError("Password minimal 8 karakter")
        return v


class UpdateUserRequest(BaseModel):
    name: Optional[str] = None
    role_id: Optional[int] = None


class UserDetailResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    role_id: Optional[int]
    company_id: Optional[uuid.UUID]
    created_at: datetime

    model_config = {"from_attributes": True}


class RoleResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}