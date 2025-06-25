# Документация Task Manager API

Этот каталог содержит всю документацию для проекта Task Manager API.

## Содержание

- [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md) - Руководство по локальной разработке с Docker
- [AUTH_GUIDE.md](AUTH_GUIDE.md) - Руководство по системе аутентификации
- [TESTING.md](TESTING.md) - Руководство по тестированию
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
- `GET /users/me` - Информация о текущем пользователе
- `PUT /users/me` - Обновление профиля

### Категории
- `GET /categories` - Список категорий
- `POST /categories` - Создание категории
- `PUT /categories/{id}` - Обновление категории
- `DELETE /categories/{id}` - Удаление категории
