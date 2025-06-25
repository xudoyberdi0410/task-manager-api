"""
Сервис для работы с категориями.
Содержит бизнес-логику для управления категориями.
"""

from sqlalchemy.orm import Session

from src.repositories.category_repository import CategoryRepository
from src.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate


class CategoryService:
    """Сервис для работы с категориями"""

    def __init__(self, db: Session):
        self.repository = CategoryRepository(db)

    def get_category_by_id(
        self, category_id: int, user_id: int
    ) -> CategoryResponse | None:
        """Получить категорию по ID"""
        category = self.repository.get_by_id(category_id, user_id)
        if category:
            return CategoryResponse.model_validate(category)
        return None

    def get_categories_by_user(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> tuple[list[CategoryResponse], int]:
        """Получить список категорий пользователя"""
        categories, total = self.repository.get_all_by_user(user_id, skip, limit)
        category_responses = [
            CategoryResponse.model_validate(cat) for cat in categories
        ]
        return category_responses, total

    def search_categories(
        self, query: str, user_id: int, skip: int = 0, limit: int = 100
    ) -> tuple[list[CategoryResponse], int]:
        """Поиск категорий по названию"""
        categories, total = self.repository.search_categories(
            query, user_id, skip, limit
        )
        category_responses = [
            CategoryResponse.model_validate(cat) for cat in categories
        ]
        return category_responses, total

    def create_category(
        self, category_data: CategoryCreate, user_id: int
    ) -> CategoryResponse | None:
        """Создать новую категорию"""
        # Проверяем, что категория с таким названием не существует у пользователя
        if self.repository.exists_by_title(category_data.title, user_id):
            return None

        category = self.repository.create_category(category_data.title, user_id)
        return CategoryResponse.model_validate(category)

    def update_category(
        self, category_id: int, category_data: CategoryUpdate, user_id: int
    ) -> CategoryResponse | None:
        """Обновить категорию"""
        # Проверяем, что категория существует и принадлежит пользователю
        existing_category = self.repository.get_by_id(category_id, user_id)
        if not existing_category:
            return None

        # Если обновляется название, проверяем, что оно не занято другой категорией
        if (
            category_data.title is not None
            and self.repository.exists_by_title_except_category(
                category_data.title, user_id, category_id
            )
        ):
            return None

        # Обновляем только переданные поля
        update_data = category_data.model_dump(exclude_unset=True)
        category = self.repository.update_category(category_id, user_id, **update_data)

        if category:
            return CategoryResponse.model_validate(category)
        return None

    def delete_category(self, category_id: int, user_id: int) -> bool:
        """Удалить категорию"""
        return self.repository.delete_category(category_id, user_id)

    def category_exists(self, category_id: int, user_id: int) -> bool:
        """Проверить существование категории"""
        return self.repository.get_by_id(category_id, user_id) is not None

    def get_category_count_by_user(self, user_id: int) -> int:
        """Получить количество категорий у пользователя"""
        return self.repository.count_by_user(user_id)
