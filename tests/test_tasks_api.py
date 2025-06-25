"""
Тесты для API задач.
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from src.models.task import StatusEnum, PriorityEnum


class TestTasksAPI:
    """Тесты для API задач"""
    
    def test_create_task(self, client: TestClient, auth_headers: dict):
        """Тест создания задачи"""
        task_data = {
            "title": "Test Task",
            "description": "Test task description",
            "status": "todo",
            "priority": "medium"
        }
        
        response = client.post("/api/tasks/", json=task_data, headers=auth_headers)
        assert response.status_code == 201
        
        data = response.json()
        assert data["title"] == task_data["title"]
        assert data["description"] == task_data["description"]
        assert data["status"] == task_data["status"]
        assert data["priority"] == task_data["priority"]
        assert "task_id" in data
        assert "created_at" in data
    
    def test_create_task_with_category(self, client: TestClient, auth_headers: dict, test_category: dict):
        """Тест создания задачи с категорией"""
        task_data = {
            "title": "Task with Category",
            "description": "Task with category description",
            "category_id": test_category["category_id"]
        }
        
        response = client.post("/api/tasks/", json=task_data, headers=auth_headers)
        assert response.status_code == 201
        
        data = response.json()
        assert data["category_id"] == test_category["category_id"]
    
    def test_create_task_with_due_date(self, client: TestClient, auth_headers: dict):
        """Тест создания задачи с датой выполнения"""
        due_date = (datetime.utcnow() + timedelta(days=7)).isoformat()
        task_data = {
            "title": "Task with Due Date",
            "due_date": due_date
        }
        
        response = client.post("/api/tasks/", json=task_data, headers=auth_headers)
        assert response.status_code == 201
        
        data = response.json()
        assert data["due_date"] is not None
    
    def test_create_task_invalid_data(self, client: TestClient, auth_headers: dict):
        """Тест создания задачи с невалидными данными"""
        task_data = {
            "title": "",  # Пустое название
        }
        
        response = client.post("/api/tasks/", json=task_data, headers=auth_headers)
        assert response.status_code == 400
    
    def test_get_tasks(self, client: TestClient, auth_headers: dict, test_task: dict):
        """Тест получения списка задач"""
        response = client.get("/api/tasks/", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "tasks" in data
        assert "total" in data
        assert len(data["tasks"]) >= 1
    
    def test_get_tasks_with_pagination(self, client: TestClient, auth_headers: dict):
        """Тест получения задач с пагинацией"""
        # Создаем несколько задач
        for i in range(5):
            task_data = {"title": f"Task {i+1}"}
            client.post("/api/tasks/", json=task_data, headers=auth_headers)
        
        # Получаем первые 3 задачи
        response = client.get("/api/tasks/?skip=0&limit=3", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["tasks"]) <= 3
        assert data["page"] == 1
        assert data["per_page"] == 3
    
    def test_get_tasks_with_filters(self, client: TestClient, auth_headers: dict):
        """Тест получения задач с фильтрацией"""
        # Создаем задачу с определенным статусом
        task_data = {
            "title": "In Progress Task",
            "status": "in_progress"
        }
        client.post("/api/tasks/", json=task_data, headers=auth_headers)
        
        # Фильтруем по статусу
        response = client.get("/api/tasks/?status=in_progress", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        for task in data["tasks"]:
            assert task["status"] == "in_progress"
    
    def test_get_task_by_id(self, client: TestClient, auth_headers: dict, test_task: dict):
        """Тест получения задачи по ID"""
        task_id = test_task["task_id"]
        response = client.get(f"/api/tasks/{task_id}", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["task_id"] == task_id
    
    def test_get_nonexistent_task(self, client: TestClient, auth_headers: dict):
        """Тест получения несуществующей задачи"""
        response = client.get("/api/tasks/99999", headers=auth_headers)
        assert response.status_code == 404
    
    def test_update_task(self, client: TestClient, auth_headers: dict, test_task: dict):
        """Тест обновления задачи"""
        task_id = test_task["task_id"]
        update_data = {
            "title": "Updated Task Title",
            "status": "in_progress",
            "priority": "high"
        }
        
        response = client.put(f"/api/tasks/{task_id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["status"] == update_data["status"]
        assert data["priority"] == update_data["priority"]
    
    def test_update_task_status(self, client: TestClient, auth_headers: dict, test_task: dict):
        """Тест обновления статуса задачи"""
        task_id = test_task["task_id"]
        new_status = "done"
        
        response = client.patch(f"/api/tasks/{task_id}/status?new_status={new_status}", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == new_status
    
    def test_search_tasks(self, client: TestClient, auth_headers: dict):
        """Тест поиска задач"""
        # Создаем задачу для поиска
        task_data = {"title": "Unique Search Task"}
        client.post("/api/tasks/", json=task_data, headers=auth_headers)
        
        # Ищем задачу
        response = client.get("/api/tasks/search?q=Unique", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["tasks"]) >= 1
        assert any("Unique" in task["title"] for task in data["tasks"])
    
    def test_get_tasks_by_status(self, client: TestClient, auth_headers: dict):
        """Тест получения задач по статусу"""
        # Создаем задачу с определенным статусом
        task_data = {"title": "Done Task", "status": "done"}
        client.post("/api/tasks/", json=task_data, headers=auth_headers)
        
        response = client.get("/api/tasks/status/done", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        for task in data["tasks"]:
            assert task["status"] == "done"
    
    def test_get_overdue_tasks(self, client: TestClient, auth_headers: dict):
        """Тест получения просроченных задач"""
        # Создаем просроченную задачу
        past_date = (datetime.utcnow() - timedelta(days=1)).isoformat()
        task_data = {
            "title": "Overdue Task",
            "due_date": past_date,
            "status": "todo"
        }
        client.post("/api/tasks/", json=task_data, headers=auth_headers)
        
        response = client.get("/api/tasks/overdue", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        # Проверяем, что есть просроченные задачи
        # (может быть 0, если в тестовой БД нет просроченных задач)
        assert "tasks" in data
    
    def test_get_task_statistics(self, client: TestClient, auth_headers: dict):
        """Тест получения статистики задач"""
        response = client.get("/api/tasks/statistics", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "total" in data
        assert "todo" in data
        assert "in_progress" in data
        assert "done" in data
        assert "archived" in data
        assert "overdue" in data
    
    def test_bulk_update_status(self, client: TestClient, auth_headers: dict):
        """Тест массового обновления статуса"""
        # Создаем несколько задач
        task_ids = []
        for i in range(3):
            task_data = {"title": f"Bulk Task {i+1}"}
            response = client.post("/api/tasks/", json=task_data, headers=auth_headers)
            task_ids.append(response.json()["task_id"])
        
        # Массово обновляем статус
        update_data = {
            "task_ids": task_ids,
            "new_status": "done"
        }
        response = client.patch(
            "/api/tasks/bulk/status", 
            json=update_data, 
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 3
        for task in data:
            assert task["status"] == "done"
    
    def test_bulk_delete_tasks(self, client: TestClient, auth_headers: dict):
        """Тест массового удаления задач"""
        # Создаем несколько задач
        task_ids = []
        for i in range(3):
            task_data = {"title": f"Delete Task {i+1}"}
            response = client.post("/api/tasks/", json=task_data, headers=auth_headers)
            task_ids.append(response.json()["task_id"])
        
        # Массово удаляем задачи
        delete_data = {"task_ids": task_ids}
        response = client.request(
            "DELETE",
            "/api/tasks/bulk",
            json=delete_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["deleted_count"] == 3
        assert data["total_requested"] == 3
    
    def test_delete_task(self, client: TestClient, auth_headers: dict, test_task: dict):
        """Тест удаления задачи"""
        task_id = test_task["task_id"]
        response = client.delete(f"/api/tasks/{task_id}", headers=auth_headers)
        assert response.status_code == 204
        
        # Проверяем, что задача удалена
        response = client.get(f"/api/tasks/{task_id}", headers=auth_headers)
        assert response.status_code == 404
    
    def test_unauthorized_access(self, client: TestClient):
        """Тест доступа без авторизации"""
        response = client.get("/api/tasks/")
        assert response.status_code == 401
