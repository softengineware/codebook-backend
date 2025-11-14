"""Application configuration using Pydantic Settings."""
import os
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "Construction Codebook AI Backend"
    VERSION: str = "0.1.0"
    APP_ENV: str = "development"
    PORT: int = 8000
    API_V1_PREFIX: str = "/v1"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Supabase
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str

    # Pinecone
    PINECONE_API_KEY: str
    PINECONE_INDEX_NAME: str
    PINECONE_ENVIRONMENT: str = "us-east-1"

    # LLM
    LLM_API_KEY: str
    LLM_MODEL_NAME: str = "gpt-4o"
    LLM_PROVIDER: str = "openai"  # or "anthropic"

    # Embeddings
    EMBEDDING_MODEL_NAME: str = "text-embedding-3-large"
    EMBEDDING_DIMENSIONS: int = 3072  # 1536 for small, 3072 for large

    # Redis (optional)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None

    # Authentication
    API_KEY_SIGNING_SECRET: str = "change-me-in-production"
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Rate Limiting
    RATE_LIMIT_STANDARD: int = 100  # requests per minute
    RATE_LIMIT_LLM: int = 10  # requests per hour

    # File Upload
    MAX_FILE_SIZE_MB: int = 10
    MAX_ROWS_PER_UPLOAD: int = 10000
    ALLOWED_MIME_TYPES: list[str] = [
        "text/csv",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ]

    # Job Processing
    JOB_POLL_INTERVAL_SECONDS: int = 5
    JOB_TIMEOUT_SECONDS: int = 300
    JOB_MAX_RETRIES: int = 3

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # or "console"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


# Global settings instance
settings = Settings()
