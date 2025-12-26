from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "Mythweaver API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # Database (Supabase)
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/postgres"
    
    # Supabase
    SUPABASE_URL: str = "https://your-project.supabase.co"
    SUPABASE_ANON_KEY: str = "your-anon-key"
    
    # Redis (optional for MVP)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # AI APIs
    OPENAI_API_KEY: Optional[str] = None
    MODEL_NAME: str = "gpt-4o-mini"
    
    # Storyfire Economics (Mythweaver-specific)
    STORYFIRE_FREE_DAILY: int = 40
    STORYFIRE_COST_PER_ACTION: int = 2
    
    # CORS Settings
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8080,http://localhost:5173"
    
    # Cache TTLs (in seconds)
    CACHE_TTL_SESSION: int = 3600  # 1 hour
    CACHE_TTL_AI_RESPONSE: int = 300  # 5 minutes  
    CACHE_TTL_CHARACTER: int = 1800  # 30 minutes
    CACHE_TTL_CAMPAIGN: int = 86400  # 24 hours
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()