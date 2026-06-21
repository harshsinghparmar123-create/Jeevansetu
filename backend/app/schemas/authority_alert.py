from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class AuthorityAlertBase(BaseModel):
    accident_id: UUID
    authority_type: str  # Police, Fire, Medical


class AuthorityAlertCreate(AuthorityAlertBase):
    pass


class AuthorityAlertUpdate(BaseModel):
    status: str


class AuthorityAlertResponse(AuthorityAlertBase):
    id: UUID
    status: str
    sent_at: datetime

    class Config:
        from_attributes = True
