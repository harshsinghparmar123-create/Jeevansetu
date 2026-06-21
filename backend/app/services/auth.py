from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core import security
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, LoginRequest


class AuthService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)

    async def register(self, user_in: UserCreate) -> User:
        # Check if user already exists
        existing = await self.user_repo.get_by_email(user_in.email)
        if not existing:
            existing = await self.user_repo.get_by_phone(user_in.phone)

        if existing:
            raise ValueError("User with this email or phone already exists")

        # Create user
        user_dict = {
            "name": user_in.name,
            "email": user_in.email,
            "phone": user_in.phone,
            "password_hash": security.get_password_hash(user_in.password),
            "fcm_token": user_in.fcm_token,
        }
        return await self.user_repo.create(user_dict)

    async def authenticate(self, login_in: LoginRequest) -> Optional[User]:
        user = await self.user_repo.get_by_email_or_phone(login_in.email_or_phone)
        if not user:
            return None
        if not security.verify_password(login_in.password, user.password_hash):
            return None
        return user
