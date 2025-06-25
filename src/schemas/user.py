from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime

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
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None

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