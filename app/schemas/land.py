import uuid
from datetime import datetime
from pydantic import BaseModel
from typing import Optional


# ── Land Schemas ──────────────────────────────────────────
class LandCreate(BaseModel):
    name: str
    width: Optional[float] = None
    length: Optional[float] = None
    total_area: Optional[float] = None


class LandUpdate(BaseModel):
    name: Optional[str] = None
    width: Optional[float] = None
    length: Optional[float] = None
    total_area: Optional[float] = None


class LandResponse(BaseModel):
    id: uuid.UUID
    company_id: uuid.UUID
    name: str
    width: Optional[float]
    length: Optional[float]
    total_area: Optional[float]
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Pond Schemas ──────────────────────────────────────────
class PondCreate(BaseModel):
    name: str
    width: Optional[float] = None
    length: Optional[float] = None
    area: Optional[float] = None


class PondUpdate(BaseModel):
    name: Optional[str] = None
    width: Optional[float] = None
    length: Optional[float] = None
    area: Optional[float] = None


class PondResponse(BaseModel):
    id: uuid.UUID
    land_id: uuid.UUID
    name: str
    width: Optional[float]
    length: Optional[float]
    area: Optional[float]
    created_at: datetime

    model_config = {"from_attributes": True}