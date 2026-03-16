import uuid
from datetime import date, datetime
from pydantic import BaseModel
from typing import Optional


# ── Subscription Plan ─────────────────────────────────────
class SubscriptionPlanResponse(BaseModel):
    id: uuid.UUID
    name: str
    price: float
    duration_days: int

    model_config = {"from_attributes": True}


# ── Subscription ──────────────────────────────────────────
class SubscriptionResponse(BaseModel):
    id: uuid.UUID
    company_id: uuid.UUID
    plan_id: uuid.UUID
    start_date: date
    end_date: date
    status: str

    model_config = {"from_attributes": True}


class SubscriptionWithPlanResponse(BaseModel):
    id: uuid.UUID
    company_id: uuid.UUID
    start_date: date
    end_date: date
    status: str
    plan: SubscriptionPlanResponse

    model_config = {"from_attributes": True}


# ── Subscription Payment ──────────────────────────────────
class SubscriptionPaymentResponse(BaseModel):
    id: uuid.UUID
    subscription_id: uuid.UUID
    paid_by: uuid.UUID
    amount: float
    payment_method: Optional[str]
    payment_date: datetime

    model_config = {"from_attributes": True}


class SubscriptionPaymentWithPlanResponse(BaseModel):
    id: uuid.UUID
    amount: float
    payment_method: Optional[str]
    payment_date: datetime
    subscription: SubscriptionWithPlanResponse

    model_config = {"from_attributes": True}