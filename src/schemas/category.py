from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    """Базовая модель категории"""

    title: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Название категории",
        examples=["Работа", "Личное", "Покупки", "Здоровье"],
    )


class CategoryCreate(BaseModel):
    """Схема для создания категории"""

    title: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Название новой категории",
        examples=["Работа", "Проекты", "Домашние дела"],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"title": "Работа"},
                {"title": "Личные проекты"},
                {"title": "Покупки"},
            ]
        }
    )


class CategoryUpdate(BaseModel):
    """Схема для обновления категории"""

    title: str | None = Field(
        None,
        min_length=1,
        max_length=100,
        description="Новое название категории",
        examples=["Обновленная категория"],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"title": "Обновленное название"},
                {"title": "Новая категория"},
            ]
        }
    )


class CategoryResponse(CategoryBase):
    """Схема для ответа с данными категории"""

    category_id: int = Field(
        ..., description="Уникальный идентификатор категории", examples=[1, 2, 3]
    )
    user_id: int = Field(
        ..., description="ID пользователя, владельца категории", examples=[1, 2, 3]
    )
    created_at: datetime = Field(
        ...,
        description="Дата и время создания категории",
        examples=["2025-06-25T10:00:00Z"],
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
                    "category_id": 1,
                    "user_id": 1,
                    "title": "Работа",
                    "created_at": "2025-06-25T10:00:00Z",
                    "updated_at": "2025-06-25T15:30:00Z",
                }
            ]
        },
    )


class CategoryInDB(CategoryBase):
    """Модель категории в базе данных"""

    category_id: int = Field(..., description="Уникальный идентификатор категории")
    user_id: int = Field(..., description="ID пользователя, владельца категории")
    created_at: datetime = Field(..., description="Дата и время создания")
    updated_at: datetime = Field(..., description="Дата и время последнего обновления")

    model_config = ConfigDict(from_attributes=True)


class CategoryList(BaseModel):
    """Схема для списка категорий с пагинацией"""

    categories: list[CategoryResponse] = Field(..., description="Список категорий")
    total: int = Field(
        ..., description="Общее количество категорий", examples=[5, 10, 0]
    )
    page: int = Field(..., description="Текущая страница", examples=[1, 2, 3])
    per_page: int = Field(
        ..., description="Количество категорий на странице", examples=[10, 20, 50]
    )
