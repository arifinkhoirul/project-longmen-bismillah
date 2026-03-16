import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.cultivation import CultivationItem, CultivationRecord
from app.models.opex import OpexRecord
from app.models.pond import Pond
from app.models.land import Land
from app.models.user import User
from app.schemas.cultivation import (
    CultivationItemCreate, CultivationItemUpdate,
    CultivationRecordCreate, CultivationRecordUpdate,
    OpexRecordCreate, OpexRecordUpdate,
)


class CultivationService:

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

    # ── Cultivation Items (Master Data) ────────────────────

    async def get_all_items(self, db: AsyncSession) -> list:
        result = await db.execute(select(CultivationItem).order_by(CultivationItem.name))
        return result.scalars().all()

    async def get_item(self, db: AsyncSession, item_id: uuid.UUID) -> CultivationItem:
        result = await db.execute(select(CultivationItem).where(CultivationItem.id == item_id))
        item = result.scalar_one_or_none()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item tidak ditemukan")
        return item

    async def create_item(self, db: AsyncSession, payload: CultivationItemCreate) -> CultivationItem:
        item = CultivationItem(name=payload.name, category=payload.category, unit=payload.unit)
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return item

    async def update_item(self, db: AsyncSession, item_id: uuid.UUID, payload: CultivationItemUpdate) -> CultivationItem:
        item = await self.get_item(db, item_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(item, field, value)
        await db.commit()
        await db.refresh(item)
        return item

    async def delete_item(self, db: AsyncSession, item_id: uuid.UUID) -> dict:
        item = await self.get_item(db, item_id)
        await db.delete(item)
        await db.commit()
        return {"message": "Item berhasil dihapus"}

    # ── Cultivation Records ────────────────────────────────

    async def get_all_records(self, db: AsyncSession, pond_id: uuid.UUID, current_user: User) -> list:
        await self._get_pond_or_404(db, pond_id, current_user)
        result = await db.execute(
            select(CultivationRecord)
            .where(CultivationRecord.pond_id == pond_id)
            .order_by(CultivationRecord.recorded_at.desc())
        )
        return result.scalars().all()

    async def get_record(self, db: AsyncSession, pond_id: uuid.UUID, record_id: uuid.UUID, current_user: User) -> CultivationRecord:
        await self._get_pond_or_404(db, pond_id, current_user)
        result = await db.execute(
            select(CultivationRecord).where(CultivationRecord.id == record_id, CultivationRecord.pond_id == pond_id)
        )
        record = result.scalar_one_or_none()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record tidak ditemukan")
        return record

    async def create_record(self, db: AsyncSession, pond_id: uuid.UUID, payload: CultivationRecordCreate, current_user: User) -> CultivationRecord:
        await self._get_pond_or_404(db, pond_id, current_user)
        await self.get_item(db, payload.item_id)
        record = CultivationRecord(
            pond_id=pond_id,
            item_id=payload.item_id,
            quantity=payload.quantity,
            cost=payload.cost,
            recorded_by=current_user.id,
            recorded_at=payload.recorded_at or datetime.now(timezone.utc),
        )
        db.add(record)
        await db.commit()
        await db.refresh(record)
        return record

    async def update_record(self, db: AsyncSession, pond_id: uuid.UUID, record_id: uuid.UUID, payload: CultivationRecordUpdate, current_user: User) -> CultivationRecord:
        record = await self.get_record(db, pond_id, record_id, current_user)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(record, field, value)
        await db.commit()
        await db.refresh(record)
        return record

    async def delete_record(self, db: AsyncSession, pond_id: uuid.UUID, record_id: uuid.UUID, current_user: User) -> dict:
        record = await self.get_record(db, pond_id, record_id, current_user)
        await db.delete(record)
        await db.commit()
        return {"message": "Record berhasil dihapus"}

    # ── Opex Records ───────────────────────────────────────

    async def get_all_opex(self, db: AsyncSession, pond_id: uuid.UUID, current_user: User) -> list:
        await self._get_pond_or_404(db, pond_id, current_user)
        result = await db.execute(
            select(OpexRecord)
            .where(OpexRecord.pond_id == pond_id)
            .order_by(OpexRecord.created_at.desc())
        )
        return result.scalars().all()

    async def get_opex(self, db: AsyncSession, pond_id: uuid.UUID, opex_id: uuid.UUID, current_user: User) -> OpexRecord:
        await self._get_pond_or_404(db, pond_id, current_user)
        result = await db.execute(
            select(OpexRecord).where(OpexRecord.id == opex_id, OpexRecord.pond_id == pond_id)
        )
        opex = result.scalar_one_or_none()
        if not opex:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opex record tidak ditemukan")
        return opex

    async def create_opex(self, db: AsyncSession, pond_id: uuid.UUID, payload: OpexRecordCreate, current_user: User) -> OpexRecord:
        await self._get_pond_or_404(db, pond_id, current_user)
        opex = OpexRecord(
            pond_id=pond_id,
            description=payload.description,
            cost=payload.cost,
            recorded_by=current_user.id,
            created_at=payload.created_at or datetime.now(timezone.utc),
        )
        db.add(opex)
        await db.commit()
        await db.refresh(opex)
        return opex

    async def update_opex(self, db: AsyncSession, pond_id: uuid.UUID, opex_id: uuid.UUID, payload: OpexRecordUpdate, current_user: User) -> OpexRecord:
        opex = await self.get_opex(db, pond_id, opex_id, current_user)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(opex, field, value)
        await db.commit()
        await db.refresh(opex)
        return opex

    async def delete_opex(self, db: AsyncSession, pond_id: uuid.UUID, opex_id: uuid.UUID, current_user: User) -> dict:
        opex = await self.get_opex(db, pond_id, opex_id, current_user)
        await db.delete(opex)
        await db.commit()
        return {"message": "Opex record berhasil dihapus"}


cultivation_service = CultivationService()