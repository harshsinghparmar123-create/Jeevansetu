import os
from typing import List
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    PROJECT_NAME: str = "Golden Minute AI"
    API_STR: str = "/api"

    # Security
    SECRET_KEY: str = "supersecretjwtkeythatisproductionreadyandlongenough321"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS Origins (JSON list or comma separated strings)
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    # Databases
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/golden_minute"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Firebase
    FIREBASE_CREDENTIALS_PATH: str = "/workspace/firebase-key.json"

    # AI Model
    MODEL_PATH: str = "app/ai/model.joblib"


settings = Settings()
