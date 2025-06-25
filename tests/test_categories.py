import pytest
from src.services.category_service import CategoryService
from src.repositories.category_repository import CategoryRepository
from src.repositories.user_repository import UserRepository
from src.schemas.category import CategoryCreate, CategoryUpdate


@pytest.fixture
def category_service(db_session):
    return CategoryService(db_session)


@pytest.fixture
def category_repository(db_session):
    return CategoryRepository(db_session)


@pytest.fixture
def test_user(db_session):
    """Создать тестового пользователя"""
    user_repo = UserRepository(db_session)
    return user_repo.create_user(
        email="test_categories@example.com",
        username="test_categories_user",
        password="password123"
    )


def test_create_category_success(category_service, test_user):
    """Тест успешного создания категории"""
    category_data = CategoryCreate(title="Работа")
    category = category_service.create_category(category_data, test_user.user_id)
    
    assert category is not None
    assert category.title == "Работа"
    assert category.user_id == test_user.user_id


def test_create_category_duplicate_title(category_service, test_user):
    """Тест создания категории с дублирующимся названием"""
    category_data = CategoryCreate(title="Личное")
    
    # Создаем первую категорию
    first_category = category_service.create_category(category_data, test_user.user_id)
    assert first_category is not None
    
    # Пытаемся создать вторую категорию с тем же названием
    second_category = category_service.create_category(category_data, test_user.user_id)
    assert second_category is None


def test_get_category_by_id_success(category_service, test_user):
    """Тест получения категории по ID"""
    category_data = CategoryCreate(title="Покупки")
    created_category = category_service.create_category(category_data, test_user.user_id)
    
    retrieved_category = category_service.get_category_by_id(created_category.category_id, test_user.user_id)
    
    assert retrieved_category is not None
    assert retrieved_category.category_id == created_category.category_id
    assert retrieved_category.title == "Покупки"


def test_get_category_by_id_not_found(category_service, test_user):
    """Тест получения несуществующей категории"""
    category = category_service.get_category_by_id(999, test_user.user_id)
    assert category is None


def test_get_categories_by_user(category_service, test_user):
    """Тест получения списка категорий пользователя"""
    # Создаем несколько категорий
    categories_data = [
        CategoryCreate(title="Дом"),
        CategoryCreate(title="Учеба"),
        CategoryCreate(title="Спорт")
    ]
    
    for category_data in categories_data:
        category_service.create_category(category_data, test_user.user_id)
    
    categories, total = category_service.get_categories_by_user(test_user.user_id)
    
    assert total == 3
    assert len(categories) == 3
    assert all(cat.user_id == test_user.user_id for cat in categories)


def test_update_category_success(category_service, test_user):
    """Тест успешного обновления категории"""
    category_data = CategoryCreate(title="Старое название")
    created_category = category_service.create_category(category_data, test_user.user_id)
    
    update_data = CategoryUpdate(title="Новое название")
    updated_category = category_service.update_category(
        created_category.category_id, 
        update_data, 
        test_user.user_id
    )
    
    assert updated_category is not None
    assert updated_category.title == "Новое название"
    assert updated_category.category_id == created_category.category_id


def test_update_category_duplicate_title(category_service, test_user):
    """Тест обновления категории с дублирующимся названием"""
    # Создаем две категории
    category1_data = CategoryCreate(title="Категория 1")
    category2_data = CategoryCreate(title="Категория 2")
    
    category1 = category_service.create_category(category1_data, test_user.user_id)
    category2 = category_service.create_category(category2_data, test_user.user_id)
    
    # Пытаемся переименовать category2 в название category1
    update_data = CategoryUpdate(title="Категория 1")
    updated_category = category_service.update_category(
        category2.category_id, 
        update_data, 
        test_user.user_id
    )
    
    assert updated_category is None


