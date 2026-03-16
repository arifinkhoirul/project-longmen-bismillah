import uuid
from datetime import datetime
from pydantic import BaseModel
from typing import Optional


# ── Cultivation Item ──────────────────────────────────────
class CultivationItemCreate(BaseModel):
    name: str
    category: Optional[str] = None
    unit: Optional[str] = None


class CultivationItemUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    unit: Optional[str] = None


class CultivationItemResponse(BaseModel):
    id: uuid.UUID
    name: str
    category: Optional[str]
    unit: Optional[str]

    model_config = {"from_attributes": True}


# ── Cultivation Record ────────────────────────────────────
class CultivationRecordCreate(BaseModel):
    item_id: uuid.UUID
    quantity: float
    cost: Optional[float] = None
    recorded_at: Optional[datetime] = None


class CultivationRecordUpdate(BaseModel):
    item_id: Optional[uuid.UUID] = None
    quantity: Optional[float] = None
    cost: Optional[float] = None
    recorded_at: Optional[datetime] = None


class CultivationRecordResponse(BaseModel):
    id: uuid.UUID
    pond_id: uuid.UUID
    item_id: uuid.UUID
    quantity: float
    cost: Optional[float]
    recorded_by: uuid.UUID
    recorded_at: datetime

    model_config = {"from_attributes": True}


# ── Opex Record ───────────────────────────────────────────
class OpexRecordCreate(BaseModel):
    description: str
    cost: float
    created_at: Optional[datetime] = None


class OpexRecordUpdate(BaseModel):
    description: Optional[str] = None
    cost: Optional[float] = None


class OpexRecordResponse(BaseModel):
    id: uuid.UUID
    pond_id: uuid.UUID
    description: str
    cost: float
    recorded_by: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}