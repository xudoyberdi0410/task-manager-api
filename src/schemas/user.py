from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Базовая модель пользователя"""

    email: EmailStr = Field(
        ...,
        description="Email адрес пользователя",
        examples=["user@example.com", "john.doe@gmail.com"],
    )
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Имя пользователя",
        examples=["johndoe", "user123", "alex_smith"],
    )


class UserCreate(BaseModel):
    """Схема для создания пользователя"""

    email: EmailStr = Field(
        ...,
        description="Email адрес для регистрации",
        examples=["user@example.com", "newuser@gmail.com"],
    )
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Уникальное имя пользователя",
        examples=["johndoe", "newuser123"],
    )
    password: str = Field(
        ...,
        min_length=8,
        description="Пароль (минимум 8 символов)",
        examples=["securePassword123", "myStrongPass!"],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "email": "john.doe@example.com",
                    "username": "johndoe",
                    "password": "securePassword123",
                },
                {
                    "email": "alice@example.com",
                    "username": "alice_smith",
                    "password": "myStrongPass!",
                },
            ]
        }
    )


class UserUpdate(BaseModel):
    """Схема для обновления пользователя"""

    email: EmailStr | None = Field(
        None, description="Новый email адрес", examples=["newemail@example.com"]
    )
    username: str | None = Field(
        None,
        min_length=3,
        max_length=50,
        description="Новое имя пользователя",
        examples=["newusername"],
    )
    password: str | None = Field(
        None,
        min_length=8,
        description="Новый пароль (минимум 8 символов)",
        examples=["newSecurePassword123"],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"username": "updated_username"},
                {"email": "updated@example.com", "password": "newPassword123"},
            ]
        }
    )


class UserResponse(UserBase):
    """Схема для ответа с данными пользователя"""

    user_id: int = Field(
        ..., description="Уникальный идентификатор пользователя", examples=[1, 42, 123]
    )
    created_at: datetime = Field(
        ..., description="Дата и время регистрации", examples=["2025-06-25T10:00:00Z"]
    )
    updated_at: datetime = Field(
        ...,
        description="Дата и время последнего обновления",
        examples=["2025-06-25T15:30:00Z"],
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "user_id": 1,
                    "email": "john.doe@example.com",
                    "username": "johndoe",
                    "created_at": "2025-06-25T10:00:00Z",
                    "updated_at": "2025-06-25T15:30:00Z",
                }
            ]
        },
    )


class UserInDB(UserBase):
    """Модель пользователя в базе данных, включает хешированный пароль"""

    user_id: int = Field(..., description="Уникальный идентификатор пользователя")
    hashed_password: str = Field(..., description="Хешированный пароль пользователя")
    created_at: datetime = Field(..., description="Дата и время регистрации")
    updated_at: datetime = Field(..., description="Дата и время последнего обновления")

    model_config = ConfigDict(from_attributes=True)


class UserList(BaseModel):
    """Схема для списка пользователей с пагинацией"""

    users: list[UserResponse] = Field(..., description="Список пользователей")
    total: int = Field(
        ..., description="Общее количество пользователей", examples=[25, 100, 0]
    )
    page: int = Field(..., description="Текущая страница", examples=[1, 2, 3])
    per_page: int = Field(
        ..., description="Количество пользователей на странице", examples=[10, 20, 50]
    )
