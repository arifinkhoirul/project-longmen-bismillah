import uuid
from datetime import datetime
from sqlalchemy import String, Numeric, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.database import Base


class CultivationItem(Base):
    __tablename__ = "cultivation_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str | None] = mapped_column(String, nullable=True)
    unit: Mapped[str | None] = mapped_column(String, nullable=True)

    records: Mapped[list["CultivationRecord"]] = relationship("CultivationRecord", back_populates="item")


class CultivationRecord(Base):
    __tablename__ = "cultivation_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pond_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ponds.id"), nullable=False)
    item_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cultivation_items.id"), nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)
    cost: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    recorded_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    pond: Mapped["Pond"] = relationship("Pond", back_populates="cultivation_records")
    item: Mapped["CultivationItem"] = relationship("CultivationItem", back_populates="records")
    recorder: Mapped["User"] = relationship("User", back_populates="cultivation_records")