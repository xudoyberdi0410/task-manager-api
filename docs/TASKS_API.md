# Task Manager API - Управление задачами

Этот документ описывает API эндпоинты для работы с задачами в Task Manager API.

## Базовый URL

```
/api/tasks
```

## Аутентификация

Все эндпоинты требуют аутентификации с помощью Bearer токена в заголовке `Authorization`.

```
Authorization: Bearer <your_jwt_token>
```

## Модель задачи

### Статусы задач
- `todo` - К выполнению
- `in_progress` - В процессе
- `done` - Выполнено
- `archived` - Архивировано

### Приоритеты задач
- `low` - Низкий
- `medium` - Средний 
- `high` - Высокий
- `urgent` - Срочный

### Структура задачи

```json
{
  "task_id": 1,
  "title": "Название задачи",
  "description": "Описание задачи",
  "status": "todo",
  "priority": "medium",
  "due_date": "2025-12-31T23:59:59",
  "category_id": 1,
  "user_id": 1,
  "created_at": "2025-06-25T10:00:00",
  "updated_at": "2025-06-25T10:00:00"
}
```

## Эндпоинты

### 1. Получить список задач

```http
GET /api/tasks/
```

#### Параметры запроса
- `skip` (int, optional): Количество записей для пропуска (по умолчанию: 0)
- `limit` (int, optional): Максимальное количество записей (по умолчанию: 10, максимум: 100)
- `status` (string, optional): Фильтр по статусу
- `priority` (string, optional): Фильтр по приоритету
- `category_id` (int, optional): Фильтр по категории
- `search` (string, optional): Поиск по названию и описанию

#### Пример запроса

```bash
curl -X GET "http://localhost:8000/api/tasks/?skip=0&limit=10&status=todo" \
  -H "Authorization: Bearer <token>"
```

#### Пример ответа

```json
{
  "tasks": [
    {
      "task_id": 1,
      "title": "Изучить FastAPI",
      "description": "Прочитать документацию и сделать примеры",
      "status": "todo",
      "priority": "high",
      "due_date": "2025-07-01T00:00:00",
      "category_id": 1,
      "user_id": 1,
      "created_at": "2025-06-25T10:00:00",
      "updated_at": "2025-06-25T10:00:00"
    }
  ],
  "total": 15,
  "page": 1,
  "per_page": 10
}
```

### 2. Создать задачу

```http
POST /api/tasks/
```

#### Тело запроса

```json
{
  "title": "Название задачи",
  "description": "Описание задачи (опционально)",
  "status": "todo",
  "priority": "medium",
  "due_date": "2025-12-31T23:59:59",
  "category_id": 1
}
```

#### Пример запроса

```bash
curl -X POST "http://localhost:8000/api/tasks/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Новая задача",
    "description": "Описание новой задачи",
    "priority": "high",
    "category_id": 1
  }'
```

### 3. Получить задачу по ID

```http
GET /api/tasks/{task_id}
```

#### Пример запроса

```bash
curl -X GET "http://localhost:8000/api/tasks/1" \
  -H "Authorization: Bearer <token>"
```

### 4. Обновить задачу

```http
PUT /api/tasks/{task_id}
```

#### Тело запроса

```json
{
  "title": "Обновленное название",
  "description": "Обновленное описание",
  "status": "in_progress",
  "priority": "high",
  "due_date": "2025-07-15T23:59:59",
  "category_id": 2
}
```

#### Пример запроса

```bash
curl -X PUT "http://localhost:8000/api/tasks/1" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Обновленная задача",
    "status": "in_progress"
  }'
```

### 5. Обновить статус задачи

```http
PATCH /api/tasks/{task_id}/status?new_status={status}
```

#### Пример запроса

```bash
curl -X PATCH "http://localhost:8000/api/tasks/1/status?new_status=done" \
  -H "Authorization: Bearer <token>"
```

### 6. Удалить задачу

```http
DELETE /api/tasks/{task_id}
```

#### Пример запроса

```bash
curl -X DELETE "http://localhost:8000/api/tasks/1" \
  -H "Authorization: Bearer <token>"
```

### 7. Поиск задач

```http
GET /api/tasks/search?q={query}
```

