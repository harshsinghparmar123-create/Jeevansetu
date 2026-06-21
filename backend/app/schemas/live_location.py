from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class LiveLocationBase(BaseModel):
    latitude: float
    longitude: float


class LiveLocationUpdate(LiveLocationBase):
    pass


class LiveLocationResponse(LiveLocationBase):
    id: UUID
    user_id: UUID
    updated_at: datetime

    class Config:
        from_attributes = True
