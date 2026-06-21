from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.live_location import LiveLocation
from app.repositories.base import BaseRepository


class LiveLocationRepository(BaseRepository[LiveLocation]):
    def __init__(self, db: AsyncSession):
        super().__init__(LiveLocation, db)

    async def get_by_user(self, user_id: str) -> Optional[LiveLocation]:
        import uuid
        uid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        query = select(self.model).where(self.model.user_id == uid)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