def test_update_category_not_found(category_service, test_user):
    """Тест обновления несуществующей категории"""
    update_data = CategoryUpdate(title="Новое название")
    updated_category = category_service.update_category(999, update_data, test_user.user_id)
    
    assert updated_category is None


def test_delete_category_success(category_service, test_user):
    """Тест успешного удаления категории"""
    category_data = CategoryCreate(title="Удаляемая категория")
    created_category = category_service.create_category(category_data, test_user.user_id)
    
    success = category_service.delete_category(created_category.category_id, test_user.user_id)
    assert success is True
    
    # Проверяем, что категория действительно удалена
    deleted_category = category_service.get_category_by_id(created_category.category_id, test_user.user_id)
    assert deleted_category is None


def test_delete_category_not_found(category_service, test_user):
    """Тест удаления несуществующей категории"""
    success = category_service.delete_category(999, test_user.user_id)
    assert success is False


def test_search_categories(category_service, test_user):
    """Тест поиска категорий"""
    # Создаем категории
    categories_data = [
        CategoryCreate(title="Work Projects"),
        CategoryCreate(title="Home Tasks"),
        CategoryCreate(title="Work Meetings")
    ]
    
    for category_data in categories_data:
        category_service.create_category(category_data, test_user.user_id)
    
    # Поиск по слову "work"
    categories, total = category_service.search_categories("work", test_user.user_id)
    
    assert total == 2
    assert len(categories) == 2
    assert all("work" in cat.title.lower() for cat in categories)


def test_get_category_count_by_user(category_service, test_user):
    """Тест подсчета количества категорий пользователя"""
    # Создаем несколько категорий
    for i in range(5):
        category_data = CategoryCreate(title=f"Категория {i+1}")
        category_service.create_category(category_data, test_user.user_id)
    
    count = category_service.get_category_count_by_user(test_user.user_id)
    assert count == 5


def test_category_exists(category_service, test_user):
    """Тест проверки существования категории"""
    category_data = CategoryCreate(title="Существующая категория")
    created_category = category_service.create_category(category_data, test_user.user_id)
    
    # Проверяем существующую категорию
    exists = category_service.category_exists(created_category.category_id, test_user.user_id)
    assert exists is True
    
    # Проверяем несуществующую категорию
    not_exists = category_service.category_exists(999, test_user.user_id)
    assert not_exists is False


def test_repository_get_by_title(category_repository, test_user):
    """Тест получения категории по названию"""
    # Создаем категорию через репозиторий
    category = category_repository.create_category("Тестовая категория", test_user.user_id)
    
    # Получаем по названию
    found_category = category_repository.get_by_title("Тестовая категория", test_user.user_id)
    
    assert found_category is not None
    assert found_category.category_id == category.category_id
    assert found_category.title == "Тестовая категория"


def test_repository_exists_by_title(category_repository, test_user):
    """Тест проверки существования категории по названию"""
    # Создаем категорию
    category_repository.create_category("Проверяемая категория", test_user.user_id)
    
    # Проверяем существование
    exists = category_repository.exists_by_title("Проверяемая категория", test_user.user_id)
    assert exists is True
    
    # Проверяем несуществующую категорию
    not_exists = category_repository.exists_by_title("Несуществующая категория", test_user.user_id)
    assert not_exists is False


def test_repository_exists_by_title_except_category(category_repository, test_user):
    """Тест проверки существования категории по названию, исключая указанную"""
    # Создаем две категории
    category1 = category_repository.create_category("Категория А", test_user.user_id)
    category2 = category_repository.create_category("Категория Б", test_user.user_id)
    
    # Проверяем, что "Категория А" не существует, исключая category1 (должно быть False)
    exists = category_repository.exists_by_title_except_category(
        "Категория А", test_user.user_id, category1.category_id
    )
    assert exists is False
    
    # Проверяем, что "Категория А" существует, исключая category2 (должно быть True)
    exists = category_repository.exists_by_title_except_category(
        "Категория А", test_user.user_id, category2.category_id
    )
    assert exists is True
