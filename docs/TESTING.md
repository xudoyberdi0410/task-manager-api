# Руководство по тестированию Task Manager API

## Обзор

Проект использует pytest для тестирования всех компонентов системы аутентификации. Тесты покрывают:
- Репозитории (доступ к данным)
- Сервисы (бизнес-логика)
- API эндпоинты (интеграционные тесты)

## Структура тестов

```
tests/
├── __init__.py
├── conftest.py           # Общие фикстуры и настройки
├── test_users.py         # Тесты эндпоинтов аутентификации и пользователей
├── test_repositories.py  # Тесты репозиториев
├── test_services.py      # Тесты сервисов
├── test_tasks_api.py     # Тесты API задач
├── test_tasks_security.py # Тесты безопасности API задач
└── test_task_service_security.py # Тесты безопасности сервисного слоя
```

## Запуск тестов

### Все тесты
```bash
make test-local
# или
uv run pytest tests/ -v
```

### Конкретные группы тестов
```bash
make test-auth          # Тесты аутентификации (test_users.py)
make test-users         # Тесты пользователей  
make test-repositories  # Тесты репозиториев
make test-services      # Тесты сервисов
```

### Тесты безопасности
```bash
# Тесты безопасности API задач
uv run pytest tests/test_tasks_security.py -v

# Тесты безопасности сервисного слоя
uv run pytest tests/test_task_service_security.py -v

# Все тесты безопасности
uv run pytest tests/test_*security.py -v
```

### С подробным выводом
```bash
make test-verbose
# или
uv run pytest tests/ -v -s
```

### С покрытием кода
```bash
make test-coverage
# или
uv run pytest tests/ --cov=src --cov-report=html --cov-report=term
```

## Описание тестов

### test_users.py - Тесты аутентификации и пользователей
- `test_register_user` - Регистрация нового пользователя
- `test_register_duplicate_email` - Проверка дублирования email
- `test_register_duplicate_username` - Проверка дублирования username
- `test_login_success` - Успешный вход в систему
- `test_login_wrong_email` - Вход с неправильным email
- `test_login_wrong_password` - Вход с неправильным паролем
- `test_login_without_registration` - Вход без регистрации
- `test_get_current_user_success` - Получение информации о пользователе
- `test_get_current_user_without_token` - Доступ без токена
- `test_get_current_user_invalid_token` - Доступ с невалидным токеном
- `test_get_user_tasks` - Получение задач пользователя
- `test_different_users_isolation` - Изоляция данных пользователей

### test_repositories.py - Тесты репозиториев
- `test_create_user` - Создание пользователя
- `test_get_user_by_email` - Поиск по email
- `test_get_user_by_username` - Поиск по username
- `test_exists_by_email` - Проверка существования по email
- `test_exists_by_username` - Проверка существования по username
- `test_update_user` - Обновление данных пользователя
- `test_delete_user` - Удаление пользователя

### test_services.py - Тесты сервисов
- `test_user_service_register_success` - Успешная регистрация
- `test_user_service_register_duplicate_*` - Проверки дублирования
- `test_auth_service_authenticate_*` - Тесты аутентификации
- `test_auth_service_login_*` - Тесты входа в систему

### test_tasks_security.py - Тесты безопасности API задач
- `test_cannot_access_other_user_task` - Защита от доступа к чужим задачам
- `test_cannot_update_other_user_task` - Защита от обновления чужих задач
- `test_cannot_delete_other_user_task` - Защита от удаления чужих задач
- `test_tasks_isolation_in_list` - Изоляция задач в списках
- `test_bulk_operations_isolation` - Безопасность массовых операций
- `test_search_isolation` - Изоляция в поиске
- `test_category_tasks_isolation` - Защита задач по категориям

### test_task_service_security.py - Тесты безопасности сервисного слоя
- `test_get_task_by_id_security` - Проверка доступа по ID
- `test_update_task_security` - Безопасность обновления
- `test_delete_task_security` - Безопасность удаления
- `test_bulk_operations_security` - Массовые операции безопасности
- `test_get_task_statistics_isolation` - Изоляция статистики

## Фикстуры

### conftest.py содержит следующие фикстуры:

- `db_session` - Тестовая сессия базы данных (SQLite в памяти)
- `client` - Тестовый клиент FastAPI
- `test_user_data` - Данные тестового пользователя
- `another_user_data` - Данные второго пользователя
- `test_user` - Объект тестового пользователя для unit-тестов
- `another_user` - Объект второго пользователя для unit-тестов
- `auth_headers` - Заголовки авторизации первого пользователя
- `another_user_headers` - Заголовки авторизации второго пользователя

## Конфигурация

Тесты используют:
- **SQLite в памяти** для быстрой изоляции
- **Автоматическое создание/удаление таблиц** для каждого теста
- **Переопределение зависимостей** FastAPI для тестовой БД
- **Изоляцию тестов** - каждый тест начинается с чистой БД

## Примеры запуска

### Разработка
```bash
# Установка зависимостей
make install

# Запуск всех тестов
make test-local

# Запуск с покрытием
make test-coverage

# Запуск конкретного файла
uv run pytest tests/test_users.py -v

# Запуск конкретного теста
uv run pytest tests/test_users.py::test_register_user -v
```

### CI/CD
```bash
# Для CI окружения
uv run pytest tests/ --cov=src --cov-report=xml --junitxml=test-results.xml
```

## Добавление новых тестов

1. **Тесты эндпоинтов** - добавлять в соответствующий файл test_*.py
2. **Тесты репозиториев** - в test_repositories.py
3. **Тесты сервисов** - в test_services.py
4. **Новые фикстуры** - в conftest.py

### Пример нового теста:
```python
def test_new_functionality(client: TestClient, test_user_data):
    """Тест новой функциональности"""
    # Подготовка данных
    token = get_access_token(client, test_user_data)
    
    # Выполнение запроса
    response = client.get("/api/new-endpoint", 
                         headers={"Authorization": f"Bearer {token}"})
    
    # Проверка результата
    assert response.status_code == 200
    assert "expected_field" in response.json()
```

## Отладка тестов

### Для отладки используйте:
```bash
# Остановка на первой ошибке
uv run pytest tests/ -x

# Подробный вывод
uv run pytest tests/ -v -s

# Запуск конкретного теста с выводом
uv run pytest tests/test_users.py::test_register_user -v -s

# С дополнительной информацией
uv run pytest tests/ --tb=long
```

## Покрытие кода

После запуска с покрытием:
```bash
make test-coverage
```

Откройте `htmlcov/index.html` в браузере для детального отчета.

## Интеграция с IDE

### VS Code
Установите расширение Python Test Explorer для запуска тестов из интерфейса.

### PyCharm
Pytest поддерживается по умолчанию. Настройте интерпретатор проекта на uv.

## Лучшие практики

1. **Изоляция тестов** - каждый тест должен быть независимым
2. **Понятные имена** - названия тестов должны описывать что проверяется
3. **Подготовка данных** - используйте фикстуры для подготовки данных
4. **Проверка результатов** - всегда проверяйте как успешные, так и ошибочные сценарии
5. **Документация** - добавляйте docstring к сложным тестам
