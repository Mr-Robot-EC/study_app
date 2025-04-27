# File: backend/services/pdf_service/src/core/config.py
import os
from pydantic_settings import BaseSettings  # Changed from pydantic import BaseSettings


class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "PDF Service"
    API_VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "YOUR_JWT_SECRET_KEY")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@pdf-db/pdf_db")

    # CORS
    ALLOWED_ORIGINS: list = ["*"]  # In production, specify actual origins

    class Config:
        env_file = ".env"


# Create settings object
settings = Settings()