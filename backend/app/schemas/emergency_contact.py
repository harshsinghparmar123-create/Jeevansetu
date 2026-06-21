from uuid import UUID
from pydantic import BaseModel


class EmergencyContactBase(BaseModel):
    name: str
    phone: str
    relationship: str


class EmergencyContactCreate(EmergencyContactBase):
    pass


class EmergencyContactUpdate(EmergencyContactBase):
    name: str | None = None
    phone: str | None = None
    relationship: str | None = None


class EmergencyContactResponse(EmergencyContactBase):
    id: UUID
    user_id: UUID

    class Config:
        from_attributes = True
