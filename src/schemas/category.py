from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class CategoryBase(BaseModel):
    """Базовая модель категории"""
    title: str

class CategoryCreate(BaseModel):
    """Схема для создания категории"""
    title: str

class CategoryUpdate(BaseModel):
    """Схема для обновления категории"""
    title: Optional[str] = None

class CategoryResponse(CategoryBase):
    """Схема для ответа с данными категории"""
    category_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class CategoryInDB(CategoryBase):
    """Модель категории в базе данных"""
    category_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class CategoryList(BaseModel):
    """Схема для списка категорий"""
    categories: list[CategoryResponse]
    total: int
    page: int
    per_page: int
