import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import String, DateTime, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    fcm_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    contacts: Mapped[List["EmergencyContact"]] = relationship(
        "EmergencyContact", back_populates="user", cascade="all, delete-orphan"
    )
    accidents: Mapped[List["Accident"]] = relationship(
        "Accident", back_populates="user", cascade="all, delete-orphan"
    )
    live_location: Mapped[Optional["LiveLocation"]] = relationship(
        "LiveLocation", back_populates="user", cascade="all, delete-orphan", uselist=False
    )
    sos_requests: Mapped[List["SOSRequest"]] = relationship(
        "SOSRequest", back_populates="user", cascade="all, delete-orphan"
    )
