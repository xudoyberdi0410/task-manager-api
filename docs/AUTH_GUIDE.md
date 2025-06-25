# Аутентификация в Task Manager API

Этот документ описывает, как реализована и используется система аутентификации в вашем API.

## Обзор

Система аутентификации использует:
- **JWT токены** для аутентификации
- **bcrypt** для хеширования паролей
- **OAuth2** схему с Bearer токенами
- **SQLAlchemy** для работы с базой данных

## Структура файлов

```
src/
├── auth/
│   └── jwt.py              # JWT токены и middleware
├── repositories/
│   └── user_repository.py  # Доступ к данным пользователей
├── services/
│   └── auth_service.py     # Бизнес-логика аутентификации
├── routers/
│   ├── token.py           # Эндпоинт для получения токена
│   ├── users.py           # Защищенные эндпоинты пользователей
│   └── auth.py            # Регистрация пользователей
├── schemas/
│   ├── token.py           # Pydantic модели для токенов
│   └── user.py            # Pydantic модели для пользователей
├── models/
│   └── user.py            # SQLAlchemy модель пользователя
├── database.py            # Настройка подключения к БД
└── config.py              # Конфигурация приложения
```

## Доступные эндпоинты

### 1. Регистрация пользователя
```http
POST /auth/register
Content-Type: application/json

{
    "email": "user@example.com",
    "username": "username",
    "password": "password123"
}
```

### 2. Получение токена (вход в систему)
```http
POST /token
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=password123
```

Ответ:
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```

### 3. Получение информации о текущем пользователе
```http
GET /api/users/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 4. Получение задач пользователя
```http
GET /api/users/me/tasks
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Как использовать в своих эндпоинтах

### Защита эндпоинта аутентификацией

```python
from typing import Annotated
from fastapi import APIRouter, Depends
from src.auth.jwt import get_current_active_user
from src.models.user import User

router = APIRouter()

@router.get("/protected-endpoint")
async def protected_endpoint(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return {"message": f"Hello, {current_user.username}!"}
```

### Получение пользователя и сессии БД

```python
from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.auth.jwt import get_current_active_user
from src.models.user import User
from src.database import get_db

@router.post("/user-specific-action")
async def user_action(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    # Здесь можно использовать current_user.user_id для фильтрации данных
    user_tasks = db.query(Task).filter(Task.user_id == current_user.user_id).all()
    return {"tasks": user_tasks}
```

## Конфигурация

В `src/config.py` настройте:

```python
class Settings(BaseSettings):
    # Security settings
    secret_key: str = "your-secret-key-here"  # Измените в продакшене!
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
```

## Тестирование

Проект включает полный набор тестов:

```bash
# Запуск всех тестов
make test-local

# Конкретные группы тестов
make test-auth          # Тесты аутентификации
make test-users         # Тесты пользователей
make test-repositories  # Тесты репозиториев
make test-services      # Тесты сервисов

# С покрытием кода
make test-coverage
```

Подробнее см. [TESTING.md](TESTING.md)

## Безопасность

- Всегда используйте HTTPS в продакшене
- Измените `secret_key` на случайный ключ (можно сгенерировать: `openssl rand -hex 32`)
- Храните секретные ключи в переменных окружения
- Настройте правильные CORS origins
- Используйте короткое время жизни токенов для критичных приложений

## Расширение функциональности

Вы можете легко добавить:
- Refresh токены
- Роли и права доступа
- Логирование входов
- Блокировку аккаунтов
- Двухфакторную аутентификацию
- OAuth2 с внешними провайдерами (Google, GitHub, etc.)
