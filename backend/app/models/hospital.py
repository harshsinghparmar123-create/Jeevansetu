import uuid
from sqlalchemy import Float, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class Hospital(Base):
    __tablename__ = "hospitals"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    trauma_level: Mapped[int] = mapped_column(Integer, nullable=False)  # Level 1, 2, 3 capability
    available_beds: Mapped[int] = mapped_column(Integer, default=0)
    ventilators: Mapped[int] = mapped_column(Integer, default=0)
