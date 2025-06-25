"""
API маршруты для работы с задачами.
Обрабатывает HTTP запросы для CRUD операций с задачами.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.database import get_db
from src.auth.jwt import get_current_user
from src.schemas.task import (
    TaskCreate, TaskUpdate, TaskResponse, TaskList, TaskFilter
)
from src.schemas.user import UserInDB
from src.services.task_service import TaskService
from src.models.task import StatusEnum, PriorityEnum

router = APIRouter(prefix="/tasks", tags=["tasks"])

def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    """Dependency для получения сервиса задач"""
    return TaskService(db)

@router.get("/", response_model=TaskList)
async def get_tasks(
    skip: int = Query(0, ge=0, description="Количество записей для пропуска"),
    limit: int = Query(10, ge=1, le=100, description="Максимальное количество записей"),
    status: Optional[StatusEnum] = Query(None, description="Фильтр по статусу"),
    priority: Optional[PriorityEnum] = Query(None, description="Фильтр по приоритету"),
    category_id: Optional[int] = Query(None, description="Фильтр по категории"),
    search: Optional[str] = Query(None, description="Поиск по названию и описанию"),
    current_user: UserInDB = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """Получить список задач пользователя с фильтрацией"""
    filters = TaskFilter(
        status=status,
        priority=priority,
        category_id=category_id,
        search=search
    )
    
    tasks, total = task_service.get_user_tasks(
        user_id=current_user.user_id,
        skip=skip,
        limit=limit,
        filters=filters
    )
    
    return TaskList(
        tasks=tasks,
        total=total,
        page=skip // limit + 1,
        per_page=limit
    )

@router.get("/status/{status}", response_model=TaskList)
async def get_tasks_by_status(
    status: StatusEnum,
    skip: int = Query(0, ge=0, description="Количество записей для пропуска"),
    limit: int = Query(10, ge=1, le=100, description="Максимальное количество записей"),
    current_user: UserInDB = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """Получить задачи по статусу"""
    tasks, total = task_service.get_tasks_by_status(
        user_id=current_user.user_id,
        status=status,
        skip=skip,
        limit=limit
    )
    
    return TaskList(
        tasks=tasks,
        total=total,
        page=skip // limit + 1,
        per_page=limit
    )

@router.get("/category/{category_id}", response_model=TaskList)
async def get_tasks_by_category(
    category_id: int,
    skip: int = Query(0, ge=0, description="Количество записей для пропуска"),
    limit: int = Query(10, ge=1, le=100, description="Максимальное количество записей"),
    current_user: UserInDB = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """Получить задачи по категории"""
    tasks, total = task_service.get_tasks_by_category(
        user_id=current_user.user_id,
        category_id=category_id,
        skip=skip,
        limit=limit
    )
    
    return TaskList(
        tasks=tasks,
        total=total,
        page=skip // limit + 1,
        per_page=limit
    )

@router.get("/overdue", response_model=TaskList)
async def get_overdue_tasks(
    skip: int = Query(0, ge=0, description="Количество записей для пропуска"),
    limit: int = Query(10, ge=1, le=100, description="Максимальное количество записей"),
    current_user: UserInDB = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """Получить просроченные задачи"""
    tasks, total = task_service.get_overdue_tasks(
        user_id=current_user.user_id,
        skip=skip,
        limit=limit
    )
    
    return TaskList(
        tasks=tasks,
        total=total,
        page=skip // limit + 1,
        per_page=limit
    )

@router.get("/search", response_model=TaskList)
async def search_tasks(
    q: str = Query(..., description="Поисковый запрос"),
    skip: int = Query(0, ge=0, description="Количество записей для пропуска"),
    limit: int = Query(10, ge=1, le=100, description="Максимальное количество записей"),
    current_user: UserInDB = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """Поиск задач"""
    tasks, total = task_service.search_tasks(
        user_id=current_user.user_id,
        query=q,
        skip=skip,
        limit=limit
    )
    
    return TaskList(
        tasks=tasks,
        total=total,
        page=skip // limit + 1,
        per_page=limit
    )

@router.get("/statistics")
async def get_task_statistics(
    current_user: UserInDB = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """Получить статистику задач пользователя"""
    return task_service.get_task_statistics(current_user.user_id)

# Массовые операции

class BulkStatusUpdate(BaseModel):
    task_ids: List[int]
    new_status: StatusEnum

class BulkTaskIds(BaseModel):
    task_ids: List[int]

@router.patch("/bulk/status", response_model=List[TaskResponse])
async def bulk_update_status(
    bulk_data: BulkStatusUpdate,
    current_user: UserInDB = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """Массовое обновление статуса задач"""
    tasks = task_service.bulk_update_status(bulk_data.task_ids, bulk_data.new_status, current_user.user_id)
    return tasks

@router.delete("/bulk")
async def bulk_delete_tasks(
    bulk_data: BulkTaskIds,
    current_user: UserInDB = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """Массовое удаление задач"""
    result = task_service.bulk_delete_tasks(bulk_data.task_ids, current_user.user_id)
    return result

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: UserInDB = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """Получить задачу по ID"""
    task = task_service.get_task_by_id(task_id, current_user.user_id)
    return task

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: UserInDB = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """Создать новую задачу"""
    task = task_service.create_task(task_data, current_user.user_id)
    return task

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: UserInDB = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """Обновить задачу"""
    task = task_service.update_task(task_id, task_data, current_user.user_id)
    return task

@router.patch("/{task_id}/status", response_model=TaskResponse)
async def update_task_status(
    task_id: int,
    new_status: StatusEnum,
    current_user: UserInDB = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """Обновить статус задачи"""
    task = task_service.update_task_status(task_id, new_status, current_user.user_id)
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: UserInDB = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """Удалить задачу"""
    task_service.delete_task(task_id, current_user.user_id)
