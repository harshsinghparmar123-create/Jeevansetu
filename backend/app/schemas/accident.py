from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class AccidentBase(BaseModel):
    latitude: float
    longitude: float
    impact_force: float
    speed: float
    orientation_change: float


class AccidentCreate(AccidentBase):
    pass


class AccidentUpdate(BaseModel):
    severity: str | None = None
    risk_score: int | None = None
    status: str | None = None


class AccidentResponse(AccidentBase):
    id: UUID
    user_id: UUID
    severity: str
    risk_score: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
