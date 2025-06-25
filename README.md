# Task Manager API

FastAPI приложение для управления задачами с использованием uv для управления зависимостями.

## Документация

📚 **Полная документация находится в папке [docs/](docs/)**

- [Локальная разработка](docs/LOCAL_DEVELOPMENT.md) - Подробное руководство по разработке
- [Система аутентификации](docs/AUTH_GUIDE.md) - Как работает аутентификация
- [Тестирование](docs/TESTING.md) - Руководство по тестированию

## Технологии

- **FastAPI** - веб-фреймворк
- **uv** - менеджер пакетов Python
- **PostgreSQL** - база данных
- **Redis** - кэширование
- **Docker** - контейнеризация

## Быстрый старт

### 1. Клонирование и настройка

```bash
# Клонировать репозиторий
git clone <repository-url>
cd task-manager-api

# Создать .env файл
cp .env.example .env
```

### 2. Запуск с Docker

```bash
# Собрать и запустить все сервисы
docker-compose up --build

# Или использовать Makefile
make init
```

### 3. Доступ к приложению

- **API**: http://localhost:8000
- **Документация**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **pgAdmin**: http://localhost:5050 (admin@admin.com / admin)

## Разработка

### Локальная разработка с uv

```bash
# Установить uv (если не установлен)
pip install uv

# Установить зависимости
uv sync

# Запустить приложение
uv run uvicorn src.app:app --reload
```

### Docker команды

```bash
# Запустить сервисы
docker-compose up -d

# Остановить сервисы
docker-compose down

# Посмотреть логи
docker-compose logs -f api

# Подключиться к контейнеру
docker-compose exec api bash
```

### Makefile команды

```bash
make help          # Показать все доступные команды
make build         # Собрать Docker образ
make up            # Запустить сервисы
make down          # Остановить сервисы
make logs          # Показать логи
make shell         # Подключиться к контейнеру
make clean         # Очистить Docker ресурсы
make reset         # Полный сброс
```

## Структура проекта

```
task-manager-api/
├── docs/                   # 📚 Документация
│   ├── README.md          # Обзор документации
│   ├── LOCAL_DEVELOPMENT.md # Локальная разработка
│   ├── AUTH_GUIDE.md      # Система аутентификации
│   ├── TESTING.md         # Тестирование
│   └── DB.erd            # Диаграмма базы данных
├── src/
│   ├── app.py             # Главное приложение FastAPI
│   ├── config.py          # Конфигурация
│   ├── database.py        # Настройка базы данных
│   ├── auth/              # Модули аутентификации
│   ├── models/            # SQLAlchemy модели
│   ├── repositories/      # Слой доступа к данным
│   ├── routers/           # API роутеры
│   ├── schemas/           # Pydantic схемы
│   ├── services/          # Бизнес-логика
│   └── utils/             # Утилиты
├── tests/                 # Тесты
├── alembic/              # Миграции базы данных
├── Dockerfile            # Docker образ
├── docker-compose.yml    # Разработка
├── docker-compose.prod.yml # Продакшен
├── pyproject.toml        # Конфигурация проекта
├── .env.example          # Пример переменных окружения
└── Makefile             # Команды управления
```

## Переменные окружения

Создайте `.env` файл на основе `.env.example`:

```env
ENVIRONMENT=development
DATABASE_URL=postgresql://postgres:password@localhost:5432/taskmanager
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
```

## Продакшен

### Запуск в продакшене

```bash
# Создать .env файл для продакшена
cp .env.example .env

# Установить переменные для продакшена
export POSTGRES_PASSWORD=secure_password

# Запустить
docker-compose -f docker-compose.prod.yml up -d

# Или через Makefile
make prod-up
```

## API Endpoints

- `GET /` - Главная страница
- `GET /health` - Проверка состояния
- `GET /docs` - Swagger документация
- `GET /tasks` - Список задач
- `POST /tasks` - Создание задачи

## Разработка

### Добавление новых зависимостей

```bash
# Добавить зависимость
uv add package-name

# Добавить dev зависимость
uv add --dev package-name

# Синхронизировать
uv sync
```

### Тестирование

```bash
# Запустить тесты
uv run pytest

# С покрытием
uv run pytest --cov=src
```

### Линтинг и форматирование

```bash
# Форматирование кода
uv run black src/
uv run isort src/

# Проверка линтером
uv run flake8 src/
```

## Troubleshooting

### Проблемы с Docker

```bash
# Пересобрать без кэша
docker-compose build --no-cache

# Удалить все контейнеры и volumes
make reset
```

### Проблемы с базой данных

```bash
# Подключиться к PostgreSQL
docker-compose exec db psql -U postgres -d taskmanager

# Посмотреть логи базы данных
docker-compose logs db
```