#### Параметры запроса
- `q` (string): Поисковый запрос
- `skip` (int, optional): Количество записей для пропуска
- `limit` (int, optional): Максимальное количество записей

#### Пример запроса

```bash
curl -X GET "http://localhost:8000/api/tasks/search?q=FastAPI" \
  -H "Authorization: Bearer <token>"
```

### 8. Получить задачи по статусу

```http
GET /api/tasks/status/{status}
```

#### Пример запроса

```bash
curl -X GET "http://localhost:8000/api/tasks/status/todo" \
  -H "Authorization: Bearer <token>"
```

### 9. Получить задачи по категории

```http
GET /api/tasks/category/{category_id}
```

#### Пример запроса

```bash
curl -X GET "http://localhost:8000/api/tasks/category/1" \
  -H "Authorization: Bearer <token>"
```

### 10. Получить просроченные задачи

```http
GET /api/tasks/overdue
```

#### Пример запроса

```bash
curl -X GET "http://localhost:8000/api/tasks/overdue" \
  -H "Authorization: Bearer <token>"
```

### 11. Получить статистику задач

```http
GET /api/tasks/statistics
```

#### Пример ответа

```json
{
  "total": 25,
  "todo": 10,
  "in_progress": 5,
  "done": 8,
  "archived": 2,
  "overdue": 3
}
```

#### Пример запроса

```bash
curl -X GET "http://localhost:8000/api/tasks/statistics" \
  -H "Authorization: Bearer <token>"
```

## Массовые операции

### 12. Массовое обновление статуса

```http
PATCH /api/tasks/bulk/status
```

#### Тело запроса

```json
{
  "task_ids": [1, 2, 3],
  "new_status": "done"
}
```

#### Пример запроса

```bash
curl -X PATCH "http://localhost:8000/api/tasks/bulk/status" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "task_ids": [1, 2, 3],
    "new_status": "done"
  }'
```

### 13. Массовое удаление задач

```http
DELETE /api/tasks/bulk
```

#### Тело запроса

```json
{
  "task_ids": [1, 2, 3]
}
```

#### Пример ответа

```json
{
  "deleted_count": 3,
  "failed_ids": [],
  "total_requested": 3
}
```

#### Пример запроса

```bash
curl -X DELETE "http://localhost:8000/api/tasks/bulk" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "task_ids": [1, 2, 3]
  }'
```

## Коды ошибок

- `200` - Успешный запрос
- `201` - Ресурс создан
- `204` - Успешное удаление (без содержимого)
- `400` - Неверный запрос
- `401` - Не авторизован
- `404` - Ресурс не найден
- `422` - Ошибка валидации данных

## Примеры использования

### Создание задачи с категорией

```python
import requests

# Получение токена (предполагается, что вы уже авторизованы)
headers = {"Authorization": "Bearer your_jwt_token"}

# Создание задачи
task_data = {
    "title": "Изучить Python",
    "description": "Пройти онлайн курс по Python",
    "priority": "high",
    "due_date": "2025-07-15T23:59:59",
    "category_id": 1
}

response = requests.post(
    "http://localhost:8000/api/tasks/",
    json=task_data,
    headers=headers
)

if response.status_code == 201:
    task = response.json()
    print(f"Задача создана с ID: {task['task_id']}")
```

### Получение задач с фильтрацией

```python
import requests

headers = {"Authorization": "Bearer your_jwt_token"}

# Получение задач со статусом "todo" и высоким приоритетом
params = {
    "status": "todo",
    "priority": "high",
    "limit": 20
}

response = requests.get(
    "http://localhost:8000/api/tasks/",
    params=params,
    headers=headers
)

if response.status_code == 200:
    data = response.json()
    print(f"Найдено {data['total']} задач")
    for task in data['tasks']:
        print(f"- {task['title']} ({task['priority']})")
```

### Обновление статуса нескольких задач

```python
import requests

headers = {"Authorization": "Bearer your_jwt_token"}

# Массовое обновление статуса
bulk_data = {
    "task_ids": [1, 2, 3, 4, 5],
    "new_status": "done"
}

response = requests.patch(
    "http://localhost:8000/api/tasks/bulk/status",
    json=bulk_data,
    headers=headers
)

if response.status_code == 200:
    updated_tasks = response.json()
    print(f"Обновлено {len(updated_tasks)} задач")
```
