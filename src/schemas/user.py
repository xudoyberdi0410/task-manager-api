from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    """Базовая модель пользователя"""

    email: EmailStr
    username: str


class UserCreate(BaseModel):
    """Схема для создания пользователя"""

    email: EmailStr
    username: str
    password: str


class UserUpdate(BaseModel):
    """Схема для обновления пользователя"""

    email: EmailStr | None = None
    username: str | None = None
    password: str | None = None


class UserResponse(UserBase):
    """Схема для ответа с данными пользователя"""

    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserBase):
    """Модель пользователя в базе данных, включает хешированный пароль"""

    user_id: int
    hashed_password: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserList(BaseModel):
    """Схема для списка пользователей"""

    users: list[UserResponse]
    total: int
    page: int
    per_page: int
