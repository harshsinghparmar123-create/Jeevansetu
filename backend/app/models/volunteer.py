import uuid
from sqlalchemy import Float, String, Boolean, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class Volunteer(Base):
    __tablename__ = "volunteers"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    training_level: Mapped[str] = mapped_column(String(50), nullable=False)  # Basic, EMT, Nurse, Doctor
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
