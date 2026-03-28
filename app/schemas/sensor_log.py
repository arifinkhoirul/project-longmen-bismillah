import uuid
from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class SensorLogCreate(BaseModel):
    sensor_id: uuid.UUID
    value: float
    recorded_at: Optional[datetime] = None


class SensorLogResponse(BaseModel):
    id: uuid.UUID
    sensor_id: uuid.UUID
    value: float
    recorded_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}