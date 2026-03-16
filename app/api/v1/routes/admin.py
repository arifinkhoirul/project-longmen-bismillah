import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.admin import (
    PlanCreate, PlanUpdate, PlanResponse,
    GlobalStatsResponse, AdminSubscriptionResponse,
)
from app.services.admin_service import admin_service
from app.utils.deps import require_roles
from app.models.user import User

ROLE_SUPERADMIN = 4

router = APIRouter(prefix="/admin", tags=["Super Admin"])

def superadmin_only():
    return require_roles(ROLE_SUPERADMIN)


# ── Stats ──────────────────────────────────────────────────
@router.get("/stats", response_model=GlobalStatsResponse)
async def get_global_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(superadmin_only()),
):
    """Statistik global seluruh platform."""
    return await admin_service.get_global_stats(db)


# ── Companies ──────────────────────────────────────────────
@router.get("/companies")
async def get_all_companies(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(superadmin_only()),
):
    """List semua company yang terdaftar."""
    return await admin_service.get_all_companies(db)


@router.get("/companies/{company_id}")
async def get_company_detail(
    company_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(superadmin_only()),
):
    """Detail satu company."""
    return await admin_service.get_company_detail(db, company_id)


# ── Subscription Plans ─────────────────────────────────────
@router.get("/plans", response_model=list[PlanResponse])
async def get_plans(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(superadmin_only()),
):
    """List semua paket subscription."""
    return await admin_service.get_all_plans(db)


@router.post("/plans", response_model=PlanResponse, status_code=201)
async def create_plan(
    payload: PlanCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(superadmin_only()),
):
    """Buat paket subscription baru."""
    return await admin_service.create_plan(db, payload)


@router.put("/plans/{plan_id}", response_model=PlanResponse)
async def update_plan(
    plan_id: uuid.UUID,
    payload: PlanUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(superadmin_only()),
):
    """Update paket subscription."""
    return await admin_service.update_plan(db, plan_id, payload)


@router.delete("/plans/{plan_id}")
async def delete_plan(
    plan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(superadmin_only()),
):
    """Hapus paket subscription."""
    return await admin_service.delete_plan(db, plan_id)


# ── Subscriptions ──────────────────────────────────────────
@router.get("/subscriptions", response_model=list[AdminSubscriptionResponse])
async def get_all_subscriptions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(superadmin_only()),
):
    """List semua subscription dari seluruh company."""
    return await admin_service.get_all_subscriptions(db)