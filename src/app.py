from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

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

@app.get("/")
async def root():
    """Главная страница API"""
    return {
        "message": "Welcome to Task Manager API",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Проверка состояния API"""
    return {"status": "healthy"}

# Пример маршрута для задач
@app.get("/tasks")
async def get_tasks():
    """Получить список всех задач"""
    return {"tasks": []}

@app.post("/tasks")
async def create_task():
    """Создать новую задачу"""
    return {"message": "Task created successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)