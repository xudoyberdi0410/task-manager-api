"""
Репозиторий для работы с категориями в базе данных.
Содержит все операции CRUD для модели Category.
"""
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.models.category import Category


class CategoryRepository:
    """Репозиторий для работы с категориями"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, category_id: int, user_id: int) -> Optional[Category]:
        """Получить категорию по ID для конкретного пользователя"""
        return (
            self.db.query(Category)
            .filter(Category.category_id == category_id, Category.user_id == user_id)
            .first()
        )
    
    def get_by_title(self, title: str, user_id: int) -> Optional[Category]:
        """Получить категорию по названию для конкретного пользователя"""
        return (
            self.db.query(Category)
            .filter(Category.title == title, Category.user_id == user_id)
            .first()
        )

    def get_all_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> Tuple[List[Category], int]:
        """Получить список всех категорий пользователя с пагинацией"""
        # Получаем общее количество категорий пользователя
        total = (
            self.db.query(func.count(Category.category_id))
            .filter(Category.user_id == user_id)
            .scalar()
        )
        
        # Получаем категории с пагинацией
        categories = (
            self.db.query(Category)
            .filter(Category.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        return categories, total

    def search_categories(self, query: str, user_id: int, skip: int = 0, limit: int = 100) -> Tuple[List[Category], int]:
        """Поиск категорий по названию для конкретного пользователя"""
        search_filter = (
            (Category.title.ilike(f"%{query}%")) & 
            (Category.user_id == user_id)
        )
        
        # Получаем общее количество найденных категорий
        total = self.db.query(func.count(Category.category_id)).filter(search_filter).scalar()
        
        # Получаем категории с пагинацией
        categories = (
            self.db.query(Category)
            .filter(search_filter)
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        return categories, total
    
    def create_category(self, title: str, user_id: int) -> Category:
        """Создать новую категорию"""
        new_category = Category(
            title=title,
            user_id=user_id
        )
        self.db.add(new_category)
        self.db.commit()
        self.db.refresh(new_category)
        return new_category
    
    def update_category(self, category_id: int, user_id: int, **kwargs) -> Optional[Category]:
        """Обновить данные категории"""
        category = self.get_by_id(category_id, user_id)
        if not category:
            return None
        
        for key, value in kwargs.items():
            if value is not None and hasattr(category, key):
                setattr(category, key, value)
        
        self.db.commit()
        self.db.refresh(category)
        return category

    def update_category_partial(self, category_id: int, user_id: int, title: Optional[str] = None) -> Optional[Category]:
        """Частичное обновление данных категории"""
        category = self.get_by_id(category_id, user_id)
        if not category:
            return None
        
        if title is not None:
            category.title = title
        
        self.db.commit()
        self.db.refresh(category)
        return category
    
    def delete_category(self, category_id: int, user_id: int) -> bool:
        """Удалить категорию"""
        category = self.get_by_id(category_id, user_id)
        if not category:
            return False
        
        self.db.delete(category)
        self.db.commit()
        return True
    
    def exists_by_title(self, title: str, user_id: int) -> bool:
        """Проверить существование категории по названию для пользователя"""
        return (
            self.db.query(Category)
            .filter(Category.title == title, Category.user_id == user_id)
            .first() is not None
        )

    def exists_by_title_except_category(self, title: str, user_id: int, category_id: int) -> bool:
        """Проверить существование категории по названию, исключая указанную категорию"""
        return (
            self.db.query(Category)
            .filter(
                Category.title == title, 
                Category.user_id == user_id,
                Category.category_id != category_id
            )
            .first() is not None
        )

    def count_by_user(self, user_id: int) -> int:
        """Получить количество категорий у пользователя"""
        return (
            self.db.query(func.count(Category.category_id))
            .filter(Category.user_id == user_id)
            .scalar()
        )
