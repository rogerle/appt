from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置管理"""
    
    # 环境设置
    FASTAPI_ENV: str = "development"
    
    # PostgreSQL 数据库配置
    DATABASE_URL: str = "postgresql://appt_user:appt_password_2026@localhost:5432/appt"
    
    # JWT 认证配置
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # CORS 配置
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost"]
    
    # API 版本
    API_V1_PREFIX: str = "/api/v1"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """获取缓存的配置实例"""
    return Settings()
