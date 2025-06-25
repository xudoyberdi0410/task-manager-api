from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from .config import settings
from .routers import token, users, auth, categories, tasks

# Создаем экземпляр FastAPI приложения
app = FastAPI(
    title="Task Manager API",
    description="API для управления задачами",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Настройка CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене укажите конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(token.router, tags=["authentication"])
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(categories.router, prefix="/api", tags=["categories"])
app.include_router(tasks.router, prefix="/api", tags=["tasks"])

@app.get("/")
async def root():
    """Главная страница API"""
    return {
        "message": "Welcome to Task Manager API",
        "environment": settings.environment,
        "docs": "/docs",
        "database_connected": True if settings.database_url else False,
        "redis_connected": True if settings.redis_url else False
    }

@app.get("/health")
async def health_check():
    """Проверка состояния API"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)