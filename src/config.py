import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Проверяем, запущены ли мы в тестовом режиме
TESTING = os.getenv("TESTING", "false").lower() == "true"

# Список обязательных переменных окружения (кроме тестового режима)
env_required_vars = [
    "ENVIRONMENT",
    "DEBUG",
    "DATABASE_URL",
    "DB_HOST",
    "DB_PORT",
    "DB_NAME",
    "DB_USER",
    "DB_PASSWORD",
    "API_HOST",
    "API_PORT",
    "SECRET_KEY",
    "ALGORITHM",
    "ACCESS_TOKEN_EXPIRE_MINUTES",
    "ALLOWED_ORIGINS",
]

# В тестовом режиме не проверяем обязательные переменные
if not TESTING:
    missing_vars = [var for var in env_required_vars if os.getenv(var) is None]
    if missing_vars:
        raise RuntimeError(
            f"Missing required environment variables in .env: {', '.join(missing_vars)}"
        )


class Settings(BaseSettings):
    """Application settings"""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Environment
    environment: str = Field(
        default="testing" if TESTING else "development", validation_alias="ENVIRONMENT"
    )
    debug: bool = Field(default=True if TESTING else False, validation_alias="DEBUG")

    # Database settings
    database_url: str = Field(
        default="sqlite:///:memory:" if TESTING else "", validation_alias="DATABASE_URL"
    )
    db_host: str = Field(
        default="localhost" if TESTING else "", validation_alias="DB_HOST"
    )
    db_port: int = Field(default=5432 if TESTING else 0, validation_alias="DB_PORT")
    db_name: str = Field(
        default="test_db" if TESTING else "", validation_alias="DB_NAME"
    )
    db_user: str = Field(
        default="test_user" if TESTING else "", validation_alias="DB_USER"
    )
    db_password: str = Field(
        default="test_password" if TESTING else "", validation_alias="DB_PASSWORD"
    )

    # API settings
    api_host: str = Field(
        default="localhost" if TESTING else "", validation_alias="API_HOST"
    )
    api_port: int = Field(default=8000 if TESTING else 0, validation_alias="API_PORT")

    # Security settings
    secret_key: str = Field(
        default="test-secret-key-for-testing-only" if TESTING else "",
        validation_alias="SECRET_KEY",
    )
    algorithm: str = Field(
        default="HS256" if TESTING else "", validation_alias="ALGORITHM"
    )
    access_token_expire_minutes: int = Field(
        default=30 if TESTING else 0, validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    # CORS settings
    allowed_origins: str = Field(
        default="*" if TESTING else "", validation_alias="ALLOWED_ORIGINS"
    )


# Create settings instance
settings = Settings()
