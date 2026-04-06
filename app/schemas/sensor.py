import uuid
from datetime import datetime
from pydantic import BaseModel
from typing import Optional


# ── Sensor Schemas ────────────────────────────────────────
class SensorCreate(BaseModel):
    name: str
    type: str
    unit: Optional[str] = None


class SensorUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    unit: Optional[str] = None


class SensorResponse(BaseModel):
    id: uuid.UUID
    pond_id: uuid.UUID
    name: str
    type: str
    unit: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Sensor Log Schemas ────────────────────────────────────
class SensorLogCreate(BaseModel):
    value: float
    recorded_at: Optional[datetime] = None


class SensorLogUpdate(BaseModel):
    value: Optional[float] = None
    recorded_at: Optional[datetime] = None


class SensorLogResponse(BaseModel):
    id: uuid.UUID
    sensor_id: uuid.UUID
    recorded_by: Optional[uuid.UUID] = None  # ← ubah jadi Optional
    value: float
    recorded_at: datetime

    model_config = {"from_attributes": True}