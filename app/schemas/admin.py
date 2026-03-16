import uuid
from datetime import datetime, date
from pydantic import BaseModel
from typing import Optional


# ── Company ───────────────────────────────────────────────
class AdminCompanyResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    phone: Optional[str]
    address: Optional[str]
    owner_user_id: Optional[uuid.UUID]
    created_at: datetime
    total_users: int
    total_lands: int
    subscription_status: Optional[str]

    model_config = {"from_attributes": True}


# ── Subscription Plan ─────────────────────────────────────
class PlanCreate(BaseModel):
    name: str
    price: float
    duration_days: int


class PlanUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    duration_days: Optional[int] = None


class PlanResponse(BaseModel):
    id: uuid.UUID
    name: str
    price: float
    duration_days: int

    model_config = {"from_attributes": True}


# ── Stats ─────────────────────────────────────────────────
class GlobalStatsResponse(BaseModel):
    total_companies: int
    total_users: int
    total_active_subscriptions: int
    total_revenue: float


# ── Subscription overview ─────────────────────────────────
class AdminSubscriptionResponse(BaseModel):
    id: uuid.UUID
    company_id: uuid.UUID
    company_name: str
    plan_name: str
    start_date: date
    end_date: date
    status: str
    amount_paid: float

    model_config = {"from_attributes": True}