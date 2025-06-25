"""
API маршруты для работы с задачами.
Обрабатывает HTTP запросы для CRUD операций с задачами.
"""

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.auth.jwt import get_current_user
from src.database import get_db
from src.models.task import PriorityEnum, StatusEnum
from src.schemas.task import TaskCreate, TaskFilter, TaskList, TaskResponse, TaskUpdate
from src.schemas.user import UserInDB
from src.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    """Dependency для получения сервиса задач"""
    return TaskService(db)


@router.get(
    "/",
    response_model=TaskList,
    summary="Получить список задач",
    description="Получить список задач пользователя с возможностью фильтрации и пагинации",
    response_description="Список задач с метаданными пагинации",
)
async def get_tasks(
    skip: int = Query(0, ge=0, description="Количество записей для пропуска"),
    limit: int = Query(10, ge=1, le=100, description="Максимальное количество записей"),
    status: StatusEnum | None = Query(None, description="Фильтр по статусу"),
    priority: PriorityEnum | None = Query(None, description="Фильтр по приоритету"),
    category_id: int | None = Query(None, description="Фильтр по категории"),
    search: str | None = Query(None, description="Поиск по названию и описанию"),
    current_user: UserInDB = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """
    ## Получить список задач пользователя

    Возвращает список задач с возможностями:
    - **Пагинация**: используйте skip и limit
    - **Фильтрация**: по статусу, приоритету, категории
    - **Поиск**: по названию и описанию задач

    ### Параметры:
    - **skip**: количество записей для пропуска (по умолчанию 0)
    - **limit**: максимальное количество записей (1-100, по умолчанию 10)
    - **status**: фильтр по статусу (todo, in_progress, done)
    - **priority**: фильтр по приоритету (low, medium, high)
    - **category_id**: ID категории для фильтрации
    - **search**: текст для поиска в названии и описании
    """
    filters = TaskFilter(
        status=status,
        priority=priority,
        category_id=category_id,
        search=search,
        due_date_from=None,
        due_date_to=None,
    )

    tasks, total = task_service.get_user_tasks(
        user_id=int(current_user.user_id), skip=skip, limit=limit, filters=filters
    )

    return TaskList(tasks=tasks, total=total, page=skip // limit + 1, per_page=limit)


@router.get(
    "/status/{status}",
    response_model=TaskList,
    summary="Получить задачи по статусу",
    description="Получить все задачи пользователя с определенным статусом",
    response_description="Список задач с указанным статусом",
)
async def get_tasks_by_status(
    status: StatusEnum,
    skip: int = Query(0, ge=0, description="Количество записей для пропуска"),
    limit: int = Query(10, ge=1, le=100, description="Максимальное количество записей"),
    current_user: UserInDB = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """
    ## Получить задачи по статусу

    Возвращает все задачи пользователя с определенным статусом.

    ### Возможные статусы:
    - **todo**: задачи к выполнению
    - **in_progress**: задачи в процессе выполнения
    - **done**: завершенные задачи
    """
    tasks, total = task_service.get_tasks_by_status(
        user_id=int(current_user.user_id), status=status, skip=skip, limit=limit
    )

    return TaskList(tasks=tasks, total=total, page=skip // limit + 1, per_page=limit)


@router.get(
    "/category/{category_id}",
    response_model=TaskList,
    summary="Получить задачи по категории",
    description="Получить все задачи пользователя из определенной категории",
    response_description="Список задач из указанной категории",
)
async def get_tasks_by_category(
    category_id: int,
    skip: int = Query(0, ge=0, description="Количество записей для пропуска"),
    limit: int = Query(10, ge=1, le=100, description="Максимальное количество записей"),
    current_user: UserInDB = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """
    ## Получить задачи по категории

    Возвращает все задачи пользователя из указанной категории.

    ### Параметры:
    - **category_id**: уникальный идентификатор категории
    """
    tasks, total = task_service.get_tasks_by_category(
        user_id=int(current_user.user_id),
        category_id=category_id,
        skip=skip,
        limit=limit,
    )

    return TaskList(tasks=tasks, total=total, page=skip // limit + 1, per_page=limit)


@router.get(
    "/overdue",
    response_model=TaskList,
    summary="Получить просроченные задачи",
    description="Получить все просроченные задачи пользователя",
    response_description="Список просроченных задач",
)
async def get_overdue_tasks(
    skip: int = Query(0, ge=0, description="Количество записей для пропуска"),
    limit: int = Query(10, ge=1, le=100, description="Максимальное количество записей"),
    current_user: UserInDB = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """
    ## Получить просроченные задачи

    Возвращает все задачи пользователя, у которых срок выполнения (due_date)
    уже прошел, но статус не равен 'done'.
    """
    tasks, total = task_service.get_overdue_tasks(
        user_id=int(current_user.user_id), skip=skip, limit=limit
    )

    return TaskList(tasks=tasks, total=total, page=skip // limit + 1, per_page=limit)


@router.get(
    "/search",
    response_model=TaskList,
    summary="Поиск задач",
    description="Поиск задач по тексту в названии и описании",
    response_description="Список найденных задач",
)
async def search_tasks(
    q: str = Query(..., description="Поисковый запрос"),
    skip: int = Query(0, ge=0, description="Количество записей для пропуска"),
    limit: int = Query(10, ge=1, le=100, description="Максимальное количество записей"),
    current_user: UserInDB = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """
    ## Поиск задач

    Выполняет полнотекстовый поиск по названию и описанию задач.

    ### Параметры:
    - **q**: поисковый запрос (обязательный)
    - **skip**: количество записей для пропуска
    - **limit**: максимальное количество записей
    """
    tasks, total = task_service.search_tasks(
        user_id=int(current_user.user_id), query=q, skip=skip, limit=limit
    )

    return TaskList(tasks=tasks, total=total, page=skip // limit + 1, per_page=limit)


@router.get(
    "/statistics",
    summary="Статистика задач",
    description="Получить статистику задач пользователя по статусам и приоритетам",
    response_description="Объект со статистикой задач",
    tags=["📊 Statistics"],
)
async def get_task_statistics(
    current_user: UserInDB = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """
    ## Статистика задач пользователя

    Возвращает подробную статистику по задачам:
    - Количество задач по статусам
    - Количество задач по приоритетам
    - Количество просроченных задач
    - Общее количество задач
    """
    return task_service.get_task_statistics(int(current_user.user_id))


# Массовые операции


class BulkStatusUpdate(BaseModel):
    """Схема для массового обновления статуса задач"""

    task_ids: list[int] = Field(
        ...,
        description="Список ID задач для обновления",
        examples=[[1, 2, 3], [42, 43]],
    )
    new_status: StatusEnum = Field(..., description="Новый статус для всех задач")


class BulkTaskIds(BaseModel):
    """Схема для массовых операций с задачами"""

    task_ids: list[int] = Field(
        ..., description="Список ID задач", examples=[[1, 2, 3], [42, 43]]
    )


@router.patch(
    "/bulk/status",
    response_model=list[TaskResponse],
    summary="Массовое обновление статуса",
    description="Обновить статус у нескольких задач одновременно",
    response_description="Список обновленных задач",
)
async def bulk_update_status(
    bulk_data: BulkStatusUpdate,
    current_user: UserInDB = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """
    ## Массовое обновление статуса задач

    Позволяет обновить статус у нескольких задач одновременно.
    Полезно для операций типа "отметить все как выполненные".

    ### Тело запроса:
    - **task_ids**: список ID задач для обновления
    - **new_status**: новый статус для всех задач
    """
    tasks = task_service.bulk_update_status(
        bulk_data.task_ids, bulk_data.new_status, int(current_user.user_id)
    )
    return tasks


@router.delete(
    "/bulk",
    summary="Массовое удаление задач",
    description="Удалить несколько задач одновременно",
    response_description="Результат операции удаления",
    status_code=status.HTTP_200_OK,
)
async def bulk_delete_tasks(
    bulk_data: BulkTaskIds,
    current_user: UserInDB = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """
    ## Массовое удаление задач

    Удаляет несколько задач одновременно.
    Операция необратима.

    ### Тело запроса:
    - **task_ids**: список ID задач для удаления
    """
    result = task_service.bulk_delete_tasks(
        bulk_data.task_ids, int(current_user.user_id)
    )
    return result


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Получить задачу",
    description="Получить подробную информацию о конкретной задаче",
    response_description="Данные задачи",
)
async def get_task(
    task_id: int,
    current_user: UserInDB = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """
    ## Получить задачу по ID

    Возвращает подробную информацию о задаче по её уникальному идентификатору.

    ### Параметры:
    - **task_id**: уникальный идентификатор задачи
    """
    task = task_service.get_task_by_id(task_id, int(current_user.user_id))
    return task


@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать задачу",
    description="Создать новую задачу для текущего пользователя",
    response_description="Созданная задача с присвоенным ID",
)
async def create_task(
    task_data: TaskCreate,
    current_user: UserInDB = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """
    ## Создать новую задачу

    Создает новую задачу для текущего пользователя.

    ### Обязательные поля:
    - **title**: название задачи

    ### Опциональные поля:
    - **description**: описание задачи
    - **status**: статус (по умолчанию "todo")
    - **priority**: приоритет (по умолчанию "medium")
    - **due_date**: срок выполнения
    - **category_id**: ID категории
    """
    task = task_service.create_task(task_data, int(current_user.user_id))
    return task


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Обновить задачу",
    description="Полное обновление задачи",
    response_description="Обновленная задача",
)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: UserInDB = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """
    ## Обновить задачу

    Обновляет данные существующей задачи. Можно обновить любые поля.

    ### Параметры:
    - **task_id**: ID задачи для обновления

    ### Поля для обновления:
    - **title**: новое название
    - **description**: новое описание
    - **status**: новый статус
    - **priority**: новый приоритет
    - **due_date**: новый срок выполнения
    - **category_id**: новая категория
    """
    task = task_service.update_task(task_id, task_data, int(current_user.user_id))
    return task


@router.patch(
    "/{task_id}/status",
    response_model=TaskResponse,
    summary="Обновить статус задачи",
    description="Быстрое обновление только статуса задачи",
    response_description="Задача с обновленным статусом",
)
async def update_task_status(
    task_id: int,
    new_status: StatusEnum,
    current_user: UserInDB = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """
    ## Обновить статус задачи

    Быстрое обновление только статуса задачи без изменения других полей.

    ### Параметры:
    - **task_id**: ID задачи
    - **new_status**: новый статус (todo, in_progress, done)
    """
    task = task_service.update_task_status(
        task_id, new_status, int(current_user.user_id)
    )
    return task


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить задачу",
    description="Удалить задачу (операция необратима)",
    response_description="Нет контента при успешном удалении",
)
async def delete_task(
    task_id: int,
    current_user: UserInDB = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """
    ## Удалить задачу

    Удаляет задачу навсегда. Операция необратима.

    ### Параметры:
    - **task_id**: ID задачи для удаления
    """
    task_service.delete_task(task_id, int(current_user.user_id))
