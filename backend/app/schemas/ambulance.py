from uuid import UUID
from pydantic import BaseModel


class AmbulanceBase(BaseModel):
    name: str
    license_plate: str
    latitude: float
    longitude: float
    status: str = "available"


class AmbulanceCreate(AmbulanceBase):
    pass


class AmbulanceUpdate(BaseModel):
    latitude: float | None = None
    longitude: float | None = None
    status: str | None = None


class AmbulanceResponse(AmbulanceBase):
    id: UUID

    class Config:
        from_attributes = True


class AmbulanceDispatchInput(BaseModel):
    ambulance_id: UUID
    accident_id: UUID


class AmbulanceETAResponse(BaseModel):
    ambulance: AmbulanceResponse
    estimated_travel_time_mins: float
    distance_km: float
