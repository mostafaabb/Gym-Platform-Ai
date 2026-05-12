import os
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Core
    APP_NAME: str = "GymFlow AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, validation_alias="DEBUG")
    ENVIRONMENT: str = Field(default="development", validation_alias="ENVIRONMENT")

    # Server
    API_V1_STR: str = "/api/v1"
    SERVER_HOST: str = Field(default="0.0.0.0", validation_alias="SERVER_HOST")
    SERVER_PORT: int = Field(default=8000, validation_alias="SERVER_PORT")
    BACKEND_CORS_ORIGINS: list[str] = Field(default=["http://localhost:3000", "http://localhost:8080"], validation_alias="BACKEND_CORS_ORIGINS")

    # Database
    DATABASE_URL: str = Field(default="postgresql://gymflow:password@localhost:5432/gymflow", validation_alias="DATABASE_URL")
    DATABASE_ECHO: bool = Field(default=False, validation_alias="DATABASE_ECHO")
    DATABASE_POOL_SIZE: int = Field(default=20, validation_alias="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=10, validation_alias="DATABASE_MAX_OVERFLOW")

    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", validation_alias="REDIS_URL")
    REDIS_CACHE_TTL: int = Field(default=3600, validation_alias="REDIS_CACHE_TTL")

    # JWT
    SECRET_KEY: str = Field(default="dev-secret-key-change-in-production", validation_alias="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Security
    BCRYPT_ROUNDS: int = 12
    PASSWORD_MIN_LENGTH: int = 8
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 15

    # Email (for notifications, password reset)
    SMTP_HOST: str = Field(default="smtp.gmail.com", validation_alias="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, validation_alias="SMTP_PORT")
    SMTP_USER: str = Field(default="", validation_alias="SMTP_USER")
    SMTP_PASSWORD: str = Field(default="", validation_alias="SMTP_PASSWORD")
    EMAILS_FROM_EMAIL: str = Field(default="noreply@gymflowai.com", validation_alias="EMAILS_FROM_EMAIL")
    EMAILS_FROM_NAME: str = "GymFlow AI"

    # AI/OpenAI
    OPENAI_API_KEY: str = Field(default="", validation_alias="OPENAI_API_KEY")
    OPENAI_MODEL: str = "gpt-4-turbo"
    OPENAI_MODEL_FALLBACK: str = "gpt-3.5-turbo"
    WHISPER_MODEL: str = "whisper-1"

    # Stripe (for payments)
    STRIPE_API_KEY: str = Field(default="", validation_alias="STRIPE_API_KEY")
    STRIPE_WEBHOOK_SECRET: str = Field(default="", validation_alias="STRIPE_WEBHOOK_SECRET")

    # AWS S3 (for file uploads)
    AWS_ACCESS_KEY_ID: str = Field(default="", validation_alias="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = Field(default="", validation_alias="AWS_SECRET_ACCESS_KEY")
    AWS_S3_BUCKET_NAME: str = Field(default="gymflow-uploads", validation_alias="AWS_S3_BUCKET_NAME")
    AWS_S3_REGION: str = Field(default="us-east-1", validation_alias="AWS_S3_REGION")

    # Feature Flags
    ENABLE_STRIPE: bool = False
    ENABLE_AWS_S3: bool = False
    ENABLE_AI_FEATURES: bool = True
    ENABLE_POSE_DETECTION: bool = True
    ENABLE_WEBSOCKETS: bool = True

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, value):
        if isinstance(value, str):
            return value.lower() in {"1", "true", "yes", "on", "debug", "development"}
        return value

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
