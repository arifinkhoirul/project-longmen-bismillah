import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.sensor import (
    SensorCreate, SensorUpdate, SensorResponse,
    SensorLogCreate, SensorLogUpdate, SensorLogResponse,
)
from app.services.sensor_service import sensor_service
from app.utils.deps import boss_or_admin, all_roles
from app.models.user import User

router = APIRouter(prefix="/ponds/{pond_id}/sensors", tags=["Sensors & Logs"])

# ── Sensors ────────────────────────────────────────────────
@router.get("", response_model=list[SensorResponse])
async def get_sensors(
    pond_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(all_roles()),
):
    return await sensor_service.get_all_sensors(db, pond_id, current_user)


@router.post("", response_model=SensorResponse, status_code=201)
async def create_sensor(
    pond_id: uuid.UUID,
    payload: SensorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(boss_or_admin()),
):
    return await sensor_service.create_sensor(db, pond_id, payload, current_user)


@router.get("/{sensor_id}", response_model=SensorResponse)
async def get_sensor(
    pond_id: uuid.UUID,
    sensor_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(all_roles()),
):
    return await sensor_service.get_sensor(db, pond_id, sensor_id, current_user)


@router.put("/{sensor_id}", response_model=SensorResponse)
async def update_sensor(
    pond_id: uuid.UUID,
    sensor_id: uuid.UUID,
    payload: SensorUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(boss_or_admin()),
):
    return await sensor_service.update_sensor(db, pond_id, sensor_id, payload, current_user)


@router.delete("/{sensor_id}")
async def delete_sensor(
    pond_id: uuid.UUID,
    sensor_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(boss_or_admin()),
):
    return await sensor_service.delete_sensor(db, pond_id, sensor_id, current_user)


# ── Sensor Logs ────────────────────────────────────────────
@router.get("/{sensor_id}/logs", response_model=list[SensorLogResponse])
async def get_logs(
    pond_id: uuid.UUID,
    sensor_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(all_roles()),
):
    return await sensor_service.get_all_logs(db, pond_id, sensor_id, current_user)


@router.post("/{sensor_id}/logs", response_model=SensorLogResponse, status_code=201)
async def create_log(
    pond_id: uuid.UUID,
    sensor_id: uuid.UUID,
    payload: SensorLogCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(all_roles()),
):
    return await sensor_service.create_log(db, pond_id, sensor_id, payload, current_user)


@router.get("/{sensor_id}/logs/{log_id}", response_model=SensorLogResponse)
async def get_log(
    pond_id: uuid.UUID,
    sensor_id: uuid.UUID,
    log_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(all_roles()),
):
    return await sensor_service.get_log(db, pond_id, sensor_id, log_id, current_user)


@router.put("/{sensor_id}/logs/{log_id}", response_model=SensorLogResponse)
async def update_log(
    pond_id: uuid.UUID,
    sensor_id: uuid.UUID,
    log_id: uuid.UUID,
    payload: SensorLogUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(all_roles()),
):
    return await sensor_service.update_log(db, pond_id, sensor_id, log_id, payload, current_user)


@router.delete("/{sensor_id}/logs/{log_id}")
async def delete_log(
    pond_id: uuid.UUID,
    sensor_id: uuid.UUID,
    log_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(boss_or_admin()),
):
    return await sensor_service.delete_log(db, pond_id, sensor_id, log_id, current_user)