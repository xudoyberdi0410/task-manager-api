import pytest

from src.repositories.category_repository import CategoryRepository
from src.repositories.user_repository import UserRepository


@pytest.fixture
def test_user_for_api(db_session):
    """Создать тестового пользователя для API тестов"""
    user_repo = UserRepository(db_session)
    return user_repo.create_user(
        email="api_test@example.com", username="api_test_user", password="password123"
    )


@pytest.fixture
def auth_headers(client, test_user_for_api):
    """Получить заголовки авторизации для тестов API"""
    # Логинимся и получаем токен
    response = client.post(
        "/token", data={"username": test_user_for_api.email, "password": "password123"}
    )

    assert response.status_code == 200
    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


def test_create_category_api(client, auth_headers):
    """Тест создания категории через API"""
    category_data = {"title": "API Тест Категория"}

    response = client.post("/api/categories/", json=category_data, headers=auth_headers)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "API Тест Категория"
    assert "category_id" in data
    assert "user_id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_category_duplicate_api(client, auth_headers):
    """Тест создания дублирующейся категории через API"""
    category_data = {"title": "Дублирующаяся категория"}

    # Создаем первую категорию
    response1 = client.post(
        "/api/categories/", json=category_data, headers=auth_headers
    )
    assert response1.status_code == 201

    # Пытаемся создать вторую с тем же названием
    response2 = client.post(
        "/api/categories/", json=category_data, headers=auth_headers
    )
    assert response2.status_code == 400
    assert "уже существует" in response2.json()["detail"]


def test_get_categories_api(client, auth_headers, db_session, test_user_for_api):
    """Тест получения списка категорий через API"""
    # Создаем несколько категорий через репозиторий
    category_repo = CategoryRepository(db_session)
    category_repo.create_category("Категория 1", test_user_for_api.user_id)
    category_repo.create_category("Категория 2", test_user_for_api.user_id)
    category_repo.create_category("Категория 3", test_user_for_api.user_id)

    response = client.get("/api/categories/", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "categories" in data
    assert "total" in data
    assert "page" in data
    assert "per_page" in data
    assert data["total"] >= 3
    assert len(data["categories"]) >= 3


def test_get_category_by_id_api(client, auth_headers, db_session, test_user_for_api):
    """Тест получения категории по ID через API"""
    # Создаем категорию
    category_repo = CategoryRepository(db_session)
    category = category_repo.create_category(
        "Тестовая категория", test_user_for_api.user_id
    )

    response = client.get(
        f"/api/categories/{category.category_id}", headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["category_id"] == category.category_id
    assert data["title"] == "Тестовая категория"
    assert data["user_id"] == test_user_for_api.user_id


def test_get_category_not_found_api(client, auth_headers):
    """Тест получения несуществующей категории через API"""
    response = client.get("/api/categories/999", headers=auth_headers)

    assert response.status_code == 404
    assert "не найдена" in response.json()["detail"]


def test_update_category_api(client, auth_headers, db_session, test_user_for_api):
    """Тест обновления категории через API"""
    # Создаем категорию
    category_repo = CategoryRepository(db_session)
    category = category_repo.create_category(
        "Старое название", test_user_for_api.user_id
    )

    update_data = {"title": "Новое название"}

    response = client.put(
        f"/api/categories/{category.category_id}",
        json=update_data,
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Новое название"
    assert data["category_id"] == category.category_id


def test_update_category_not_found_api(client, auth_headers):
    """Тест обновления несуществующей категории через API"""
    update_data = {"title": "Новое название"}

    response = client.put("/api/categories/999", json=update_data, headers=auth_headers)

    assert response.status_code == 404
    assert "не найдена" in response.json()["detail"]


def test_patch_category_api(client, auth_headers, db_session, test_user_for_api):
    """Тест частичного обновления категории через API"""
    # Создаем категорию
    category_repo = CategoryRepository(db_session)
    category = category_repo.create_category(
        "Исходное название", test_user_for_api.user_id
    )

    update_data = {"title": "Обновленное название"}

    response = client.patch(
        f"/api/categories/{category.category_id}",
        json=update_data,
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Обновленное название"


def test_delete_category_api(client, auth_headers, db_session, test_user_for_api):
    """Тест удаления категории через API"""
    # Создаем категорию
    category_repo = CategoryRepository(db_session)
    category = category_repo.create_category(
        "Удаляемая категория", test_user_for_api.user_id
    )

    response = client.delete(
        f"/api/categories/{category.category_id}", headers=auth_headers
    )

    assert response.status_code == 204

    # Проверяем, что категория действительно удалена
    get_response = client.get(
        f"/api/categories/{category.category_id}", headers=auth_headers
    )
    assert get_response.status_code == 404


def test_delete_category_not_found_api(client, auth_headers):
    """Тест удаления несуществующей категории через API"""
    response = client.delete("/api/categories/999", headers=auth_headers)

    assert response.status_code == 404
    assert "не найдена" in response.json()["detail"]


def test_search_categories_api(client, auth_headers, db_session, test_user_for_api):
    """Тест поиска категорий через API"""
    # Создаем категории
    category_repo = CategoryRepository(db_session)
    category_repo.create_category("Work Projects", test_user_for_api.user_id)
    category_repo.create_category("Home Tasks", test_user_for_api.user_id)
    category_repo.create_category("Work Meetings", test_user_for_api.user_id)

    # Поиск по слову "work"
    response = client.get("/api/categories/?search=work", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 2
    # Проверяем, что все найденные категории содержат искомое слово
    for category in data["categories"]:
        assert "work" in category["title"].lower()


def test_get_categories_with_pagination_api(
    client, auth_headers, db_session, test_user_for_api
):
    """Тест пагинации списка категорий через API"""
    # Создаем несколько категорий
    category_repo = CategoryRepository(db_session)
    for i in range(5):
        category_repo.create_category(f"Категория {i + 1}", test_user_for_api.user_id)

    # Запрашиваем первые 2 категории
    response = client.get("/api/categories/?skip=0&limit=2", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data["categories"]) == 2
    assert data["per_page"] == 2
    assert data["page"] == 1
    assert data["total"] >= 5


def test_get_categories_count_api(client, auth_headers, db_session, test_user_for_api):
    """Тест получения количества категорий через API"""
    # Создаем несколько категорий
    category_repo = CategoryRepository(db_session)
    for i in range(3):
        category_repo.create_category(
            f"Счетная категория {i + 1}", test_user_for_api.user_id
        )

    response = client.get("/api/categories/stats/count", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert data["count"] >= 3


def test_unauthorized_access_api(client):
    """Тест доступа к API без авторизации"""
    # Попытка получить категории без токена
    response = client.get("/api/categories/")
    assert response.status_code == 401

    # Попытка создать категорию без токена
    response = client.post("/api/categories/", json={"title": "Тест"})
    assert response.status_code == 401

    # Попытка получить категорию по ID без токена
    response = client.get("/api/categories/1")
    assert response.status_code == 401

    # Попытка обновить категорию без токена
    response = client.put("/api/categories/1", json={"title": "Тест"})
    assert response.status_code == 401

    # Попытка удалить категорию без токена
    response = client.delete("/api/categories/1")
    assert response.status_code == 401
