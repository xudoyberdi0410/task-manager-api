from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers import auth, categories, tasks, token, users

# Описание для Swagger документации
description = """
## Task Manager API

Comprehensive REST API for task management with user authentication and categorization.

### Features:

* **Authentication**: JWT-based authentication system
* **User Management**: User registration, login, and profile management
* **Task Management**: Create, read, update, and delete tasks with filters
* **Categories**: Organize tasks with custom categories
* **Priorities & Status**: Task prioritization and status tracking
* **Search & Filter**: Advanced search and filtering capabilities

### API Sections:

* **Authentication**: Login, logout, and token management
* **Users**: User profile and account management
* **Tasks**: Complete task CRUD operations with filtering
* **Categories**: Task categorization system

### Getting Started:

1. Register a new user account or login with existing credentials
2. Obtain an access token from the `/token` endpoint
3. Use the token in the Authorization header: `Bearer <your_token>`
4. Start managing your tasks and categories

### Security:

All endpoints (except authentication) require a valid JWT token in the Authorization header.
"""

# Метаданные тегов для группировки эндпоинтов
tags_metadata: list[dict[str, Any]] = [
    {
        "name": "🏠 Health & Info",
        "description": "Информация о состоянии API и основные данные",
    },
    {
        "name": "🔐 Authentication",
        "description": "Аутентификация и получение токенов доступа",
        "externalDocs": {
            "description": "Подробнее об аутентификации",
            "url": "https://fastapi.tiangolo.com/tutorial/security/",
        },
    },
    {
        "name": "👤 User Registration",
        "description": "Регистрация новых пользователей",
    },
    {
        "name": "👥 User Management",
        "description": "Управление профилями пользователей",
    },
    {
        "name": "📁 Categories",
        "description": "Создание и управление категориями задач",
    },
    {
        "name": "📋 Tasks",
        "description": "Полное управление задачами - создание, чтение, обновление, удаление",
    },
    {
        "name": "📊 Statistics",
        "description": "Статистика и аналитика по задачам",
    },
]

# Создаем экземпляр FastAPI приложения
app = FastAPI(
    title="Task Manager API",
    description=description,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=tags_metadata,
    contact={
        "name": "Task Manager API Support",
        "url": "https://github.com/xudoyberdi0410/task-manager-api",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {"url": "http://localhost:8000", "description": "Development server"},
        {"url": "https://task-manager-api-fntf.onrender.com", "description": "Production server"},
    ],
    # Настройки безопасности для Swagger UI
    swagger_ui_parameters={
        "persistAuthorization": True,
        "displayRequestDuration": True,
        "filter": True,
        "tryItOutEnabled": True,
    },
)

# Настройка CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(",") if settings.allowed_origins != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры с улучшенными тегами
app.include_router(
    token.router,
    tags=["🔐 Authentication"],
    prefix="",
    responses={
        401: {"description": "Неверные учетные данные"},
        422: {"description": "Ошибка валидации данных"},
    },
)

app.include_router(
    auth.router,
    prefix="/auth",
    tags=["👤 User Registration"],
    responses={
        400: {"description": "Пользователь уже существует"},
        422: {"description": "Ошибка валидации данных"},
    },
)

app.include_router(
    users.router,
    prefix="/api",
    tags=["👥 User Management"],
    responses={
        401: {"description": "Не авторизован"},
        403: {"description": "Доступ запрещен"},
        404: {"description": "Пользователь не найден"},
    },
)

app.include_router(
    categories.router,
    prefix="/api",
    tags=["📁 Categories"],
    responses={
        401: {"description": "Не авторизован"},
        403: {"description": "Доступ запрещен"},
        404: {"description": "Категория не найдена"},
    },
)

app.include_router(
    tasks.router,
    prefix="/api",
    tags=["📋 Tasks"],
    responses={
        401: {"description": "Не авторизован"},
        403: {"description": "Доступ запрещен"},
        404: {"description": "Задача не найдена"},
    },
)


@app.get(
    "/",
    summary="API Information",
    description="Get basic information about the Task Manager API, including environment and service status",
    response_description="API information and service status",
    tags=["🏠 Health & Info"],
)
async def root():
    """
    ## API Welcome Endpoint

    Returns basic information about the Task Manager API including:
    - Welcome message
    - Current environment
    - Documentation links
    - Service connectivity status
    """
    return {
        "message": "Welcome to Task Manager API",
        "environment": settings.environment,
        "docs": "/docs",
        "redoc": "/redoc",
        "database_connected": True if settings.database_url else False,
    }


@app.get(
    "/health",
    summary="Health Check",
    description="Check if the API is running and accessible",
    response_description="Service health status",
    tags=["🏠 Health & Info"],
)
async def health_check():
    """
    ## Health Check Endpoint

    Simple health check to verify the API is running properly.
    Used by monitoring systems and load balancers.
    """
    return {"status": "healthy", "timestamp": "2025-06-25T00:00:00Z"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
