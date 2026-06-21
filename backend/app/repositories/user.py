from typing import Optional
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> Optional[User]:
        query = select(self.model).where(self.model.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_phone(self, phone: str) -> Optional[User]:
        query = select(self.model).where(self.model.phone == phone)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_email_or_phone(self, login_str: str) -> Optional[User]:
        query = select(self.model).where(
            or_(self.model.email == login_str, self.model.phone == login_str)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
