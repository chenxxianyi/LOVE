"""
Core configuration module.
"""
import os
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    API_PREFIX: str = "/api/v1"
    APP_PORT: int = 8000

    # Database
    DATABASE_URL: str = "mysql+pymysql://root:123456@127.0.0.1:3306/love_memory"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:5174"

    # File uploads
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 10

    # Public URLs
    PUBLIC_BASE_URL: str = "http://localhost:8000"
    FRONTEND_BASE_URL: str = "http://localhost:5174"

    # Security
    PASSWORD_SALT: str = "love_memory_dev_salt_change_in_production"
    ACCESS_TOKEN_TTL_MINUTES: int = 120
    REFRESH_TOKEN_TTL_DAYS: int = 30
    AES_SECRET_KEY: str = "love_memory_aes_key_32bytes_xx"

    # Logging
    LOG_LEVEL: str = "INFO"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string into a list."""
        if not self.CORS_ORIGINS:
            return []
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def upload_dir_path(self) -> Path:
        """Get absolute path to uploads directory."""
        base_dir = Path(__file__).parent.parent.parent.parent.resolve()
        return base_dir / self.UPLOAD_DIR

    @property
    def max_upload_size_bytes(self) -> int:
        """Get max upload size in bytes."""
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()