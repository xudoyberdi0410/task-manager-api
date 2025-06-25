"""
Тесты безопасности для сервисного слоя задач.
Проверка защиты на уровне бизнес-логики.
"""
import pytest
from fastapi import HTTPException
from src.services.task_service import TaskService
from src.schemas.task import TaskCreate, TaskUpdate
from src.models.task import StatusEnum, PriorityEnum


class TestTaskServiceSecurity:
    """Тесты безопасности для сервиса задач"""

    def test_get_task_by_id_security(self, db_session, test_user, another_user):
        """Тест: получение задачи по ID с проверкой владельца"""
        task_service = TaskService(db_session)
        
        # Создаем задачу для первого пользователя
        task_data = TaskCreate(title="Private Task", description="Secret information")
        task = task_service.create_task(task_data, test_user.user_id)
        
        # Пытаемся получить задачу от имени другого пользователя
        with pytest.raises(HTTPException) as exc_info:
            task_service.get_task_by_id(task.task_id, another_user.user_id)
        
        assert exc_info.value.status_code == 404
        assert "Task not found" in str(exc_info.value.detail)

    def test_update_task_security(self, db_session, test_user, another_user):
        """Тест: обновление задачи с проверкой владельца"""
        task_service = TaskService(db_session)
        
        # Создаем задачу для первого пользователя
        task_data = TaskCreate(title="Original Task")
        task = task_service.create_task(task_data, test_user.user_id)
        
        # Пытаемся обновить задачу от имени другого пользователя
        update_data = TaskUpdate(title="Hacked Task")
        with pytest.raises(HTTPException) as exc_info:
            task_service.update_task(task.task_id, update_data, another_user.user_id)
        
        assert exc_info.value.status_code == 404
        assert "Task not found" in str(exc_info.value.detail)

    def test_update_task_status_security(self, db_session, test_user, another_user):
        """Тест: обновление статуса задачи с проверкой владельца"""
        task_service = TaskService(db_session)
        
        # Создаем задачу для первого пользователя
        task_data = TaskCreate(title="Status Task", status=StatusEnum.todo)
        task = task_service.create_task(task_data, test_user.user_id)
        
        # Пытаемся обновить статус от имени другого пользователя
        with pytest.raises(HTTPException) as exc_info:
            task_service.update_task_status(task.task_id, StatusEnum.done, another_user.user_id)
        
        assert exc_info.value.status_code == 404
        assert "Task not found" in str(exc_info.value.detail)

    def test_delete_task_security(self, db_session, test_user, another_user):
        """Тест: удаление задачи с проверкой владельца"""
        task_service = TaskService(db_session)
        
        # Создаем задачу для первого пользователя
        task_data = TaskCreate(title="Task to Delete")
        task = task_service.create_task(task_data, test_user.user_id)
        
        # Пытаемся удалить задачу от имени другого пользователя
        with pytest.raises(HTTPException) as exc_info:
            task_service.delete_task(task.task_id, another_user.user_id)
        
        assert exc_info.value.status_code == 404
        assert "Task not found" in str(exc_info.value.detail)
        
        # Проверяем, что задача все еще существует
        retrieved_task = task_service.get_task_by_id(task.task_id, test_user.user_id)
        assert retrieved_task is not None
        assert retrieved_task.title == "Task to Delete"

    def test_get_user_tasks_isolation(self, db_session, test_user, another_user):
        """Тест: получение задач пользователя - изоляция"""
        task_service = TaskService(db_session)
        
        # Создаем задачи для первого пользователя
        for i in range(3):
            task_data = TaskCreate(title=f"User1 Task {i+1}")
            task_service.create_task(task_data, test_user.user_id)
        
        # Создаем задачи для второго пользователя
        for i in range(2):
            task_data = TaskCreate(title=f"User2 Task {i+1}")
            task_service.create_task(task_data, another_user.user_id)
        
        # Проверяем, что каждый пользователь видит только свои задачи
        user1_tasks, user1_total = task_service.get_user_tasks(test_user.user_id)
        assert user1_total == 3
        for task in user1_tasks:
            assert "User1" in task.title
            assert task.user_id == test_user.user_id
        
        user2_tasks, user2_total = task_service.get_user_tasks(another_user.user_id)
        assert user2_total == 2
        for task in user2_tasks:
            assert "User2" in task.title
            assert task.user_id == another_user.user_id

    def test_get_tasks_by_status_isolation(self, db_session, test_user, another_user):
        """Тест: получение задач по статусу - изоляция пользователей"""
        task_service = TaskService(db_session)
        
        # Создаем задачи с одинаковым статусом для разных пользователей
        task_data = TaskCreate(title="User1 In Progress", status=StatusEnum.in_progress)
        task_service.create_task(task_data, test_user.user_id)
        
        task_data = TaskCreate(title="User2 In Progress", status=StatusEnum.in_progress)
        task_service.create_task(task_data, another_user.user_id)
        
        # Каждый пользователь должен видеть только свои задачи
        user1_tasks, user1_total = task_service.get_tasks_by_status(
            test_user.user_id, StatusEnum.in_progress
        )
        assert user1_total == 1
        assert user1_tasks[0].title == "User1 In Progress"
        assert user1_tasks[0].user_id == test_user.user_id
        
        user2_tasks, user2_total = task_service.get_tasks_by_status(
            another_user.user_id, StatusEnum.in_progress
        )
        assert user2_total == 1
        assert user2_tasks[0].title == "User2 In Progress"
        assert user2_tasks[0].user_id == another_user.user_id

    def test_search_tasks_isolation(self, db_session, test_user, another_user):
        """Тест: поиск задач - изоляция пользователей"""
        task_service = TaskService(db_session)
        
        # Создаем задачи с одинаковым поисковым термином для разных пользователей
        task_data = TaskCreate(title="Important Project for User1")
        task_service.create_task(task_data, test_user.user_id)
        
        task_data = TaskCreate(title="Important Project for User2")
        task_service.create_task(task_data, another_user.user_id)
        
        # Каждый пользователь должен находить только свои задачи
        user1_tasks, user1_total = task_service.search_tasks(
            test_user.user_id, "Important"
        )
        assert user1_total == 1
        assert "User1" in user1_tasks[0].title
        assert user1_tasks[0].user_id == test_user.user_id
        
        user2_tasks, user2_total = task_service.search_tasks(
            another_user.user_id, "Important"
        )
        assert user2_total == 1
        assert "User2" in user2_tasks[0].title
        assert user2_tasks[0].user_id == another_user.user_id

    def test_bulk_update_status_security(self, db_session, test_user, another_user):
        """Тест: массовое обновление статуса - защита от чужих задач"""
        task_service = TaskService(db_session)
        
        # Создаем задачи для первого пользователя
        user1_task_ids = []
        for i in range(3):
            task_data = TaskCreate(title=f"User1 Bulk Task {i+1}")
            task = task_service.create_task(task_data, test_user.user_id)
            user1_task_ids.append(task.task_id)
        
        # Второй пользователь пытается массово обновить задачи первого
        with pytest.raises(HTTPException) as exc_info:
            task_service.bulk_update_status(
                user1_task_ids, StatusEnum.done, another_user.user_id
            )
        
        assert exc_info.value.status_code == 400
        assert "Failed to update tasks" in str(exc_info.value.detail)
        
        # Проверяем, что задачи не изменились
        for task_id in user1_task_ids:
            task = task_service.get_task_by_id(task_id, test_user.user_id)
            assert task.status == StatusEnum.todo  # Статус по умолчанию

    def test_bulk_delete_tasks_security(self, db_session, test_user, another_user):
        """Тест: массовое удаление задач - защита от чужих задач"""
        task_service = TaskService(db_session)
        
        # Создаем задачи для первого пользователя
        user1_task_ids = []
        for i in range(3):
            task_data = TaskCreate(title=f"User1 Delete Task {i+1}")
            task = task_service.create_task(task_data, test_user.user_id)
            user1_task_ids.append(task.task_id)
        
        # Второй пользователь пытается массово удалить задачи первого
        result = task_service.bulk_delete_tasks(user1_task_ids, another_user.user_id)
        
        # Должно быть 0 удаленных задач и все ID в списке неудачных
        assert result["deleted_count"] == 0
        assert len(result["failed_ids"]) == 3
        assert result["total_requested"] == 3
        
        # Проверяем, что все задачи все еще существуют
        for task_id in user1_task_ids:
            task = task_service.get_task_by_id(task_id, test_user.user_id)
            assert task is not None

    def test_get_task_statistics_isolation(self, db_session, test_user, another_user):
        """Тест: статистика задач - изоляция пользователей"""
        task_service = TaskService(db_session)
        
        # Создаем разные задачи для первого пользователя
        task_service.create_task(
            TaskCreate(title="Todo Task", status=StatusEnum.todo), 
            test_user.user_id
        )
        task_service.create_task(
            TaskCreate(title="In Progress Task", status=StatusEnum.in_progress), 
            test_user.user_id
        )
        task_service.create_task(
            TaskCreate(title="Done Task", status=StatusEnum.done), 
            test_user.user_id
        )
        
        # Создаем задачи для второго пользователя
        task_service.create_task(
            TaskCreate(title="User2 Task 1", status=StatusEnum.todo), 
            another_user.user_id
        )
        task_service.create_task(
            TaskCreate(title="User2 Task 2", status=StatusEnum.todo), 
            another_user.user_id
        )
        
        # Проверяем статистику для каждого пользователя
        user1_stats = task_service.get_task_statistics(test_user.user_id)
        assert user1_stats["total"] == 3
        assert user1_stats["todo"] == 1
        assert user1_stats["in_progress"] == 1
        assert user1_stats["done"] == 1
        
        user2_stats = task_service.get_task_statistics(another_user.user_id)
        assert user2_stats["total"] == 2
        assert user2_stats["todo"] == 2
        assert user2_stats["in_progress"] == 0
        assert user2_stats["done"] == 0
