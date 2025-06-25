from pydantic import BaseModel, ConfigDict, Field


class Token(BaseModel):
    """Модель токена для аутентификации"""

    access_token: str = Field(
        ...,
        description="JWT токен доступа",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )
    token_type: str = Field(
        default="bearer", description="Тип токена", examples=["bearer"]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiZXhwIjoxNjQwOTk1MjAwfQ.signature",
                    "token_type": "bearer",
                }
            ]
        }
    )


class TokenData(BaseModel):
    """Данные извлеченные из токена"""

    email: str | None = Field(
        None, description="Email пользователя из токена", examples=["user@example.com"]
    )


class LoginRequest(BaseModel):
    """Схема для запроса аутентификации"""

    username: str = Field(
        ...,
        description="Имя пользователя или email",
        examples=["johndoe", "user@example.com"],
    )
    password: str = Field(
        ..., description="Пароль пользователя", examples=["securePassword123"]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"username": "johndoe", "password": "securePassword123"},
                {"username": "user@example.com", "password": "myPassword!"},
            ]
        }
    )
