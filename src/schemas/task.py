from datetime import datetime

from pydantic import BaseModel, ConfigDict

from src.models.task import PriorityEnum, StatusEnum


class TaskBase(BaseModel):
    """Базовая модель задачи"""

    title: str
    description: str | None = None
    status: StatusEnum = StatusEnum.todo
    priority: PriorityEnum = PriorityEnum.medium
    due_date: datetime | None = None
    category_id: int | None = None


class TaskCreate(BaseModel):
    """Схема для создания задачи"""

    title: str
    description: str | None = None
    status: StatusEnum = StatusEnum.todo
    priority: PriorityEnum = PriorityEnum.medium
    due_date: datetime | None = None
    category_id: int | None = None


class TaskUpdate(BaseModel):
    """Схема для обновления задачи"""

    title: str | None = None
    description: str | None = None
    status: StatusEnum | None = None
    priority: PriorityEnum | None = None
    due_date: datetime | None = None
    category_id: int | None = None


class TaskResponse(TaskBase):
    """Схема для ответа с данными задачи"""

    task_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskInDB(TaskBase):
    """Модель задачи в базе данных"""

    task_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskList(BaseModel):
    """Схема для списка задач"""

    tasks: list[TaskResponse]
    total: int
    page: int
    per_page: int

    model_config = ConfigDict(from_attributes=True)


class TaskFilter(BaseModel):
    """Схема для фильтрации задач"""

    status: StatusEnum | None = None
    priority: PriorityEnum | None = None
    category_id: int | None = None
    due_date_from: datetime | None = None
    due_date_to: datetime | None = None
    search: str | None = None
