import uuid
from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)
    role_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("roles.id"), nullable=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    company: Mapped["Company"] = relationship("Company", back_populates="users", foreign_keys=[company_id])
    role: Mapped["Role"] = relationship("Role", back_populates="users")
    password_resets: Mapped[list["PasswordReset"]] = relationship("PasswordReset", back_populates="user")
    sensor_logs: Mapped[list["SensorLog"]] = relationship("SensorLog", back_populates="recorder")
    cultivation_records: Mapped[list["CultivationRecord"]] = relationship("CultivationRecord", back_populates="recorder")
    opex_records: Mapped[list["OpexRecord"]] = relationship("OpexRecord", back_populates="recorder")
    subscription_payments: Mapped[list["SubscriptionPayment"]] = relationship("SubscriptionPayment", back_populates="paid_by_user")