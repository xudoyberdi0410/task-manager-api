"""
Тесты безопасности для API задач.
Проверка изоляции задач между пользователями.
"""
import pytest
from fastapi.testclient import TestClient


def get_access_token(client: TestClient, user_data: dict) -> str:
    """Вспомогательная функция для получения токена доступа"""
    # Регистрируем пользователя
    client.post("/auth/register", json=user_data)
    
    # Получаем токен
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    response = client.post("/token", data=login_data)
    return response.json()["access_token"]


class TestTasksSecurity:
    """Тесты безопасности для задач"""

    def test_cannot_access_other_user_task(self, client: TestClient, test_user_data: dict, another_user_data: dict):
        """Тест: пользователь не может получить чужую задачу"""
        # Получаем токены для двух пользователей
        token1 = get_access_token(client, test_user_data)
        token2 = get_access_token(client, another_user_data)
        
        headers1 = {"Authorization": f"Bearer {token1}"}
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        # Первый пользователь создает задачу
        task_data = {
            "title": "Private Task",
            "description": "This task belongs to user 1"
        }
        response = client.post("/api/tasks/", json=task_data, headers=headers1)
        assert response.status_code == 201
        task_id = response.json()["task_id"]
        
        # Второй пользователь пытается получить задачу первого
        response = client.get(f"/api/tasks/{task_id}", headers=headers2)
        assert response.status_code == 404  # Задача не найдена (для второго пользователя)

    def test_cannot_update_other_user_task(self, client: TestClient, test_user_data: dict, another_user_data: dict):
        """Тест: пользователь не может обновить чужую задачу"""
        # Получаем токены для двух пользователей
        token1 = get_access_token(client, test_user_data)
        token2 = get_access_token(client, another_user_data)
        
        headers1 = {"Authorization": f"Bearer {token1}"}
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        # Первый пользователь создает задачу
        task_data = {
            "title": "Original Task",
            "description": "Original description"
        }
        response = client.post("/api/tasks/", json=task_data, headers=headers1)
        assert response.status_code == 201
        task_id = response.json()["task_id"]
        
        # Второй пользователь пытается обновить задачу первого
        update_data = {
            "title": "Hacked Task",
            "description": "This should not work"
        }
        response = client.put(f"/api/tasks/{task_id}", json=update_data, headers=headers2)
        assert response.status_code == 404  # Задача не найдена (для второго пользователя)
        
        # Проверяем, что задача не изменилась
        response = client.get(f"/api/tasks/{task_id}", headers=headers1)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Original Task"  # Оригинальное название не изменилось

    def test_cannot_delete_other_user_task(self, client: TestClient, test_user_data: dict, another_user_data: dict):
        """Тест: пользователь не может удалить чужую задачу"""
        # Получаем токены для двух пользователей
        token1 = get_access_token(client, test_user_data)
        token2 = get_access_token(client, another_user_data)
        
        headers1 = {"Authorization": f"Bearer {token1}"}
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        # Первый пользователь создает задачу
        task_data = {
            "title": "Task to protect",
            "description": "This task should not be deleted by another user"
        }
        response = client.post("/api/tasks/", json=task_data, headers=headers1)
        assert response.status_code == 201
        task_id = response.json()["task_id"]
        
        # Второй пользователь пытается удалить задачу первого
        response = client.delete(f"/api/tasks/{task_id}", headers=headers2)
        assert response.status_code == 404  # Задача не найдена (для второго пользователя)
        
        # Проверяем, что задача все еще существует
        response = client.get(f"/api/tasks/{task_id}", headers=headers1)
        assert response.status_code == 200  # Задача все еще доступна владельцу

    def test_cannot_update_task_status_of_other_user(self, client: TestClient, test_user_data: dict, another_user_data: dict):
        """Тест: пользователь не может изменить статус чужой задачи"""
        # Получаем токены для двух пользователей
        token1 = get_access_token(client, test_user_data)
        token2 = get_access_token(client, another_user_data)
        
        headers1 = {"Authorization": f"Bearer {token1}"}
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        # Первый пользователь создает задачу
        task_data = {
            "title": "Status Protection Task",
            "status": "todo"
        }
        response = client.post("/api/tasks/", json=task_data, headers=headers1)
        assert response.status_code == 201
        task_id = response.json()["task_id"]
        
        # Второй пользователь пытается изменить статус задачи первого
        response = client.patch(f"/api/tasks/{task_id}/status?new_status=done", headers=headers2)
        assert response.status_code == 404  # Задача не найдена (для второго пользователя)
        
        # Проверяем, что статус не изменился
        response = client.get(f"/api/tasks/{task_id}", headers=headers1)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "todo"  # Статус остался прежним

    def test_tasks_isolation_in_list(self, client: TestClient, test_user_data: dict, another_user_data: dict):
        """Тест: пользователи видят только свои задачи в списке"""
        # Получаем токены для двух пользователей
        token1 = get_access_token(client, test_user_data)
        token2 = get_access_token(client, another_user_data)
        
        headers1 = {"Authorization": f"Bearer {token1}"}
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        # Первый пользователь создает задачи
        for i in range(3):
            task_data = {"title": f"User1 Task {i+1}"}
            client.post("/api/tasks/", json=task_data, headers=headers1)
        
        # Второй пользователь создает задачи
        for i in range(2):
            task_data = {"title": f"User2 Task {i+1}"}
            client.post("/api/tasks/", json=task_data, headers=headers2)
        
        # Проверяем, что каждый пользователь видит только свои задачи
        response1 = client.get("/api/tasks/", headers=headers1)
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["total"] == 3
        for task in data1["tasks"]:
            assert "User1" in task["title"]
        
        response2 = client.get("/api/tasks/", headers=headers2)
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["total"] == 2
        for task in data2["tasks"]:
            assert "User2" in task["title"]

    def test_bulk_operations_isolation(self, client: TestClient, test_user_data: dict, another_user_data: dict):
        """Тест: массовые операции не затрагивают чужие задачи"""
        # Получаем токены для двух пользователей
        token1 = get_access_token(client, test_user_data)
        token2 = get_access_token(client, another_user_data)
        
        headers1 = {"Authorization": f"Bearer {token1}"}
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        # Первый пользователь создает задачи
        task_ids_user1 = []
        for i in range(3):
            task_data = {"title": f"User1 Bulk Task {i+1}"}
            response = client.post("/api/tasks/", json=task_data, headers=headers1)
            task_ids_user1.append(response.json()["task_id"])
        
        # Второй пользователь создает задачи
        task_ids_user2 = []
        for i in range(2):
            task_data = {"title": f"User2 Bulk Task {i+1}"}
            response = client.post("/api/tasks/", json=task_data, headers=headers2)
            task_ids_user2.append(response.json()["task_id"])
        
        # Второй пользователь пытается массово изменить статус задач первого пользователя
        bulk_data = {
            "task_ids": task_ids_user1,  # ID задач первого пользователя
            "new_status": "done"
        }
        response = client.patch("/api/tasks/bulk/status", json=bulk_data, headers=headers2)
        # Ожидаем ошибку, так как задачи не принадлежат второму пользователю
        assert response.status_code == 400
        
        # Проверяем, что задачи первого пользователя не изменились
        for task_id in task_ids_user1:
            response = client.get(f"/api/tasks/{task_id}", headers=headers1)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "todo"  # Статус остался прежним

    def test_bulk_delete_isolation(self, client: TestClient, test_user_data: dict, another_user_data: dict):
        """Тест: массовое удаление не затрагивает чужие задачи"""
        # Получаем токены для двух пользователей
        token1 = get_access_token(client, test_user_data)
        token2 = get_access_token(client, another_user_data)
        
        headers1 = {"Authorization": f"Bearer {token1}"}
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        # Первый пользователь создает задачи
        task_ids_user1 = []
        for i in range(3):
            task_data = {"title": f"User1 Delete Task {i+1}"}
            response = client.post("/api/tasks/", json=task_data, headers=headers1)
            task_ids_user1.append(response.json()["task_id"])
        
        # Второй пользователь пытается массово удалить задачи первого пользователя
        bulk_data = {"task_ids": task_ids_user1}
        response = client.request("DELETE", "/api/tasks/bulk", json=bulk_data, headers=headers2)
        assert response.status_code == 200
        
        # Проверяем результат - должно быть 0 удаленных задач
        data = response.json()
        assert data["deleted_count"] == 0
        assert len(data["failed_ids"]) == 3  # Все ID в списке неудачных
        
        # Проверяем, что все задачи первого пользователя все еще существуют
        for task_id in task_ids_user1:
            response = client.get(f"/api/tasks/{task_id}", headers=headers1)
            assert response.status_code == 200

    def test_search_isolation(self, client: TestClient, test_user_data: dict, another_user_data: dict):
        """Тест: поиск задач изолирован между пользователями"""
        # Получаем токены для двух пользователей
        token1 = get_access_token(client, test_user_data)
        token2 = get_access_token(client, another_user_data)
        
        headers1 = {"Authorization": f"Bearer {token1}"}
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        # Первый пользователь создает задачу с уникальным словом
        task_data = {"title": "Confidential Secret Project"}
        client.post("/api/tasks/", json=task_data, headers=headers1)
        
        # Второй пользователь создает задачу с тем же словом
        task_data = {"title": "My Secret Recipe"}
        client.post("/api/tasks/", json=task_data, headers=headers2)
        
        # Каждый пользователь ищет по слову "Secret"
        response1 = client.get("/api/tasks/search?q=Secret", headers=headers1)
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["total"] == 1
        assert "Confidential" in data1["tasks"][0]["title"]
        
        response2 = client.get("/api/tasks/search?q=Secret", headers=headers2)
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["total"] == 1
        assert "Recipe" in data2["tasks"][0]["title"]

    def test_category_tasks_isolation(self, client: TestClient, test_user_data: dict, another_user_data: dict):
        """Тест: задачи по категориям изолированы между пользователями"""
        # Получаем токены для двух пользователей
        token1 = get_access_token(client, test_user_data)
        token2 = get_access_token(client, another_user_data)
        
        headers1 = {"Authorization": f"Bearer {token1}"}
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        # Каждый пользователь создает категорию с одинаковым названием
        category_data = {"title": "Work"}
        
        response1 = client.post("/api/categories/", json=category_data, headers=headers1)
        category1_id = response1.json()["category_id"]
        
        response2 = client.post("/api/categories/", json=category_data, headers=headers2)
        category2_id = response2.json()["category_id"]
        
        # Каждый пользователь создает задачу в своей категории
        task_data1 = {"title": "User1 Work Task", "category_id": category1_id}
        client.post("/api/tasks/", json=task_data1, headers=headers1)
        
        task_data2 = {"title": "User2 Work Task", "category_id": category2_id}
        client.post("/api/tasks/", json=task_data2, headers=headers2)
        
        # Первый пользователь пытается получить задачи из категории второго пользователя
        response = client.get(f"/api/tasks/category/{category2_id}", headers=headers1)
        assert response.status_code == 404  # Категория не найдена (для первого пользователя)
        
        # Второй пользователь пытается получить задачи из категории первого пользователя
        response = client.get(f"/api/tasks/category/{category1_id}", headers=headers2)
        assert response.status_code == 404  # Категория не найдена (для второго пользователя)
        
        # Каждый пользователь может получить задачи только из своей категории
        response1 = client.get(f"/api/tasks/category/{category1_id}", headers=headers1)
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["total"] == 1
        assert "User1" in data1["tasks"][0]["title"]
        
        response2 = client.get(f"/api/tasks/category/{category2_id}", headers=headers2)
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["total"] == 1
        assert "User2" in data2["tasks"][0]["title"]
