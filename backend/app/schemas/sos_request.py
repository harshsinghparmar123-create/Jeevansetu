from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class SOSRequestBase(BaseModel):
    accident_id: UUID | None = None


class SOSRequestCreate(SOSRequestBase):
    pass


class SOSRequestUpdate(BaseModel):
    status: str


class SOSRequestResponse(BaseModel):
    id: UUID
    user_id: UUID
    accident_id: UUID | None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
