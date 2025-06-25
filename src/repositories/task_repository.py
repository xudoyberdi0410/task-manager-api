"""
Репозиторий для работы с задачами в базе данных.
Содержит все операции CRUD для модели Task.
"""
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime
from src.models.task import Task, StatusEnum, PriorityEnum


class TaskRepository:
    """Репозиторий для работы с задачами"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, task_id: int, user_id: int) -> Optional[Task]:
        """Получить задачу по ID для конкретного пользователя"""
        return (
            self.db.query(Task)
            .filter(Task.task_id == task_id, Task.user_id == user_id)
            .first()
        )
    
    def get_all_by_user(
        self, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[StatusEnum] = None,
        priority: Optional[PriorityEnum] = None,
        category_id: Optional[int] = None,
        due_date_from: Optional[datetime] = None,
        due_date_to: Optional[datetime] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Task], int]:
        """Получить список всех задач пользователя с фильтрацией и пагинацией"""
        
        # Базовый фильтр по пользователю
        filters = [Task.user_id == user_id]
        
        # Добавляем дополнительные фильтры
        if status:
            filters.append(Task.status == status)
        
        if priority:
            filters.append(Task.priority == priority)
        
        if category_id:
            filters.append(Task.category_id == category_id)
        
        if due_date_from:
            filters.append(Task.due_date >= due_date_from)
        
        if due_date_to:
            filters.append(Task.due_date <= due_date_to)
        
        if search:
            search_filter = Task.title.ilike(f"%{search}%") | Task.description.ilike(f"%{search}%")
            filters.append(search_filter)
        
        # Создаем условие фильтрации
        filter_condition = and_(*filters)
        
        # Получаем общее количество задач
        total = (
            self.db.query(func.count(Task.task_id))
            .filter(filter_condition)
            .scalar()
        )
        
        # Получаем задачи с пагинацией
        tasks = (
            self.db.query(Task)
            .filter(filter_condition)
            .order_by(Task.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        return tasks, total

    def get_by_status(self, user_id: int, status: StatusEnum, skip: int = 0, limit: int = 100) -> Tuple[List[Task], int]:
        """Получить задачи по статусу для конкретного пользователя"""
        # Получаем общее количество задач с указанным статусом
        total = (
            self.db.query(func.count(Task.task_id))
            .filter(Task.user_id == user_id, Task.status == status)
            .scalar()
        )
        
        # Получаем задачи с пагинацией
        tasks = (
            self.db.query(Task)
            .filter(Task.user_id == user_id, Task.status == status)
            .order_by(Task.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        return tasks, total

    def get_by_category(self, user_id: int, category_id: int, skip: int = 0, limit: int = 100) -> Tuple[List[Task], int]:
        """Получить задачи по категории для конкретного пользователя"""
        # Получаем общее количество задач в указанной категории
        total = (
            self.db.query(func.count(Task.task_id))
            .filter(Task.user_id == user_id, Task.category_id == category_id)
            .scalar()
        )
        
        # Получаем задачи с пагинацией
        tasks = (
            self.db.query(Task)
            .filter(Task.user_id == user_id, Task.category_id == category_id)
            .order_by(Task.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        return tasks, total

    def get_overdue_tasks(self, user_id: int, skip: int = 0, limit: int = 100) -> Tuple[List[Task], int]:
        """Получить просроченные задачи для конкретного пользователя"""
        now = datetime.utcnow()
        
        # Получаем общее количество просроченных задач
        total = (
            self.db.query(func.count(Task.task_id))
            .filter(
                Task.user_id == user_id,
                Task.due_date < now,
                Task.status != StatusEnum.done,
                Task.status != StatusEnum.archived
            )
            .scalar()
        )
        
        # Получаем просроченные задачи с пагинацией
        tasks = (
            self.db.query(Task)
            .filter(
                Task.user_id == user_id,
                Task.due_date < now,
                Task.status != StatusEnum.done,
                Task.status != StatusEnum.archived
            )
            .order_by(Task.due_date.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        return tasks, total

    def search_tasks(self, query: str, user_id: int, skip: int = 0, limit: int = 100) -> Tuple[List[Task], int]:
        """Поиск задач по названию и описанию для конкретного пользователя"""
        search_filter = (
            (Task.title.ilike(f"%{query}%") | Task.description.ilike(f"%{query}%")) & 
            (Task.user_id == user_id)
        )
        
        # Получаем общее количество найденных задач
        total = self.db.query(func.count(Task.task_id)).filter(search_filter).scalar()
        
        # Получаем задачи с пагинацией
        tasks = (
            self.db.query(Task)
            .filter(search_filter)
            .order_by(Task.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        return tasks, total
    
    def create_task(
        self, 
        title: str, 
        user_id: int,
        description: Optional[str] = None,
        status: StatusEnum = StatusEnum.todo,
        priority: PriorityEnum = PriorityEnum.medium,
        due_date: Optional[datetime] = None,
        category_id: Optional[int] = None
    ) -> Task:
        """Создать новую задачу"""
        new_task = Task(
            title=title,
            description=description,
            status=status,
            priority=priority,
            due_date=due_date,
            user_id=user_id,
            category_id=category_id
        )
        self.db.add(new_task)
        self.db.commit()
        self.db.refresh(new_task)
        return new_task
    
    def update_task(self, task_id: int, user_id: int, **kwargs) -> Optional[Task]:
        """Обновить данные задачи"""
        task = self.get_by_id(task_id, user_id)
        if not task:
            return None
        
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
        
        self.db.commit()
        self.db.refresh(task)
        return task

    def update_task_partial(
        self, 
        task_id: int, 
        user_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[StatusEnum] = None,
        priority: Optional[PriorityEnum] = None,
        due_date: Optional[datetime] = None,
        category_id: Optional[int] = None
    ) -> Optional[Task]:
        """Частичное обновление данных задачи"""
        task = self.get_by_id(task_id, user_id)
        if not task:
            return None
        
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if status is not None:
            task.status = status
        if priority is not None:
            task.priority = priority
        if due_date is not None:
            task.due_date = due_date
        if category_id is not None:
            task.category_id = category_id
        
        self.db.commit()
        self.db.refresh(task)
        return task

    def update_status(self, task_id: int, user_id: int, status: StatusEnum) -> Optional[Task]:
        """Обновить статус задачи"""
        task = self.get_by_id(task_id, user_id)
        if not task:
            return None
        
        task.status = status
        self.db.commit()
        self.db.refresh(task)
        return task
    
    def delete_task(self, task_id: int, user_id: int) -> bool:
        """Удалить задачу"""
        task = self.get_by_id(task_id, user_id)
        if not task:
            return False
        
        self.db.delete(task)
        self.db.commit()
        return True
    
    def count_by_user(self, user_id: int) -> int:
        """Получить общее количество задач у пользователя"""
        return (
            self.db.query(func.count(Task.task_id))
            .filter(Task.user_id == user_id)
            .scalar()
        )

    def count_by_status(self, user_id: int, status: StatusEnum) -> int:
        """Получить количество задач определенного статуса у пользователя"""
        return (
            self.db.query(func.count(Task.task_id))
            .filter(Task.user_id == user_id, Task.status == status)
            .scalar()
        )

    def get_task_statistics(self, user_id: int) -> dict:
        """Получить статистику задач пользователя"""
        total = self.count_by_user(user_id)
        todo_count = self.count_by_status(user_id, StatusEnum.todo)
        in_progress_count = self.count_by_status(user_id, StatusEnum.in_progress)
        done_count = self.count_by_status(user_id, StatusEnum.done)
        archived_count = self.count_by_status(user_id, StatusEnum.archived)
        
        # Подсчитываем просроченные задачи
        now = datetime.utcnow()
        overdue_count = (
            self.db.query(func.count(Task.task_id))
            .filter(
                Task.user_id == user_id,
                Task.due_date < now,
                Task.status != StatusEnum.done,
                Task.status != StatusEnum.archived
            )
            .scalar()
        )
        
        return {
            "total": total,
            "todo": todo_count,
            "in_progress": in_progress_count,
            "done": done_count,
            "archived": archived_count,
            "overdue": overdue_count
        }
