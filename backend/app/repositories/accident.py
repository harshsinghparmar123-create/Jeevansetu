from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.accident import Accident
from app.repositories.base import BaseRepository


class AccidentRepository(BaseRepository[Accident]):
    def __init__(self, db: AsyncSession):
        super().__init__(Accident, db)

    async def get_by_user(self, user_id: str) -> List[Accident]:
        import uuid
        uid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        query = select(self.model).where(self.model.user_id == uid).order_by(self.model.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())
