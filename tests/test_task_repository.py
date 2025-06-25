"""
Тесты для репозитория задач.
"""

from datetime import datetime, timedelta

import pytest

from src.models.category import Category
from src.models.task import PriorityEnum, StatusEnum, Task
from src.models.user import User
from src.repositories.task_repository import TaskRepository


class TestTaskRepository:
    """Тесты для TaskRepository"""

    @pytest.fixture
    def user(self, db_session):
        """Создать тестового пользователя"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    @pytest.fixture
    def category(self, db_session, user):
        """Создать тестовую категорию"""
        category = Category(title="Test Category", user_id=user.user_id)
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)
        return category

    @pytest.fixture
    def task_repo(self, db_session):
        """Создать экземпляр TaskRepository"""
        return TaskRepository(db_session)

    @pytest.fixture
    def task(self, db_session, user):
        """Создать тестовую задачу"""
        task = Task(
            title="Test Task",
            description="Test description",
            status=StatusEnum.todo,
            priority=PriorityEnum.medium,
            user_id=user.user_id,
        )
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)
        return task

    def test_create_task(self, task_repo, user):
        """Тест создания задачи"""
        task = task_repo.create_task(
            title="New Task",
            user_id=user.user_id,
            description="New task description",
            status=StatusEnum.todo,
            priority=PriorityEnum.high,
        )

        assert task.title == "New Task"
        assert task.description == "New task description"
        assert task.status == StatusEnum.todo
        assert task.priority == PriorityEnum.high
        assert task.user_id == user.user_id
        assert task.task_id is not None

    def test_get_by_id(self, task_repo, task, user):
        """Тест получения задачи по ID"""
        found_task = task_repo.get_by_id(task.task_id, user.user_id)

        assert found_task is not None
        assert found_task.task_id == task.task_id
        assert found_task.title == task.title

    def test_get_by_id_wrong_user(self, task_repo, task, db_session):
        """Тест получения задачи другим пользователем"""
        # Создаем другого пользователя
        other_user = User(
            email="other@example.com",
            username="otheruser",
            hashed_password="hashed_password",
        )
        db_session.add(other_user)
        db_session.commit()
        db_session.refresh(other_user)

        found_task = task_repo.get_by_id(task.task_id, other_user.user_id)
        assert found_task is None

    def test_get_all_by_user(self, task_repo, user, db_session):
        """Тест получения всех задач пользователя"""
        # Создаем несколько задач
        for i in range(3):
            task = Task(title=f"Task {i + 1}", user_id=user.user_id)
            db_session.add(task)
        db_session.commit()

        tasks, total = task_repo.get_all_by_user(user.user_id)

        assert total == 3
        assert len(tasks) == 3

    def test_get_all_by_user_with_filters(self, task_repo, user, db_session):
        """Тест получения задач с фильтрацией"""
        # Создаем задачи с разными статусами
        task1 = Task(title="Task 1", status=StatusEnum.todo, user_id=user.user_id)
        task2 = Task(
            title="Task 2", status=StatusEnum.in_progress, user_id=user.user_id
        )
        task3 = Task(title="Task 3", status=StatusEnum.done, user_id=user.user_id)

        db_session.add_all([task1, task2, task3])
        db_session.commit()

        # Фильтр по статусу
        tasks, total = task_repo.get_all_by_user(
            user_id=user.user_id, status=StatusEnum.todo
        )

        assert total == 1
        assert tasks[0].status == StatusEnum.todo

    def test_get_by_status(self, task_repo, user, db_session):
        """Тест получения задач по статусу"""
        # Создаем задачи с разными статусами
        for status in [StatusEnum.todo, StatusEnum.in_progress, StatusEnum.todo]:
            task = Task(
                title=f"Task {status.value}", status=status, user_id=user.user_id
            )
            db_session.add(task)
        db_session.commit()

        tasks, total = task_repo.get_by_status(user.user_id, StatusEnum.todo)

        assert total == 2
        for task in tasks:
            assert task.status == StatusEnum.todo

    def test_get_by_category(self, task_repo, user, category, db_session):
        """Тест получения задач по категории"""
        # Создаем задачи с категорией и без
        task1 = Task(
            title="Task 1", category_id=category.category_id, user_id=user.user_id
        )
        task2 = Task(title="Task 2", user_id=user.user_id)

        db_session.add_all([task1, task2])
        db_session.commit()

        tasks, total = task_repo.get_by_category(user.user_id, category.category_id)

        assert total == 1
        assert tasks[0].category_id == category.category_id

    def test_get_overdue_tasks(self, task_repo, user, db_session):
        """Тест получения просроченных задач"""
        past_date = datetime.utcnow() - timedelta(days=1)
        future_date = datetime.utcnow() + timedelta(days=1)

        # Создаем просроченную задачу
        overdue_task = Task(
            title="Overdue Task",
            due_date=past_date,
            status=StatusEnum.todo,
            user_id=user.user_id,
        )

        # Создаем не просроченную задачу
        normal_task = Task(
            title="Normal Task",
            due_date=future_date,
            status=StatusEnum.todo,
            user_id=user.user_id,
        )

        # Создаем выполненную просроченную задачу (не должна попасть в результат)
        done_task = Task(
            title="Done Task",
            due_date=past_date,
            status=StatusEnum.done,
            user_id=user.user_id,
        )

        db_session.add_all([overdue_task, normal_task, done_task])
        db_session.commit()

        tasks, total = task_repo.get_overdue_tasks(user.user_id)

        assert total == 1
        assert tasks[0].title == "Overdue Task"

    def test_search_tasks(self, task_repo, user, db_session):
        """Тест поиска задач"""
        # Создаем задачи для поиска
        task1 = Task(
            title="Important meeting",
            description="Weekly team meeting",
            user_id=user.user_id,
        )
        task2 = Task(
            title="Buy groceries", description="Milk, bread, eggs", user_id=user.user_id
        )
        task3 = Task(
            title="Code review",
            description="Review PR for important feature",
            user_id=user.user_id,
        )

        db_session.add_all([task1, task2, task3])
        db_session.commit()

        # Поиск по названию
        tasks, total = task_repo.search_tasks("meeting", user.user_id)
        assert total == 1
        assert tasks[0].title == "Important meeting"

        # Поиск по описанию
        tasks, total = task_repo.search_tasks("important", user.user_id)
        assert total == 2  # В названии и в описании

    def test_update_task(self, task_repo, task, user):
        """Тест обновления задачи"""
        updated_task = task_repo.update_task(
            task.task_id,
            user.user_id,
            title="Updated Title",
            status=StatusEnum.in_progress,
            priority=PriorityEnum.high,
        )

        assert updated_task is not None
        assert updated_task.title == "Updated Title"
        assert updated_task.status == StatusEnum.in_progress
        assert updated_task.priority == PriorityEnum.high

    def test_update_task_partial(self, task_repo, task, user):
        """Тест частичного обновления задачи"""
        original_description = task.description

        updated_task = task_repo.update_task_partial(
            task.task_id, user.user_id, title="New Title"
        )

        assert updated_task is not None
        assert updated_task.title == "New Title"
        assert updated_task.description == original_description  # Не изменилось

    def test_update_status(self, task_repo, task, user):
        """Тест обновления статуса задачи"""
        updated_task = task_repo.update_status(
            task.task_id, user.user_id, StatusEnum.done
        )

        assert updated_task is not None
        assert updated_task.status == StatusEnum.done

    def test_delete_task(self, task_repo, task, user):
        """Тест удаления задачи"""
        success = task_repo.delete_task(task.task_id, user.user_id)
        assert success is True

        # Проверяем, что задача удалена
        deleted_task = task_repo.get_by_id(task.task_id, user.user_id)
        assert deleted_task is None

    def test_delete_nonexistent_task(self, task_repo, user):
        """Тест удаления несуществующей задачи"""
        success = task_repo.delete_task(99999, user.user_id)
        assert success is False

    def test_count_by_user(self, task_repo, user, db_session):
        """Тест подсчета задач пользователя"""
        # Создаем несколько задач
        for i in range(5):
            task = Task(title=f"Task {i + 1}", user_id=user.user_id)
            db_session.add(task)
        db_session.commit()

        count = task_repo.count_by_user(user.user_id)
        assert count == 5

    def test_count_by_status(self, task_repo, user, db_session):
        """Тест подсчета задач по статусу"""
        # Создаем задачи с разными статусами
        statuses = [
            StatusEnum.todo,
            StatusEnum.todo,
            StatusEnum.in_progress,
            StatusEnum.done,
        ]
        for status in statuses:
            task = Task(
                title=f"Task {status.value}", status=status, user_id=user.user_id
            )
            db_session.add(task)
        db_session.commit()

        todo_count = task_repo.count_by_status(user.user_id, StatusEnum.todo)
        assert todo_count == 2

        in_progress_count = task_repo.count_by_status(
            user.user_id, StatusEnum.in_progress
        )
        assert in_progress_count == 1

    def test_get_task_statistics(self, task_repo, user, db_session):
        """Тест получения статистики задач"""
        past_date = datetime.utcnow() - timedelta(days=1)

        # Создаем задачи разных типов
        tasks_data = [
            {"title": "Todo 1", "status": StatusEnum.todo},
            {"title": "Todo 2", "status": StatusEnum.todo},
            {"title": "In Progress", "status": StatusEnum.in_progress},
            {"title": "Done", "status": StatusEnum.done},
            {"title": "Overdue", "status": StatusEnum.todo, "due_date": past_date},
        ]

        for data in tasks_data:
            task = Task(user_id=user.user_id, **data)
            db_session.add(task)
        db_session.commit()

        stats = task_repo.get_task_statistics(user.user_id)

        assert stats["total"] == 5
        assert stats["todo"] == 3  # Включая просроченную
        assert stats["in_progress"] == 1
        assert stats["done"] == 1
        assert stats["overdue"] == 1
