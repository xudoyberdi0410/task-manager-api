"""
Тесты для сервиса задач.
"""
import pytest
from fastapi import HTTPException
from datetime import datetime, timedelta
from src.services.task_service import TaskService
from src.schemas.task import TaskCreate, TaskUpdate, TaskFilter
from src.models.task import StatusEnum, PriorityEnum
from src.models.user import User
from src.models.category import Category


class TestTaskService:
    """Тесты для TaskService"""
    
    @pytest.fixture
    def user(self, db_session):
        """Создать тестового пользователя"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user
    
    @pytest.fixture
    def category(self, db_session, user):
        """Создать тестовую категорию"""
        category = Category(
            title="Test Category",
            user_id=user.user_id
        )
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)
        return category
    
    @pytest.fixture
    def task_service(self, db_session):
        """Создать экземпляр TaskService"""
        return TaskService(db_session)
    
    def test_create_task_success(self, task_service, user):
        """Тест успешного создания задачи"""
        task_data = TaskCreate(
            title="Test Task",
            description="Test description",
            status=StatusEnum.todo,
            priority=PriorityEnum.medium
        )
        
        task = task_service.create_task(task_data, user.user_id)
        
        assert task.title == "Test Task"
        assert task.description == "Test description"
        assert task.status == StatusEnum.todo
        assert task.priority == PriorityEnum.medium
        assert task.user_id == user.user_id
    
    def test_create_task_with_category(self, task_service, user, category):
        """Тест создания задачи с категорией"""
        task_data = TaskCreate(
            title="Task with Category",
            category_id=category.category_id
        )
        
        task = task_service.create_task(task_data, user.user_id)
        
        assert task.category_id == category.category_id
    
    def test_create_task_with_invalid_category(self, task_service, user):
        """Тест создания задачи с несуществующей категорией"""
        task_data = TaskCreate(
            title="Task with Invalid Category",
            category_id=99999
        )
        
        with pytest.raises(HTTPException) as exc_info:
            task_service.create_task(task_data, user.user_id)
        
        assert exc_info.value.status_code == 404
        assert "Category not found" in str(exc_info.value.detail)
    
    def test_create_task_empty_title(self, task_service, user):
        """Тест создания задачи с пустым названием"""
        task_data = TaskCreate(title="   ")  # Только пробелы
        
        with pytest.raises(HTTPException) as exc_info:
            task_service.create_task(task_data, user.user_id)
        
        assert exc_info.value.status_code == 400
        assert "cannot be empty" in str(exc_info.value.detail)
    
    def test_get_task_by_id_success(self, task_service, user):
        """Тест успешного получения задачи по ID"""
        # Создаем задачу
        task_data = TaskCreate(title="Test Task")
        created_task = task_service.create_task(task_data, user.user_id)
        
        # Получаем задачу
        found_task = task_service.get_task_by_id(created_task.task_id, user.user_id)
        
        assert found_task.task_id == created_task.task_id
        assert found_task.title == "Test Task"
    
    def test_get_task_by_id_not_found(self, task_service, user):
        """Тест получения несуществующей задачи"""
        with pytest.raises(HTTPException) as exc_info:
            task_service.get_task_by_id(99999, user.user_id)
        
        assert exc_info.value.status_code == 404
        assert "Task not found" in str(exc_info.value.detail)
    
    def test_get_user_tasks_without_filters(self, task_service, user):
        """Тест получения задач пользователя без фильтров"""
        # Создаем несколько задач
        for i in range(3):
            task_data = TaskCreate(title=f"Task {i+1}")
            task_service.create_task(task_data, user.user_id)
        
        tasks, total = task_service.get_user_tasks(user.user_id)
        
        assert total == 3
        assert len(tasks) == 3
    
    def test_get_user_tasks_with_filters(self, task_service, user):
        """Тест получения задач с фильтрами"""
        # Создаем задачи с разными статусами
        task1_data = TaskCreate(title="Todo Task", status=StatusEnum.todo)
        task2_data = TaskCreate(title="Done Task", status=StatusEnum.done)
        
        task_service.create_task(task1_data, user.user_id)
        task_service.create_task(task2_data, user.user_id)
        
        # Фильтруем по статусу
        filters = TaskFilter(status=StatusEnum.todo)
        tasks, total = task_service.get_user_tasks(user.user_id, filters=filters)
        
        assert total == 1
        assert tasks[0].status == StatusEnum.todo
    
    def test_get_tasks_by_category_success(self, task_service, user, category):
        """Тест получения задач по категории"""
        # Создаем задачу с категорией
        task_data = TaskCreate(title="Categorized Task", category_id=category.category_id)
        task_service.create_task(task_data, user.user_id)
        
        tasks, total = task_service.get_tasks_by_category(user.user_id, category.category_id)
        
        assert total == 1
        assert tasks[0].category_id == category.category_id
    
    def test_get_tasks_by_invalid_category(self, task_service, user):
        """Тест получения задач по несуществующей категории"""
        with pytest.raises(HTTPException) as exc_info:
            task_service.get_tasks_by_category(user.user_id, 99999)
        
        assert exc_info.value.status_code == 404
        assert "Category not found" in str(exc_info.value.detail)
    
    def test_search_tasks_success(self, task_service, user):
        """Тест поиска задач"""
        # Создаем задачи для поиска
        task1_data = TaskCreate(title="Important meeting")
        task2_data = TaskCreate(title="Buy groceries")
        
        task_service.create_task(task1_data, user.user_id)
        task_service.create_task(task2_data, user.user_id)
        
        tasks, total = task_service.search_tasks(user.user_id, "meeting")
        
        assert total == 1
        assert "meeting" in tasks[0].title.lower()
    
    def test_search_tasks_empty_query(self, task_service, user):
        """Тест поиска с пустым запросом"""
        with pytest.raises(HTTPException) as exc_info:
            task_service.search_tasks(user.user_id, "   ")
        
        assert exc_info.value.status_code == 400
        assert "cannot be empty" in str(exc_info.value.detail)
    
    def test_update_task_success(self, task_service, user):
        """Тест успешного обновления задачи"""
        # Создаем задачу
        task_data = TaskCreate(title="Original Task")
        created_task = task_service.create_task(task_data, user.user_id)
        
        # Обновляем задачу
        update_data = TaskUpdate(
            title="Updated Task",
            status=StatusEnum.in_progress,
            priority=PriorityEnum.high
        )
        
        updated_task = task_service.update_task(created_task.task_id, update_data, user.user_id)
        
        assert updated_task.title == "Updated Task"
        assert updated_task.status == StatusEnum.in_progress
        assert updated_task.priority == PriorityEnum.high
    
    def test_update_task_with_category(self, task_service, user, category):
        """Тест обновления задачи с добавлением категории"""
        # Создаем задачу без категории
        task_data = TaskCreate(title="Task without category")
        created_task = task_service.create_task(task_data, user.user_id)
        
        # Добавляем категорию
        update_data = TaskUpdate(category_id=category.category_id)
        updated_task = task_service.update_task(created_task.task_id, update_data, user.user_id)
        
        assert updated_task.category_id == category.category_id
    
    def test_update_task_remove_category(self, task_service, user, category):
        """Тест удаления категории из задачи"""
        # Создаем задачу с категорией
        task_data = TaskCreate(title="Task with category", category_id=category.category_id)
        created_task = task_service.create_task(task_data, user.user_id)
        
        # Убираем категорию (передаем 0)
        update_data = TaskUpdate(category_id=0)
        updated_task = task_service.update_task(created_task.task_id, update_data, user.user_id)
        
        assert updated_task.category_id is None
    
    def test_update_task_empty_title(self, task_service, user):
        """Тест обновления задачи с пустым названием"""
        # Создаем задачу
        task_data = TaskCreate(title="Original Task")
        created_task = task_service.create_task(task_data, user.user_id)
        
        # Пытаемся обновить с пустым названием
        update_data = TaskUpdate(title="   ")
        
        with pytest.raises(HTTPException) as exc_info:
            task_service.update_task(created_task.task_id, update_data, user.user_id)
        
        assert exc_info.value.status_code == 400
    
    def test_update_task_not_found(self, task_service, user):
        """Тест обновления несуществующей задачи"""
        update_data = TaskUpdate(title="New Title")
        
        with pytest.raises(HTTPException) as exc_info:
            task_service.update_task(99999, update_data, user.user_id)
        
        assert exc_info.value.status_code == 404
    
    def test_update_task_status_success(self, task_service, user):
        """Тест обновления статуса задачи"""
        # Создаем задачу
        task_data = TaskCreate(title="Task to complete")
        created_task = task_service.create_task(task_data, user.user_id)
        
        # Обновляем статус
        updated_task = task_service.update_task_status(
            created_task.task_id, 
            StatusEnum.done, 
            user.user_id
        )
        
        assert updated_task.status == StatusEnum.done
    
    def test_update_task_status_not_found(self, task_service, user):
        """Тест обновления статуса несуществующей задачи"""
        with pytest.raises(HTTPException) as exc_info:
            task_service.update_task_status(99999, StatusEnum.done, user.user_id)
        
        assert exc_info.value.status_code == 404
    
    def test_delete_task_success(self, task_service, user):
        """Тест успешного удаления задачи"""
        # Создаем задачу
        task_data = TaskCreate(title="Task to delete")
        created_task = task_service.create_task(task_data, user.user_id)
        
        # Удаляем задачу
        success = task_service.delete_task(created_task.task_id, user.user_id)
        assert success is True
    
    def test_delete_task_not_found(self, task_service, user):
        """Тест удаления несуществующей задачи"""
        with pytest.raises(HTTPException) as exc_info:
            task_service.delete_task(99999, user.user_id)
        
        assert exc_info.value.status_code == 404
    
    def test_get_task_statistics(self, task_service, user):
        """Тест получения статистики задач"""
        # Создаем задачи разных типов
        tasks_data = [
            TaskCreate(title="Todo 1", status=StatusEnum.todo),
            TaskCreate(title="Todo 2", status=StatusEnum.todo),
            TaskCreate(title="In Progress", status=StatusEnum.in_progress),
            TaskCreate(title="Done", status=StatusEnum.done),
        ]
        
        for task_data in tasks_data:
            task_service.create_task(task_data, user.user_id)
        
        stats = task_service.get_task_statistics(user.user_id)
        
        assert stats["total"] == 4
        assert stats["todo"] == 2
        assert stats["in_progress"] == 1
        assert stats["done"] == 1
    
    def test_bulk_update_status_success(self, task_service, user):
        """Тест массового обновления статуса"""
        # Создаем несколько задач
        task_ids = []
        for i in range(3):
            task_data = TaskCreate(title=f"Bulk Task {i+1}")
            task = task_service.create_task(task_data, user.user_id)
            task_ids.append(task.task_id)
        
        # Массово обновляем статус
        updated_tasks = task_service.bulk_update_status(
            task_ids, 
            StatusEnum.done, 
            user.user_id
        )
        
        assert len(updated_tasks) == 3
        for task in updated_tasks:
            assert task.status == StatusEnum.done
    
    def test_bulk_update_status_with_invalid_ids(self, task_service, user):
        """Тест массового обновления с невалидными ID"""
        # Создаем одну задачу
        task_data = TaskCreate(title="Valid Task")
        valid_task = task_service.create_task(task_data, user.user_id)
        
        # Пытаемся обновить валидную и невалидную задачи
        task_ids = [valid_task.task_id, 99999]
        
        with pytest.raises(HTTPException) as exc_info:
            task_service.bulk_update_status(task_ids, StatusEnum.done, user.user_id)
        
        assert exc_info.value.status_code == 400
        assert "99999" in str(exc_info.value.detail)
    
    def test_bulk_delete_tasks_success(self, task_service, user):
        """Тест массового удаления задач"""
        # Создаем несколько задач
        task_ids = []
        for i in range(3):
            task_data = TaskCreate(title=f"Delete Task {i+1}")
            task = task_service.create_task(task_data, user.user_id)
            task_ids.append(task.task_id)
        
        # Массово удаляем задачи
        result = task_service.bulk_delete_tasks(task_ids, user.user_id)
        
        assert result["deleted_count"] == 3
        assert result["total_requested"] == 3
        assert len(result["failed_ids"]) == 0
    
    def test_bulk_delete_tasks_with_invalid_ids(self, task_service, user):
        """Тест массового удаления с невалидными ID"""
        # Создаем одну задачу
        task_data = TaskCreate(title="Valid Task")
        valid_task = task_service.create_task(task_data, user.user_id)
        
        # Пытаемся удалить валидную и невалидную задачи
        task_ids = [valid_task.task_id, 99999]
        
        result = task_service.bulk_delete_tasks(task_ids, user.user_id)
        
        assert result["deleted_count"] == 1
        assert result["total_requested"] == 2
        assert 99999 in result["failed_ids"]
