# Документация Task Manager API

Этот каталог содержит всю документацию для проекта Task Manager API.

## Содержание

- [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md) - Руководство по локальной разработке с Docker
- [AUTH_GUIDE.md](AUTH_GUIDE.md) - Руководство по системе аутентификации  
- [TESTING.md](TESTING.md) - Руководство по тестированию
- [TASKS_API.md](TASKS_API.md) - Документация API задач
- [TASKS_SECURITY.md](TASKS_SECURITY.md) - Система безопасности задач
- [GITHUB_ACTIONS.md](GITHUB_ACTIONS.md) - Настройка GitHub Actions CI/CD
- [DEV_TOOLS_SETUP.md](DEV_TOOLS_SETUP.md) - Установка инструментов разработки
- [DB.erd](DB.erd) - Диаграмма базы данных

## Быстрый старт

1. Прочитайте [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md) для настройки среды разработки
2. Изучите [AUTH_GUIDE.md](AUTH_GUIDE.md) для понимания системы аутентификации
3. Следуйте [TESTING.md](TESTING.md) для запуска тестов

## Структура проекта

```
src/
├── app.py              # Основное приложение FastAPI
├── config.py           # Конфигурация
├── database.py         # Настройка базы данных
├── auth/              # Модули аутентификации
├── models/            # Модели данных SQLAlchemy
├── repositories/      # Слой доступа к данным
├── routers/           # API роутеры
├── schemas/           # Pydantic схемы
├── services/          # Бизнес-логика
└── utils/             # Утилиты
```

## API Endpoints

### Аутентификация
- `POST /auth/register` - Регистрация пользователя
- `POST /token` - Получение JWT токена

### Пользователи
- `GET /api/users/me` - Информация о текущем пользователе
- `PUT /api/users/me` - Обновление профиля
- `GET /api/users/me/tasks` - Задачи пользователя

### Категории
- `GET /api/categories` - Список категорий
- `POST /api/categories` - Создание категории
- `PUT /api/categories/{id}` - Обновление категории
- `DELETE /api/categories/{id}` - Удаление категории

### Задачи
- `GET /api/tasks` - Список задач
- `POST /api/tasks` - Создание задачи
- `GET /api/tasks/{id}` - Получение задачи
- `PUT /api/tasks/{id}` - Обновление задачи
- `DELETE /api/tasks/{id}` - Удаление задачи
