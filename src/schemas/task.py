from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from src.models.task import StatusEnum, PriorityEnum

class TaskBase(BaseModel):
    """Базовая модель задачи"""
    title: str
    description: Optional[str] = None
    status: StatusEnum = StatusEnum.todo
    priority: PriorityEnum = PriorityEnum.medium
    due_date: Optional[datetime] = None
    category_id: Optional[int] = None

class TaskCreate(BaseModel):
    """Схема для создания задачи"""
    title: str
    description: Optional[str] = None
    status: StatusEnum = StatusEnum.todo
    priority: PriorityEnum = PriorityEnum.medium
    due_date: Optional[datetime] = None
    category_id: Optional[int] = None

class TaskUpdate(BaseModel):
    """Схема для обновления задачи"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[StatusEnum] = None
    priority: Optional[PriorityEnum] = None
    due_date: Optional[datetime] = None
    category_id: Optional[int] = None

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

class TaskFilter(BaseModel):
    """Схема для фильтрации задач"""
    status: Optional[StatusEnum] = None
    priority: Optional[PriorityEnum] = None
    category_id: Optional[int] = None
    due_date_from: Optional[datetime] = None
    due_date_to: Optional[datetime] = None
    search: Optional[str] = None
