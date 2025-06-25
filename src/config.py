import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
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
    secret_key: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS settings
    allowed_origins: str = '["http://localhost:3000", "http://localhost:8080"]'
    

# Create settings instance
settings = Settings()
