import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.cultivation import (
    CultivationItemCreate, CultivationItemUpdate, CultivationItemResponse,
    CultivationRecordCreate, CultivationRecordUpdate, CultivationRecordResponse,
    OpexRecordCreate, OpexRecordUpdate, OpexRecordResponse,
)
from app.services.cultivation_service import cultivation_service
from app.utils.deps import boss_or_admin, all_roles
from app.models.user import User

# ── Cultivation Items ─────────────────────────────────────
items_router = APIRouter(prefix="/cultivation-items", tags=["Cultivation Items"])

@items_router.get("", response_model=list[CultivationItemResponse])
async def get_items(db: AsyncSession = Depends(get_db), current_user: User = Depends(all_roles())):
    return await cultivation_service.get_all_items(db)

@items_router.post("", response_model=CultivationItemResponse, status_code=201)
async def create_item(payload: CultivationItemCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(boss_or_admin())):
    return await cultivation_service.create_item(db, payload)

@items_router.get("/{item_id}", response_model=CultivationItemResponse)
async def get_item(item_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(all_roles())):
    return await cultivation_service.get_item(db, item_id)

@items_router.put("/{item_id}", response_model=CultivationItemResponse)
async def update_item(item_id: uuid.UUID, payload: CultivationItemUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(boss_or_admin())):
    return await cultivation_service.update_item(db, item_id, payload)

@items_router.delete("/{item_id}")
async def delete_item(item_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(boss_or_admin())):
    return await cultivation_service.delete_item(db, item_id)


# ── Cultivation Records ───────────────────────────────────
records_router = APIRouter(prefix="/ponds/{pond_id}/cultivation-records", tags=["Cultivation Records"])

@records_router.get("", response_model=list[CultivationRecordResponse])
async def get_records(pond_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(all_roles())):
    return await cultivation_service.get_all_records(db, pond_id, current_user)

@records_router.post("", response_model=CultivationRecordResponse, status_code=201)
async def create_record(pond_id: uuid.UUID, payload: CultivationRecordCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(all_roles())):
    return await cultivation_service.create_record(db, pond_id, payload, current_user)

@records_router.get("/{record_id}", response_model=CultivationRecordResponse)
async def get_record(pond_id: uuid.UUID, record_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(all_roles())):
    return await cultivation_service.get_record(db, pond_id, record_id, current_user)

@records_router.put("/{record_id}", response_model=CultivationRecordResponse)
async def update_record(pond_id: uuid.UUID, record_id: uuid.UUID, payload: CultivationRecordUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(all_roles())):
    return await cultivation_service.update_record(db, pond_id, record_id, payload, current_user)

@records_router.delete("/{record_id}")
async def delete_record(pond_id: uuid.UUID, record_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(boss_or_admin())):
    return await cultivation_service.delete_record(db, pond_id, record_id, current_user)


# ── Opex Records ──────────────────────────────────────────
opex_router = APIRouter(prefix="/ponds/{pond_id}/opex-records", tags=["Opex Records"])

@opex_router.get("", response_model=list[OpexRecordResponse])
async def get_opex_list(pond_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(all_roles())):
    return await cultivation_service.get_all_opex(db, pond_id, current_user)

@opex_router.post("", response_model=OpexRecordResponse, status_code=201)
async def create_opex(pond_id: uuid.UUID, payload: OpexRecordCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(boss_or_admin())):
    return await cultivation_service.create_opex(db, pond_id, payload, current_user)

@opex_router.get("/{opex_id}", response_model=OpexRecordResponse)
async def get_opex(pond_id: uuid.UUID, opex_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(all_roles())):
    return await cultivation_service.get_opex(db, pond_id, opex_id, current_user)

@opex_router.put("/{opex_id}", response_model=OpexRecordResponse)
async def update_opex(pond_id: uuid.UUID, opex_id: uuid.UUID, payload: OpexRecordUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(boss_or_admin())):
    return await cultivation_service.update_opex(db, pond_id, opex_id, payload, current_user)

@opex_router.delete("/{opex_id}")
async def delete_opex(pond_id: uuid.UUID, opex_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(boss_or_admin())):
    return await cultivation_service.delete_opex(db, pond_id, opex_id, current_user)