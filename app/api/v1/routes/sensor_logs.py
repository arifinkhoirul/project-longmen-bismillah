import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.models.sensor_log import SensorLog
from app.models.sensor import Sensor
from app.models.pond import Pond
from app.schemas.sensor_log import SensorLogCreate, SensorLogResponse
from app.utils.deps import get_current_user, all_roles
from app.models.user import User

router = APIRouter(tags=["Sensor Logs"])


@router.post("/sensors/{sensor_id}/logs", response_model=SensorLogResponse)
async def create_sensor_log(
    sensor_id: uuid.UUID,
    data: SensorLogCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(all_roles),
):
    sensor = await db.get(Sensor, sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor tidak ditemukan")

    log = SensorLog(
        sensor_id=sensor_id,
        value=data.value,
        recorded_at=data.recorded_at or datetime.now(timezone.utc),
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return log


@router.get("/sensors/{sensor_id}/logs", response_model=list[SensorLogResponse])
async def get_sensor_logs(
    sensor_id: uuid.UUID,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(all_roles),
):
    result = await db.execute(
        select(SensorLog)
        .where(SensorLog.sensor_id == sensor_id)
        .order_by(SensorLog.recorded_at.desc())
        .limit(limit)
    )
    return result.scalars().all()


@router.post("/ponds/{pond_id}/logs/batch", response_model=list[SensorLogResponse])
async def create_batch_sensor_logs(
    pond_id: uuid.UUID,
    logs: list[SensorLogCreate],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(all_roles),
):
    """Input data semua sensor dalam satu kolam sekaligus."""
    created = []
    for item in logs:
        sensor = await db.get(Sensor, item.sensor_id)
        if not sensor:
            continue
        log = SensorLog(
            sensor_id=item.sensor_id,
            value=item.value,
            recorded_at=item.recorded_at or datetime.now(timezone.utc),
        )
        db.add(log)
        created.append(log)

    await db.commit()
    for log in created:
        await db.refresh(log)
    return created


@router.get("/ponds/{pond_id}/logs", response_model=list[dict])
async def get_pond_logs(
    pond_id: uuid.UUID,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(all_roles),
):
    """Ambil semua sensor logs dari satu kolam, termasuk info sensor."""
    # Ambil semua sensor di pond ini
    sensors_result = await db.execute(
        select(Sensor).where(Sensor.pond_id == pond_id)
    )
    sensors = sensors_result.scalars().all()
    sensor_ids = [s.id for s in sensors]
    sensor_map = {s.id: s for s in sensors}

    if not sensor_ids:
        return []

    # Ambil logs dari semua sensor
    logs_result = await db.execute(
        select(SensorLog)
        .where(SensorLog.sensor_id.in_(sensor_ids))
        .order_by(SensorLog.recorded_at.desc())
        .limit(limit)
    )
    logs = logs_result.scalars().all()

    # Gabungkan dengan info sensor
    result = []
    for log in logs:
        sensor = sensor_map.get(log.sensor_id)
        result.append({
            "id": str(log.id),
            "sensor_id": str(log.sensor_id),
            "value": float(log.value),
            "recorded_at": log.recorded_at.isoformat(),
            "created_at": log.created_at.isoformat(),
            "sensor_name": sensor.name if sensor else None,
            "sensor_type": sensor.type if sensor else None,
            "sensor_unit": sensor.unit if sensor else None,
        })

    return result