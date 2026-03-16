from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.subscription import (
    SubscriptionPlanResponse,
    SubscriptionWithPlanResponse,
    SubscriptionPaymentWithPlanResponse,
)
from app.services.subscription_service import subscription_service
from app.utils.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/subscriptions", tags=["Subscription"])


@router.get("/plans", response_model=list[SubscriptionPlanResponse])
async def get_plans(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List semua paket subscription yang tersedia."""
    return await subscription_service.get_all_plans(db)


@router.get("/active", response_model=SubscriptionWithPlanResponse)
async def get_active_subscription(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Info subscription aktif company saat ini."""
    return await subscription_service.get_active_subscription(db, current_user)


@router.get("/history", response_model=list[SubscriptionWithPlanResponse])
async def get_subscription_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Riwayat semua subscription company."""
    return await subscription_service.get_all_subscriptions(db, current_user)


@router.get("/payments", response_model=list[SubscriptionPaymentWithPlanResponse])
async def get_payment_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Riwayat pembayaran subscription company."""
    return await subscription_service.get_payment_history(db, current_user)