from uuid import UUID
from pydantic import BaseModel


class VolunteerBase(BaseModel):
    name: str
    phone: str
    latitude: float
    longitude: float
    training_level: str
    is_available: bool = True


class VolunteerCreate(VolunteerBase):
    pass


class VolunteerUpdate(BaseModel):
    latitude: float | None = None
    longitude: float | None = None
    is_available: bool | None = None


class VolunteerResponse(VolunteerBase):
    id: UUID

    class Config:
        from_attributes = True


class VolunteerNearbyResponse(BaseModel):
    volunteer: VolunteerResponse
    distance_km: float
