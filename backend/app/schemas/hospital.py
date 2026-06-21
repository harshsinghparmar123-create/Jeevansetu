from uuid import UUID
from pydantic import BaseModel


class HospitalBase(BaseModel):
    name: str
    latitude: float
    longitude: float
    trauma_level: int
    available_beds: int
    ventilators: int


class HospitalCreate(HospitalBase):
    pass


class HospitalUpdate(BaseModel):
    name: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    trauma_level: int | None = None
    available_beds: int | None = None
    ventilators: int | None = None


class HospitalResponse(HospitalBase):
    id: UUID

    class Config:
        from_attributes = True


class HospitalRecommendationResponse(BaseModel):
    hospital: HospitalResponse
    score: float
    estimated_travel_time_mins: float
    distance_km: float
