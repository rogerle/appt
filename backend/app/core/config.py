"""
Application Configuration Module

Uses pydantic-settings to load and validate environment variables.
All configuration values are typed and validated at startup.
"""

from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Ignore unknown variables to avoid crashes
    )

    # Environment
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # CORS (Cross-Origin Resource Sharing)
    CORS_ORIGINS: List[str] = ["*"]  # Default to allow all for development
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # Admin settings (for first-time setup) 
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin1234567890"  # Short enough for bcrypt
    
    # Logging
    LOG_LEVEL: str = "INFO"

    def validate(self):
        """Validate critical configuration values."""
        errors = []
        
        if self.SECRET_KEY == "change_this_to_a_random_512bit_key_in_production":
            errors.append("SECRET_KEY is using default value - CRITICAL SECURITY RISK!")
        
        if "*" in self.CORS_ORIGINS and len(self.CORS_ORIGINS) == 1:
            # Warning, not error - common for development
            pass
        
        return errors


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Returns:
        Settings: Cached settings instance loaded from environment variables
    
    Example:
        >>> settings = get_settings()
        >>> print(settings.DATABASE_URL)
    """
    return Settings()


# Export default instance for convenience
settings = get_settings()
