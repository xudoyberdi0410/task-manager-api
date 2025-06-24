import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Environment
    environment: str = "development"
    debug: bool = False
    
    # Database settings
    database_url: str = "postgresql://postgres:password@localhost:5432/taskmanager"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "taskmanager"
    db_user: str = "postgres"
    db_password: str = "password"
    
    # Redis settings
    redis_url: str = "redis://localhost:6379/0"
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Security settings
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS settings
    allowed_origins: str = '["http://localhost:3000", "http://localhost:8080"]'
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields from .env


# Create settings instance
settings = Settings()
