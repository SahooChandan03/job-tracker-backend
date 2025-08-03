from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import EmailStr
import secrets


class Settings(BaseSettings):
    # Project Info
    PROJECT_NAME: str = "Job Tracker Service"
    VERSION: str = "1.0.0"

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: Optional[str] = None
    REDIS_HOST: str = "54.81.124.151"  # Direct IP address
    REDIS_PORT: int = 13014
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = "RkS933CNSoJjJue9CyYrehqHQKfvvidH"
    REDIS_USERNAME: str = "default"

    # JWT
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SECRET_KEY: str = "your-super-secret-flask-key-change-in-production"

    # Flask
    FLASK_ENV: str = "development"
    FLASK_DEBUG: bool = True

    # Email (Optional - for future use)
    MAILGUN_DOMAIN: Optional[str] = None
    MAILGUN_API_KEY: Optional[str] = None
    SMTP_TLS: bool = True
    SMTP_PORT: int = 587
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[EmailStr] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_KEY: Optional[str] = None
    FROM_EMAIL: Optional[EmailStr] = None

    # OTP
    OTP_EXPIRY_SECONDS: int = 300

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"  # Allow extra fields from .env
    )


settings = Settings()
