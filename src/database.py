from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from src.config import settings

# Создание движка SQLAlchemy
engine = create_engine(settings.database_url, echo=settings.debug)

# Создание фабрики сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency для получения сессии базы данных
def get_db():
    """Получение сессии базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_context():
    """Контекстный менеджер для работы с базой данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_test_engine(database_url: str | None = None):
    """Создание тестового движка базы данных"""
    if database_url is None:
        database_url = "sqlite:///./test.db"
    return create_engine(database_url, echo=False)

def create_test_session(engine):
    """Создание тестовой сессии"""
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return TestSessionLocal()
