from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.subscription import SubscriptionPlan, Subscription, SubscriptionPayment
from app.models.user import User


class SubscriptionService:

    async def get_all_plans(self, db: AsyncSession) -> list:
        """List semua paket subscription yang tersedia."""
        result = await db.execute(select(SubscriptionPlan).order_by(SubscriptionPlan.price))
        return result.scalars().all()

    async def get_active_subscription(self, db: AsyncSession, current_user: User):
        """Ambil subscription aktif milik company user."""
        result = await db.execute(
            select(Subscription)
            .options(selectinload(Subscription.plan))
            .where(
                Subscription.company_id == current_user.company_id,
                Subscription.status == "active"
            )
            .order_by(Subscription.end_date.desc())
        )
        subscription = result.scalars().first()
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tidak ada subscription aktif"
            )
        return subscription

    async def get_all_subscriptions(self, db: AsyncSession, current_user: User) -> list:
        """Riwayat semua subscription company."""
        result = await db.execute(
            select(Subscription)
            .options(selectinload(Subscription.plan))
            .where(Subscription.company_id == current_user.company_id)
            .order_by(Subscription.start_date.desc())
        )
        return result.scalars().all()

    async def get_payment_history(self, db: AsyncSession, current_user: User) -> list:
        """Riwayat pembayaran subscription company."""
        result = await db.execute(
            select(SubscriptionPayment)
            .options(
                selectinload(SubscriptionPayment.subscription).selectinload(Subscription.plan)
            )
            .join(Subscription, SubscriptionPayment.subscription_id == Subscription.id)
            .where(Subscription.company_id == current_user.company_id)
            .order_by(SubscriptionPayment.payment_date.desc())
        )
        return result.scalars().all()


subscription_service = SubscriptionService()