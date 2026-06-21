import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class AuthorityAlert(Base):
    __tablename__ = "authority_alerts"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    accident_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("accidents.id", ondelete="CASCADE"), nullable=False
    )
    authority_type: Mapped[str] = mapped_column(String(50), nullable=False)  # Police, Fire, Medical
    status: Mapped[str] = mapped_column(String(50), default="notified")  # notified, dispatched, resolved
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    accident: Mapped["Accident"] = relationship("Accident")
