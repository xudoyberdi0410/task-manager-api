from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.models.task import PriorityEnum, StatusEnum


class TaskBase(BaseModel):
    """Базовая модель задачи"""

    title: str = Field(
        ...,
        description="Название задачи",
        examples=["Завершить проект", "Купить продукты", "Написать отчет"],
    )
    description: str | None = Field(
        None,
        description="Подробное описание задачи",
        examples=["Завершить разработку API для управления задачами", None],
    )
    status: StatusEnum = Field(
        default=StatusEnum.todo, description="Статус выполнения задачи"
    )
    priority: PriorityEnum = Field(
        default=PriorityEnum.medium, description="Приоритет задачи"
    )
    due_date: datetime | None = Field(
        None,
        description="Срок выполнения задачи",
        examples=["2025-12-31T23:59:59Z", None],
    )
    category_id: int | None = Field(
        None, description="ID категории задачи", examples=[1, 2, None]
    )


class TaskCreate(BaseModel):
    """Схема для создания задачи"""

    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Название задачи",
        examples=["Изучить FastAPI", "Подготовить презентацию"],
    )
    description: str | None = Field(
        None,
        max_length=1000,
        description="Подробное описание задачи",
        examples=["Изучить документацию FastAPI и создать простое приложение", None],
    )
    status: StatusEnum = Field(
        default=StatusEnum.todo, description="Статус выполнения задачи"
    )
    priority: PriorityEnum = Field(
        default=PriorityEnum.medium, description="Приоритет задачи"
    )
    due_date: datetime | None = Field(
        None, description="Срок выполнения задачи", examples=["2025-12-31T23:59:59Z"]
    )
    category_id: int | None = Field(
        None, description="ID категории задачи", examples=[1, 2]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "title": "Изучить FastAPI",
                    "description": "Изучить документацию и создать простое приложение",
                    "status": "todo",
                    "priority": "high",
                    "due_date": "2025-12-31T23:59:59Z",
                    "category_id": 1,
                },
                {
                    "title": "Купить продукты",
                    "description": "Молоко, хлеб, яйца",
                    "status": "todo",
                    "priority": "low",
                    "due_date": None,
                    "category_id": 2,
                },
            ]
        }
    )


class TaskUpdate(BaseModel):
    """Схема для обновления задачи"""

    title: str | None = Field(
        None,
        min_length=1,
        max_length=200,
        description="Новое название задачи",
        examples=["Обновленное название задачи"],
    )
    description: str | None = Field(
        None,
        max_length=1000,
        description="Новое описание задачи",
        examples=["Обновленное описание задачи"],
    )
    status: StatusEnum | None = Field(None, description="Новый статус задачи")
    priority: PriorityEnum | None = Field(None, description="Новый приоритет задачи")
    due_date: datetime | None = Field(
        None, description="Новый срок выполнения", examples=["2025-12-31T23:59:59Z"]
    )
    category_id: int | None = Field(
        None, description="Новый ID категории", examples=[1, 2]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"title": "Обновленная задача", "status": "in_progress"},
                {
                    "description": "Обновленное описание",
                    "priority": "high",
                    "due_date": "2025-12-31T23:59:59Z",
                },
            ]
        }
    )


class TaskResponse(TaskBase):
    """Схема для ответа с данными задачи"""

    task_id: int = Field(
        ..., description="Уникальный идентификатор задачи", examples=[1, 42, 123]
    )
    user_id: int = Field(
        ..., description="ID пользователя, владельца задачи", examples=[1, 2, 3]
    )
    created_at: datetime = Field(
        ...,
        description="Дата и время создания задачи",
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
                    "task_id": 1,
                    "user_id": 1,
                    "title": "Изучить FastAPI",
                    "description": "Изучить документацию и создать приложение",
                    "status": "in_progress",
                    "priority": "high",
                    "due_date": "2025-12-31T23:59:59Z",
                    "category_id": 1,
                    "created_at": "2025-06-25T10:00:00Z",
                    "updated_at": "2025-06-25T15:30:00Z",
                }
            ]
        },
    )


class TaskInDB(TaskBase):
    """Модель задачи в базе данных"""

    task_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskList(BaseModel):
    """Схема для списка задач с пагинацией"""

    tasks: list[TaskResponse] = Field(..., description="Список задач")
    total: int = Field(..., description="Общее количество задач", examples=[25, 100, 0])
    page: int = Field(..., description="Текущая страница", examples=[1, 2, 3])
    per_page: int = Field(
        ..., description="Количество задач на странице", examples=[10, 20, 50]
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "tasks": [
                        {
                            "task_id": 1,
                            "user_id": 1,
                            "title": "Изучить FastAPI",
                            "description": "Изучить документацию и создать приложение",
                            "status": "in_progress",
                            "priority": "high",
                            "due_date": "2025-12-31T23:59:59Z",
                            "category_id": 1,
                            "created_at": "2025-06-25T10:00:00Z",
                            "updated_at": "2025-06-25T15:30:00Z",
                        }
                    ],
                    "total": 25,
                    "page": 1,
                    "per_page": 10,
                }
            ]
        },
    )


class TaskFilter(BaseModel):
    """Схема для фильтрации задач"""

    status: StatusEnum | None = Field(None, description="Фильтр по статусу задачи")
    priority: PriorityEnum | None = Field(
        None, description="Фильтр по приоритету задачи"
    )
    category_id: int | None = Field(
        None, description="Фильтр по ID категории", examples=[1, 2, 3]
    )
    due_date_from: datetime | None = Field(
        None,
        description="Фильтр задач с крайним сроком от указанной даты",
        examples=["2025-06-01T00:00:00Z"],
    )
    due_date_to: datetime | None = Field(
        None,
        description="Фильтр задач с крайним сроком до указанной даты",
        examples=["2025-12-31T23:59:59Z"],
    )
    search: str | None = Field(
        None,
        description="Поиск по названию и описанию задачи",
        examples=["FastAPI", "проект", "купить"],
    )
