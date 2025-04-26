# File: backend/services/auth_service/src/core/config.py
import os
from pydantic_settings import BaseSettings  # Changed from pydantic import BaseSettings


class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "Auth Service"
    API_VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # JWT Settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "YOUR_JWT_SECRET_KEY")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@auth-db/auth_db")

    # OAuth
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8001/auth/google")

    # CORS
    ALLOWED_ORIGINS: list = ["*"]  # In production, specify actual origins

    # Session
    SESSION_SECRET: str = os.getenv("SESSION_SECRET", "SESSION_SECRET_KEY")

    class Config:
        env_file = ".env"


# Create settings object
settings = Settings()