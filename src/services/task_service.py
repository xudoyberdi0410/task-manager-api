"""
Бизнес-логика для работы с задачами.
Сервисный слой между API и репозиторием.
"""

from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.models.task import StatusEnum, Task
from src.repositories.category_repository import CategoryRepository
from src.repositories.task_repository import TaskRepository
from src.schemas.task import TaskCreate, TaskFilter, TaskResponse, TaskUpdate


class TaskService:
    """Сервис для работы с задачами"""

    def __init__(self, db: Session):
        self.task_repo = TaskRepository(db)
        self.category_repo = CategoryRepository(db)

    def get_task_by_id(self, task_id: int, user_id: int) -> Task | None:
        """Получить задачу по ID"""
        task = self.task_repo.get_by_id(task_id, user_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )
        return task

    def get_user_tasks(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        filters: TaskFilter | None = None,
    ) -> tuple[list[TaskResponse], int]:
        """Получить список задач пользователя с фильтрацией"""
        if filters:
            tasks, total = self.task_repo.get_all_by_user(
                user_id=user_id,
                skip=skip,
                limit=limit,
                status=filters.status,
                priority=filters.priority,
                category_id=filters.category_id,
                due_date_from=filters.due_date_from,
                due_date_to=filters.due_date_to,
                search=filters.search,
            )
        else:
            tasks, total = self.task_repo.get_all_by_user(user_id, skip, limit)

        # Convert Task models to TaskResponse
        task_responses = [TaskResponse.model_validate(task) for task in tasks]
        return task_responses, total

    def get_tasks_by_status(
        self, user_id: int, status: StatusEnum, skip: int = 0, limit: int = 100
    ) -> tuple[list[TaskResponse], int]:
        """Получить задачи по статусу"""
        tasks, total = self.task_repo.get_by_status(user_id, status, skip, limit)
        task_responses = [TaskResponse.model_validate(task) for task in tasks]
        return task_responses, total

    def get_tasks_by_category(
        self, user_id: int, category_id: int, skip: int = 0, limit: int = 100
    ) -> tuple[list[TaskResponse], int]:
        """Получить задачи по категории"""
        # Проверяем, что категория принадлежит пользователю
        category = self.category_repo.get_by_id(category_id, user_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )

        tasks, total = self.task_repo.get_by_category(user_id, category_id, skip, limit)
        task_responses = [TaskResponse.model_validate(task) for task in tasks]
        return task_responses, total

    def get_overdue_tasks(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> tuple[list[TaskResponse], int]:
        """Получить просроченные задачи"""
        tasks, total = self.task_repo.get_overdue_tasks(user_id, skip, limit)
        task_responses = [TaskResponse.model_validate(task) for task in tasks]
        return task_responses, total

    def search_tasks(
        self, user_id: int, query: str, skip: int = 0, limit: int = 100
    ) -> tuple[list[TaskResponse], int]:
        """Поиск задач"""
        if not query.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Search query cannot be empty",
            )

        tasks, total = self.task_repo.search_tasks(query, user_id, skip, limit)
        task_responses = [TaskResponse.model_validate(task) for task in tasks]
        return task_responses, total

    def create_task(self, task_data: TaskCreate, user_id: int) -> Task:
        """Создать новую задачу"""
        # Проверяем существование категории, если указана
        if task_data.category_id:
            category = self.category_repo.get_by_id(task_data.category_id, user_id)
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
                )

        # Проверяем корректность данных
        if not task_data.title.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task title cannot be empty",
            )

        # Создаем задачу
        return self.task_repo.create_task(
            title=task_data.title.strip(),
            description=(
                task_data.description.strip() if task_data.description else None
            ),
            status=task_data.status,
            priority=task_data.priority,
            due_date=task_data.due_date,
            category_id=task_data.category_id,
            user_id=user_id,
        )

    def update_task(self, task_id: int, task_data: TaskUpdate, user_id: int) -> Task:
        """Обновить задачу"""
        # Проверяем существование задачи
        task = self.task_repo.get_by_id(task_id, user_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )

        # Проверяем существование категории, если указана
        if task_data.category_id is not None:
            if task_data.category_id > 0:  # 0 означает убрать категорию
                category = self.category_repo.get_by_id(task_data.category_id, user_id)
                if not category:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Category not found",
                    )

        # Подготавливаем данные для обновления
        update_data: dict[str, Any] = {}
        if task_data.title is not None:
            if not task_data.title.strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Task title cannot be empty",
                )
            update_data["title"] = task_data.title.strip()

        if task_data.description is not None:
            update_data["description"] = (
                task_data.description.strip() if task_data.description else None
            )

        if task_data.status is not None:
            update_data["status"] = task_data.status

        if task_data.priority is not None:
            update_data["priority"] = task_data.priority

        if task_data.due_date is not None:
            update_data["due_date"] = task_data.due_date

        if task_data.category_id is not None:
            update_data["category_id"] = (
                task_data.category_id if task_data.category_id > 0 else None
            )

        # Обновляем задачу
        updated_task = self.task_repo.update_task(task_id, user_id, **update_data)
        if not updated_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )

        return updated_task

    def update_task_status(
        self, task_id: int, new_status: StatusEnum, user_id: int
    ) -> Task:
        """Обновить статус задачи"""
        task = self.task_repo.get_by_id(task_id, user_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )

        updated_task = self.task_repo.update_status(task_id, user_id, new_status)
        if not updated_task:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update task status",
            )

        return updated_task

    def delete_task(self, task_id: int, user_id: int) -> bool:
        """Удалить задачу"""
        task = self.task_repo.get_by_id(task_id, user_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )

        success = self.task_repo.delete_task(task_id, user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete task",
            )

        return success

    def get_task_statistics(self, user_id: int) -> dict:
        """Получить статистику задач пользователя"""
        return self.task_repo.get_task_statistics(user_id)

    def bulk_update_status(
        self, task_ids: list[int], new_status: StatusEnum, user_id: int
    ) -> list[Task]:
        """Массовое обновление статуса задач"""
        updated_tasks = []
        failed_ids = []

        for task_id in task_ids:
            try:
                task = self.task_repo.get_by_id(task_id, user_id)
                if task:
                    updated_task = self.task_repo.update_status(
                        task_id, user_id, new_status
                    )
                    if updated_task:
                        updated_tasks.append(updated_task)
                    else:
                        failed_ids.append(task_id)
                else:
                    failed_ids.append(task_id)
            except Exception:
                failed_ids.append(task_id)

        if failed_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to update tasks with IDs: {failed_ids}",
            )

        return updated_tasks

    def bulk_delete_tasks(self, task_ids: list[int], user_id: int) -> dict:
        """Массовое удаление задач"""
        deleted_count = 0
        failed_ids = []

        for task_id in task_ids:
            try:
                task = self.task_repo.get_by_id(task_id, user_id)
                if task:
                    success = self.task_repo.delete_task(task_id, user_id)
                    if success:
                        deleted_count += 1
                    else:
                        failed_ids.append(task_id)
                else:
                    failed_ids.append(task_id)
            except Exception:
                failed_ids.append(task_id)

        return {
            "deleted_count": deleted_count,
            "failed_ids": failed_ids,
            "total_requested": len(task_ids),
        }
