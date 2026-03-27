"""
PACTA Backend Configuration
"""
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # ============================================
    # FastAPI Configuration
    # ============================================
    environment: str = "development"
    debug: bool = True
    app_name: str = "PACTA API"
    app_version: str = "2.0.0"
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"

    # ============================================
    # API Configuration
    # ============================================
    api_v1_str: str = "/api/v1"
    api_prefix: str = "/api"

    # ============================================
    # Database Configuration
    # ============================================
    database_url: str = "postgresql+asyncpg://pacta:pacta_dev_password@localhost:5432/pacta"
    database_echo: bool = False

    # ============================================
    # JWT Configuration
    # ============================================
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    jwt_algorithm: str = "HS256"

    # ============================================
    # Redis Configuration
    # ============================================
    redis_url: str = "redis://localhost:6379/0"
    redis_expiry_seconds: int = 3600

    # ============================================
    # MinIO/S3 Configuration
    # ============================================
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin_password"
    minio_bucket: str = "pacta-documents"
    minio_secure: bool = False

    # ============================================
    # CORS Configuration
    # ============================================
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5000",
        "http://localhost:8080",
    ]
    cors_credentials: bool = True
    cors_methods: list[str] = ["*"]
    cors_headers: list[str] = ["*"]

    # ============================================
    # Rate Limiting
    # ============================================
    rate_limit_enabled: bool = True
    rate_limit_requests_per_minute: int = 60

    # ============================================
    # Logging
    # ============================================
    log_level: str = "INFO"
    log_format: str = "json"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
