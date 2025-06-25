"""
Конфигурация для тестов
"""
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

# Устанавливаем переменную для тестового режима
os.environ["TESTING"] = "true"

from src.app import app
from src.models.base import Base
# Импортируем все модели чтобы они были зарегистрированы в Base
from src.models.user import User
from src.models.task import Task 
from src.models.category import Category
from src.database import get_db

# Глобальный тестовый движок
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def get_test_db():
    """Получение тестовой сессии БД"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Автоматическая настройка базы данных для каждого теста"""
    # Создаем таблицы перед каждым тестом
    Base.metadata.create_all(bind=test_engine)
    yield
    # Удаляем таблицы после каждого теста
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="function")
def client():
    """Фикстура для тестового клиента FastAPI"""
    # Переопределяем зависимость для каждого теста
    app.dependency_overrides[get_db] = get_test_db
    with TestClient(app) as c:
        yield c
    # Очищаем переопределения после теста
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def db_session():
    """Фикстура для создания тестовой сессии БД"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def test_user_data():
    """Фикстура с тестовыми данными пользователя"""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123"
    }

@pytest.fixture
def another_user_data():
    """Фикстура с данными другого пользователя"""
    return {
        "email": "another@example.com",
        "username": "anotheruser",
        "password": "anotherpassword123"
    }

@pytest.fixture
def auth_headers(client: TestClient, test_user_data: dict):
    """Фикстура для получения заголовков авторизации"""
    # Регистрируем пользователя
    client.post("/auth/register", json=test_user_data)
    
    # Логинимся
    login_data = {
        "username": test_user_data["username"],
        "password": test_user_data["password"]
    }
    response = client.post("/token", data=login_data)
    token = response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def test_category(client: TestClient, auth_headers: dict):
    """Фикстура для создания тестовой категории"""
    category_data = {"title": "Test Category"}
    response = client.post("/api/categories/", json=category_data, headers=auth_headers)
    return response.json()

@pytest.fixture
def test_task(client: TestClient, auth_headers: dict):
    """Фикстура для создания тестовой задачи"""
    task_data = {
        "title": "Test Task",
        "description": "Test task description",
        "status": "todo",
        "priority": "medium"
    }
    response = client.post("/api/tasks/", json=task_data, headers=auth_headers)
    return response.json()

@pytest.fixture
def test_task_with_category(client: TestClient, auth_headers: dict, test_category: dict):
    """Фикстура для создания тестовой задачи с категорией"""
    task_data = {
        "title": "Task with Category",
        "description": "Task with category description",
        "category_id": test_category["category_id"]
    }
    response = client.post("/api/tasks/", json=task_data, headers=auth_headers)
    return response.json()

@pytest.fixture
def another_user_headers(client: TestClient, another_user_data: dict):
    """Фикстура для получения заголовков авторизации второго пользователя"""
    # Регистрируем второго пользователя
    client.post("/auth/register", json=another_user_data)
    
    # Логинимся
    login_data = {
        "username": another_user_data["username"],
        "password": another_user_data["password"]
    }
    response = client.post("/token", data=login_data)
    token = response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def test_user(db_session):
    """Фикстура для создания тестового пользователя для unit-тестов"""
    from src.repositories.user_repository import UserRepository
    
    user_repo = UserRepository(db_session)
    return user_repo.create_user(
        email="test@example.com",
        username="testuser",
        password="testpassword123"
    )

@pytest.fixture
def another_user(db_session):
    """Фикстура для создания второго тестового пользователя для unit-тестов"""
    from src.repositories.user_repository import UserRepository
    
    user_repo = UserRepository(db_session)
    return user_repo.create_user(
        email="another@example.com",
        username="anotheruser",
        password="anotherpassword123"
    )
