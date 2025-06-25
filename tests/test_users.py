"""
Тесты для защищенных эндпоинтов пользователей
"""
from fastapi.testclient import TestClient

def get_access_token(client, user_data: dict) -> str:
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

def test_get_current_user_success(client, test_user_data):
    """Тест получения информации о текущем пользователе"""
    token = get_access_token(client, test_user_data)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/users/me/", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert data["username"] == test_user_data["username"]

def test_get_current_user_without_token(client):
    """Тест доступа к защищенному эндпоинту без токена"""
    response = client.get("/api/users/me/")
    assert response.status_code == 401

def test_get_current_user_invalid_token(client):
    """Тест доступа с невалидным токеном"""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/api/users/me/", headers=headers)
    assert response.status_code == 401

def test_get_current_user_expired_token(client, test_user_data):
    """Тест доступа с истекшим токеном"""
    # Создаем токен с очень коротким временем жизни
    # Этот тест требует модификации для установки короткого времени жизни токена
    pass

def test_get_user_tasks(client, test_user_data):
    """Тест получения задач пользователя"""
    token = get_access_token(client, test_user_data)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/users/me/tasks/", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "tasks" in data
    assert data["owner"] == test_user_data["username"]

def test_different_users_isolation(client, test_user_data, another_user_data):
    """Тест изоляции данных разных пользователей"""
    # Получаем токены для двух разных пользователей
    token1 = get_access_token(client, test_user_data)
    token2 = get_access_token(client, another_user_data)
    
    # Проверяем, что каждый токен возвращает информацию о правильном пользователе
    headers1 = {"Authorization": f"Bearer {token1}"}
    response1 = client.get("/api/users/me/", headers=headers1)
    
    headers2 = {"Authorization": f"Bearer {token2}"}
    response2 = client.get("/api/users/me/", headers=headers2)
    
    assert response1.status_code == 200
    assert response2.status_code == 200
    
    data1 = response1.json()
    data2 = response2.json()
    
    assert data1["email"] == test_user_data["email"]
    assert data2["email"] == another_user_data["email"]
    assert data1["email"] != data2["email"]

def test_register_user(client, test_user_data):
    """Тест регистрации пользователя"""
    response = client.post("/auth/register", json=test_user_data)
    assert response.status_code == 201 or response.status_code == 200
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert data["username"] == test_user_data["username"]

def test_get_users_list(client, test_user_data):
    """Тест получения списка пользователей"""
    token = get_access_token(client, test_user_data)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/users", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    assert any(u["email"] == test_user_data["email"] for u in data["users"])

def test_search_users(client, test_user_data):
    """Тест поиска пользователей по email"""
    token = get_access_token(client, test_user_data)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"/api/users?search={test_user_data['email']}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert any(test_user_data["email"] in u["email"] for u in data["users"])

def test_update_user_me(client, test_user_data):
    """Тест обновления текущего пользователя"""
    token = get_access_token(client, test_user_data)
    headers = {"Authorization": f"Bearer {token}"}
    new_username = test_user_data["username"] + "_upd"
    response = client.put("/api/users/me", json={"username": new_username}, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == new_username

def test_delete_user_me(client, test_user_data):
    """Тест удаления текущего пользователя"""
    token = get_access_token(client, test_user_data)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.delete("/api/users/me", headers=headers)
    assert response.status_code == 204

    # Проверяем, что пользователь больше не может войти в систему
    login_data = {
        "username": test_user_data["email"],
        "password": test_user_data["password"]
    }
    login_response = client.post("/token", data=login_data)
    assert login_response.status_code == 401

def test_register_duplicate_email(client, test_user_data):
    """Тест регистрации пользователя с уже существующим email"""
    client.post("/auth/register", json=test_user_data)
    # Попытка зарегистрировать с тем же email
    user2 = test_user_data.copy()
    user2["username"] = user2["username"] + "_other"
    response = client.post("/auth/register", json=user2)
    assert response.status_code == 400 or response.status_code == 409

def test_register_duplicate_username(client, test_user_data):
    """Тест регистрации пользователя с уже существующим username"""
    client.post("/auth/register", json=test_user_data)
    # Попытка зарегистрировать с тем же username
    user2 = test_user_data.copy()
    user2["email"] = "other_" + user2["email"]
    response = client.post("/auth/register", json=user2)
    assert response.status_code == 400 or response.status_code == 409


def test_get_user_by_id(client, test_user_data):
    """Тест получения пользователя по ID"""
    token = get_access_token(client, test_user_data)
    headers = {"Authorization": f"Bearer {token}"}
    
    # Сначала получим ID пользователя
    me_response = client.get("/api/users/me/", headers=headers)
    user_id = me_response.json()["user_id"]

    response = client.get(f"/api/users/{user_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert data["user_id"] == user_id

def test_get_user_not_found(client, test_user_data):
    """Тест получения несуществующего пользователя"""
    token = get_access_token(client, test_user_data)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/users/99999", headers=headers)
    assert response.status_code == 404

def test_update_user_by_id(client, test_user_data):
    """Тест обновления пользователя по ID"""
    token = get_access_token(client, test_user_data)
    headers = {"Authorization": f"Bearer {token}"}
    
    me_response = client.get("/api/users/me/", headers=headers)
    user_id = me_response.json()["user_id"]

    new_username = "new_username_by_id"
    response = client.put(f"/api/users/{user_id}", json={"username": new_username}, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == new_username

def test_delete_user_by_id(client, test_user_data):
    """Тест удаления пользователя по ID"""
    token = get_access_token(client, test_user_data)
    headers = {"Authorization": f"Bearer {token}"}
    
    me_response = client.get("/api/users/me/", headers=headers)
    user_id = me_response.json()["user_id"]

    response = client.delete(f"/api/users/{user_id}", headers=headers)
    assert response.status_code == 204
    
    # Проверяем, что пользователь больше не может войти в систему
    login_data = {
        "username": test_user_data["email"],
        "password": test_user_data["password"]
    }
    login_response = client.post("/token", data=login_data)
    assert login_response.status_code == 401
