import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.sensor import Sensor
from app.models.sensor_log import SensorLog
from app.models.pond import Pond
from app.models.land import Land
from app.models.user import User
from app.schemas.sensor import SensorCreate, SensorUpdate, SensorLogCreate, SensorLogUpdate


class SensorService:

    # ── Helpers ────────────────────────────────────────────

    async def _get_pond_or_404(self, db: AsyncSession, pond_id: uuid.UUID, current_user: User) -> Pond:
        result = await db.execute(
            select(Pond)
            .join(Land, Pond.land_id == Land.id)
            .where(Pond.id == pond_id, Land.company_id == current_user.company_id)
        )
        pond = result.scalar_one_or_none()
        if not pond:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pond tidak ditemukan")
        return pond

    async def _get_sensor_or_404(self, db: AsyncSession, pond_id: uuid.UUID, sensor_id: uuid.UUID, current_user: User) -> Sensor:
        await self._get_pond_or_404(db, pond_id, current_user)
        result = await db.execute(
            select(Sensor).where(Sensor.id == sensor_id, Sensor.pond_id == pond_id)
        )
        sensor = result.scalar_one_or_none()
        if not sensor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sensor tidak ditemukan")
        return sensor

    async def _get_log_or_404(self, db: AsyncSession, sensor_id: uuid.UUID, log_id: uuid.UUID) -> SensorLog:
        result = await db.execute(
            select(SensorLog).where(SensorLog.id == log_id, SensorLog.sensor_id == sensor_id)
        )
        log = result.scalar_one_or_none()
        if not log:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log tidak ditemukan")
        return log

    # ── Sensors ────────────────────────────────────────────

    async def get_all_sensors(self, db: AsyncSession, pond_id: uuid.UUID, current_user: User) -> list:
        await self._get_pond_or_404(db, pond_id, current_user)
        result = await db.execute(select(Sensor).where(Sensor.pond_id == pond_id))
        return result.scalars().all()

    async def get_sensor(self, db: AsyncSession, pond_id: uuid.UUID, sensor_id: uuid.UUID, current_user: User) -> Sensor:
        return await self._get_sensor_or_404(db, pond_id, sensor_id, current_user)

    async def create_sensor(self, db: AsyncSession, pond_id: uuid.UUID, payload: SensorCreate, current_user: User) -> Sensor:
        await self._get_pond_or_404(db, pond_id, current_user)
        sensor = Sensor(pond_id=pond_id, name=payload.name, type=payload.type, unit=payload.unit)
        db.add(sensor)
        await db.commit()
        await db.refresh(sensor)
        return sensor

    async def update_sensor(self, db: AsyncSession, pond_id: uuid.UUID, sensor_id: uuid.UUID, payload: SensorUpdate, current_user: User) -> Sensor:
        sensor = await self._get_sensor_or_404(db, pond_id, sensor_id, current_user)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(sensor, field, value)
        await db.commit()
        await db.refresh(sensor)
        return sensor

    async def delete_sensor(self, db: AsyncSession, pond_id: uuid.UUID, sensor_id: uuid.UUID, current_user: User) -> dict:
        sensor = await self._get_sensor_or_404(db, pond_id, sensor_id, current_user)
        await db.delete(sensor)
        await db.commit()
        return {"message": "Sensor berhasil dihapus"}

    # ── Sensor Logs ────────────────────────────────────────

    async def get_all_logs(self, db: AsyncSession, pond_id: uuid.UUID, sensor_id: uuid.UUID, current_user: User) -> list:
        await self._get_sensor_or_404(db, pond_id, sensor_id, current_user)
        result = await db.execute(
            select(SensorLog)
            .where(SensorLog.sensor_id == sensor_id)
            .order_by(SensorLog.recorded_at.desc())
        )
        return result.scalars().all()

    async def get_log(self, db: AsyncSession, pond_id: uuid.UUID, sensor_id: uuid.UUID, log_id: uuid.UUID, current_user: User) -> SensorLog:
        await self._get_sensor_or_404(db, pond_id, sensor_id, current_user)
        return await self._get_log_or_404(db, sensor_id, log_id)

    async def create_log(self, db: AsyncSession, pond_id: uuid.UUID, sensor_id: uuid.UUID, payload: SensorLogCreate, current_user: User) -> SensorLog:
        await self._get_sensor_or_404(db, pond_id, sensor_id, current_user)
        log = SensorLog(
            sensor_id=sensor_id,
            # recorded_by=current_user.id,
            value=payload.value,
            recorded_at=payload.recorded_at or datetime.now(timezone.utc),
        )
        db.add(log)
        await db.commit()
        await db.refresh(log)
        return log

    async def update_log(self, db: AsyncSession, pond_id: uuid.UUID, sensor_id: uuid.UUID, log_id: uuid.UUID, payload: SensorLogUpdate, current_user: User) -> SensorLog:
        await self._get_sensor_or_404(db, pond_id, sensor_id, current_user)
        log = await self._get_log_or_404(db, sensor_id, log_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(log, field, value)
        await db.commit()
        await db.refresh(log)
        return log

    async def delete_log(self, db: AsyncSession, pond_id: uuid.UUID, sensor_id: uuid.UUID, log_id: uuid.UUID, current_user: User) -> dict:
        await self._get_sensor_or_404(db, pond_id, sensor_id, current_user)
        log = await self._get_log_or_404(db, sensor_id, log_id)
        await db.delete(log)
        await db.commit()
        return {"message": "Log berhasil dihapus"}


sensor_service = SensorService()