import uuid
from datetime import datetime
from sqlalchemy import Text, Numeric, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.database import Base


class OpexRecord(Base):
    __tablename__ = "opex_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pond_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ponds.id"), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    cost: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    recorded_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    pond: Mapped["Pond"] = relationship("Pond", back_populates="opex_records")
    recorder: Mapped["User"] = relationship("User", back_populates="opex_records")