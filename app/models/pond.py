import uuid
from datetime import datetime
from sqlalchemy import String, Numeric, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Pond(Base):
    __tablename__ = "ponds"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    land_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("lands.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    width: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    length: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    area: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    land: Mapped["Land"] = relationship("Land", back_populates="ponds")
    sensors: Mapped[list["Sensor"]] = relationship("Sensor", back_populates="pond")
    cultivation_records: Mapped[list["CultivationRecord"]] = relationship("CultivationRecord", back_populates="pond")
    opex_records: Mapped[list["OpexRecord"]] = relationship("OpexRecord", back_populates="pond")