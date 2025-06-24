from src.models.base import BaseModel

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

class User(BaseModel):
    """Модель пользователя, представляющая таблицу пользователей в базе данных."""
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    username = Column(String(50), nullable=False)

    tasks = relationship("Task", back_populates="user")
    categories = relationship("Category", back_populates="user")
