"""
Конфигурация для тестов
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

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
