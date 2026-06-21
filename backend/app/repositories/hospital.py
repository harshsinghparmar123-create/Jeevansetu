from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.hospital import Hospital
from app.repositories.base import BaseRepository


class HospitalRepository(BaseRepository[Hospital]):
    def __init__(self, db: AsyncSession):
        super().__init__(Hospital, db)
