import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.models.base import BaseModel


class StatusEnum(enum.Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"
    archived = "archived"


class PriorityEnum(enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class Task(BaseModel):
    """Модель задачи, представляющая таблицу задач в базе данных."""

    __tablename__ = "tasks"

    task_id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    status: "Column[StatusEnum]" = Column(
        Enum(StatusEnum), default=StatusEnum.todo, nullable=False
    )
    priority: "Column[PriorityEnum]" = Column(
        Enum(PriorityEnum), default=PriorityEnum.medium, nullable=False
    )
    due_date = Column(DateTime, nullable=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=True)

    user = relationship("User", back_populates="tasks")
    category = relationship("Category", back_populates="tasks")
