from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.models.base import BaseModel


class Category(BaseModel):
    """Модель категории, представляющая таблицу категорий в базе данных."""

    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(50), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    user = relationship("User", back_populates="categories")
    tasks = relationship("Task", back_populates="category")
