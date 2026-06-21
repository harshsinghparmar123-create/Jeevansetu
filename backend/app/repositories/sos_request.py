from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.sos_request import SOSRequest
from app.repositories.base import BaseRepository


class SOSRequestRepository(BaseRepository[SOSRequest]):
    def __init__(self, db: AsyncSession):
        super().__init__(SOSRequest, db)

    async def get_active_requests(self) -> List[SOSRequest]:
        query = select(self.model).where(self.model.status == "active").order_by(self.model.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_user(self, user_id: str) -> List[SOSRequest]:
        import uuid
        uid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        query = select(self.model).where(self.model.user_id == uid).order_by(self.model.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())
