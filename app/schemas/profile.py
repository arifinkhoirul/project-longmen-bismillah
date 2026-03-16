import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional


class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None


class UpdateCompanyRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class CompanyResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    phone: Optional[str]
    address: Optional[str]
    owner_user_id: Optional[uuid.UUID]
    created_at: datetime

    model_config = {"from_attributes": True}


class ProfileResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    role_id: Optional[int]
    company_id: Optional[uuid.UUID]
    created_at: datetime
    company: Optional[CompanyResponse]

    model_config = {"from_attributes": True}