import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.land import LandCreate, LandUpdate, LandResponse, PondCreate, PondUpdate, PondResponse
from app.services.land_service import land_service
from app.utils.deps import get_current_user, boss_or_admin, all_roles
from app.models.user import User

router = APIRouter(prefix="/lands", tags=["Lands & Ponds"])

# ── Lands ──────────────────────────────────────────────────
@router.get("", response_model=list[LandResponse])
async def get_lands(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(all_roles()),
):
    return await land_service.get_all_lands(db, current_user)


@router.post("", response_model=LandResponse, status_code=201)
async def create_land(
    payload: LandCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(boss_or_admin()),
):
    return await land_service.create_land(db, payload, current_user)


@router.get("/{land_id}", response_model=LandResponse)
async def get_land(
    land_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(all_roles()),
):
    return await land_service.get_land(db, land_id, current_user)


@router.put("/{land_id}", response_model=LandResponse)
async def update_land(
    land_id: uuid.UUID,
    payload: LandUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(boss_or_admin()),
):
    return await land_service.update_land(db, land_id, payload, current_user)


@router.delete("/{land_id}")
async def delete_land(
    land_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(boss_or_admin()),
):
    return await land_service.delete_land(db, land_id, current_user)


# ── Ponds ──────────────────────────────────────────────────
@router.get("/{land_id}/ponds", response_model=list[PondResponse])
async def get_ponds(
    land_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(all_roles()),
):
    return await land_service.get_all_ponds(db, land_id, current_user)


@router.post("/{land_id}/ponds", response_model=PondResponse, status_code=201)
async def create_pond(
    land_id: uuid.UUID,
    payload: PondCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(boss_or_admin()),
):
    return await land_service.create_pond(db, land_id, payload, current_user)


@router.get("/{land_id}/ponds/{pond_id}", response_model=PondResponse)
async def get_pond(
    land_id: uuid.UUID,
    pond_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(all_roles()),
):
    return await land_service.get_pond(db, land_id, pond_id, current_user)


@router.put("/{land_id}/ponds/{pond_id}", response_model=PondResponse)
async def update_pond(
    land_id: uuid.UUID,
    pond_id: uuid.UUID,
    payload: PondUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(boss_or_admin()),
):
    return await land_service.update_pond(db, land_id, pond_id, payload, current_user)


@router.delete("/{land_id}/ponds/{pond_id}")
async def delete_pond(
    land_id: uuid.UUID,
    pond_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(boss_or_admin()),
):
    return await land_service.delete_pond(db, land_id, pond_id, current_user)