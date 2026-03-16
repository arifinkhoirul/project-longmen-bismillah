import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.company import Company
from app.models.user import User
from app.models.land import Land
from app.models.subscription import SubscriptionPlan, Subscription, SubscriptionPayment
from app.schemas.admin import PlanCreate, PlanUpdate, GlobalStatsResponse, AdminSubscriptionResponse


class AdminService:

    # ── Stats ──────────────────────────────────────────────

    async def get_global_stats(self, db: AsyncSession) -> GlobalStatsResponse:
        """Statistik global seluruh platform."""
        total_companies = await db.scalar(select(func.count(Company.id)))
        total_users = await db.scalar(select(func.count(User.id)))
        total_active_subs = await db.scalar(
            select(func.count(Subscription.id)).where(Subscription.status == "active")
        )
        total_revenue = await db.scalar(
            select(func.coalesce(func.sum(SubscriptionPayment.amount), 0))
        )

        return GlobalStatsResponse(
            total_companies=total_companies or 0,
            total_users=total_users or 0,
            total_active_subscriptions=total_active_subs or 0,
            total_revenue=float(total_revenue or 0),
        )

    # ── Companies ──────────────────────────────────────────

    async def get_all_companies(self, db: AsyncSession) -> list:
        """List semua company beserta ringkasan data."""
        result = await db.execute(
            select(Company).options(
                selectinload(Company.users),
                selectinload(Company.lands),
                selectinload(Company.subscriptions),
            )
        )
        companies = result.scalars().all()

        output = []
        for company in companies:
            active_sub = next((s for s in company.subscriptions if s.status == "active"), None)
            output.append({
                "id": company.id,
                "name": company.name,
                "email": company.email,
                "phone": company.phone,
                "address": company.address,
                "owner_user_id": company.owner_user_id,
                "created_at": company.created_at,
                "total_users": len(company.users),
                "total_lands": len(company.lands),
                "subscription_status": active_sub.status if active_sub else None,
            })
        return output

    async def get_company_detail(self, db: AsyncSession, company_id: uuid.UUID) -> dict:
        """Detail satu company beserta semua data."""
        result = await db.execute(
            select(Company)
            .options(
                selectinload(Company.users),
                selectinload(Company.lands),
                selectinload(Company.subscriptions).selectinload(Subscription.plan),
            )
            .where(Company.id == company_id)
        )
        company = result.scalar_one_or_none()
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company tidak ditemukan")

        active_sub = next((s for s in company.subscriptions if s.status == "active"), None)
        return {
            "id": company.id,
            "name": company.name,
            "email": company.email,
            "phone": company.phone,
            "address": company.address,
            "owner_user_id": company.owner_user_id,
            "created_at": company.created_at,
            "total_users": len(company.users),
            "total_lands": len(company.lands),
            "subscription_status": active_sub.status if active_sub else None,
        }

    # ── Subscription Plans ─────────────────────────────────

    async def get_all_plans(self, db: AsyncSession) -> list:
        result = await db.execute(select(SubscriptionPlan).order_by(SubscriptionPlan.price))
        return result.scalars().all()

    async def create_plan(self, db: AsyncSession, payload: PlanCreate) -> SubscriptionPlan:
        plan = SubscriptionPlan(name=payload.name, price=payload.price, duration_days=payload.duration_days)
        db.add(plan)
        await db.commit()
        await db.refresh(plan)
        return plan

    async def update_plan(self, db: AsyncSession, plan_id: uuid.UUID, payload: PlanUpdate) -> SubscriptionPlan:
        result = await db.execute(select(SubscriptionPlan).where(SubscriptionPlan.id == plan_id))
        plan = result.scalar_one_or_none()
        if not plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan tidak ditemukan")
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(plan, field, value)
        await db.commit()
        await db.refresh(plan)
        return plan

    async def delete_plan(self, db: AsyncSession, plan_id: uuid.UUID) -> dict:
        result = await db.execute(select(SubscriptionPlan).where(SubscriptionPlan.id == plan_id))
        plan = result.scalar_one_or_none()
        if not plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan tidak ditemukan")
        await db.delete(plan)
        await db.commit()
        return {"message": "Plan berhasil dihapus"}

    # ── Subscriptions ──────────────────────────────────────

    async def get_all_subscriptions(self, db: AsyncSession) -> list:
        """Semua subscription dari seluruh company."""
        result = await db.execute(
            select(Subscription)
            .options(
                selectinload(Subscription.plan),
                selectinload(Subscription.company),
                selectinload(Subscription.payments),
            )
            .order_by(Subscription.status)
        )
        subscriptions = result.scalars().all()

        output = []
        for sub in subscriptions:
            total_paid = sum(p.amount for p in sub.payments)
            output.append(AdminSubscriptionResponse(
                id=sub.id,
                company_id=sub.company_id,
                company_name=sub.company.name,
                plan_name=sub.plan.name,
                start_date=sub.start_date,
                end_date=sub.end_date,
                status=sub.status,
                amount_paid=float(total_paid),
            ))
        return output


admin_service = AdminService()