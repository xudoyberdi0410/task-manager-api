# Task Manager API

[![CI/CD](https://github.com/xudoyberdi0410/task-manager-api/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/xudoyberdi0410/task-manager-api/actions/workflows/ci-cd.yml)
[![Security Check](https://github.com/xudoyberdi0410/task-manager-api/actions/workflows/dependency-check.yml/badge.svg)](https://github.com/xudoyberdi0410/task-manager-api/actions/workflows/dependency-check.yml)

FastAPI приложение для управления задачами с использованием uv для управления зависимостями.

## Документация

📚 **Полная документация находится в папке [docs/](docs/)**

- [**Swagger Documentation**](docs/SWAGGER_DOCUMENTATION.md) - **🔥 Подробная документация по Swagger UI**
- [Локальная разработка](docs/LOCAL_DEVELOPMENT.md) - Подробное руководство по разработке
- [Система аутентификации](docs/AUTH_GUIDE.md) - Как работает аутентификация
- [Тестирование](docs/TESTING.md) - Руководство по тестированию  
- [API задач](docs/TASKS_API.md) - Документация API для работы с задачами
- [Безопасность задач](docs/TASKS_SECURITY.md) - Система безопасности и изоляции данных
- [Настройка CI/CD](docs/CI_CD_SETUP.md) - Пошаговая настройка CI/CD
- [GitHub Actions CI/CD](docs/GITHUB_ACTIONS.md) - Использование GitHub Actions
- [Инструменты разработки](docs/DEV_TOOLS_SETUP.md) - Установка dev tools

## Технологии

- **FastAPI** - веб-фреймворк
- **uv** - менеджер пакетов Python
- **PostgreSQL** - база данных
- **Docker** - контейнеризация
- **GitHub Actions** - CI/CD

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
- **🔥 Swagger UI**: http://localhost:8000/docs - Интерактивная документация API
- **ReDoc**: http://localhost:8000/redoc - Альтернативная документация
- **pgAdmin**: http://localhost:5050 (admin@admin.com / admin)

#### 📖 Быстрый тест API через Swagger

1. Откройте http://localhost:8000/docs
2. Зарегистрируйтесь: `POST /auth/register`
3. Получите токен: `POST /token`
4. Нажмите "Authorize" и введите: `Bearer <ваш_токен>`
5. Теперь можете тестировать все защищенные эндпоинты!

## CI/CD

Проект использует GitHub Actions для автоматизации:

- **Тестирование** - автоматический запуск тестов
- **Линтинг** - проверка качества кода (ruff, black, mypy)
- **Безопасность** - сканирование уязвимостей (bandit, safety)
- **Docker** - автоматическая сборка и публикация образов
- **Развертывание** - автодеплой в staging и production

### Рабочий процесс

1. **Разработка** в ветке `feature/*` или `develop`
2. **Pull Request** запускает все проверки
3. **Merge в develop** → автоматический деплой в staging
4. **Merge в main** → автоматический деплой в production
5. **Теги версии** → создание релизов

### Локальные проверки

```bash
# Запустить все CI проверки локально
./scripts/ci-check.sh

# Или по отдельности
make format-local   # Форматирование кода
make lint-local     # Линтинг
make security       # Проверка безопасности
make test-local     # Тесты
make pre-commit     # Все проверки перед коммитом
```

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
- `GET /api/tasks` - Список задач
- `POST /api/tasks` - Создание задачи
- `POST /auth/register` - Регистрация пользователя
- `POST /token` - Получение JWT токена

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
uv run black src/ tests/
uv run isort src/ tests/

# Проверка линтером
uv run ruff check src/ tests/
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