from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func
from datetime import datetime
from typing import Any, Dict

Base = declarative_base()

class BaseModel(Base):
    """Абстрактный базовый класс для всех моделей с общими методами и полями."""
    
    __abstract__ = True  # Указывает SQLAlchemy, что это абстрактный класс
    
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def as_dict(self) -> Dict[str, Any]:
        """Преобразует модель в словарь."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    @classmethod
    def create(cls, session, **kwargs):
        """Создает новую запись."""
        instance = cls(**kwargs)
        session.add(instance)
        session.flush()  # Получаем ID до коммита
        return instance
        
    def update(self, **kwargs):
        """Обновляет поля модели."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
        return self
