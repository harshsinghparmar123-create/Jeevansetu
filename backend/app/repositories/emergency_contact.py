from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.emergency_contact import EmergencyContact
from app.repositories.base import BaseRepository


class EmergencyContactRepository(BaseRepository[EmergencyContact]):
    def __init__(self, db: AsyncSession):
        super().__init__(EmergencyContact, db)

    async def get_by_user(self, user_id: str) -> List[EmergencyContact]:
        import uuid
        uid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        query = select(self.model).where(self.model.user_id == uid)
        result = await self.db.execute(query)
        return list(result.scalars().all())
