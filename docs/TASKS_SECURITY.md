# Безопасность задач в Task Manager API

## Обзор

В Task Manager API реализована многоуровневая система защиты для обеспечения изоляции задач между пользователями. Каждый пользователь может видеть и управлять только своими задачами.

## Архитектура безопасности

### 1. Аутентификация (Уровень API)
- Все эндпоинты задач требуют валидный JWT токен
- Токен содержит информацию о пользователе (`user_id`)
- Использование dependency `get_current_user` во всех роутах

```python
@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: UserInDB = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """Получить задачу по ID"""
    task = task_service.get_task_by_id(task_id, current_user.user_id)
    return task
```

### 2. Авторизация (Уровень Сервиса)
- Все методы сервиса принимают `user_id` как обязательный параметр
- Проверка принадлежности задачи пользователю перед любой операцией
- Возврат HTTP 404 при попытке доступа к чужой задаче

```python
def get_task_by_id(self, task_id: int, user_id: int) -> Optional[Task]:
    """Получить задачу по ID"""
    task = self.task_repo.get_by_id(task_id, user_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task
```

### 3. Фильтрация данных (Уровень Репозитория)
- Все SQL-запросы включают фильтр по `user_id`
- Невозможность получить данные чужих пользователей на уровне БД

```python
def get_by_id(self, task_id: int, user_id: int) -> Optional[Task]:
    """Получить задачу по ID для конкретного пользователя"""
    return (
        self.db.query(Task)
        .filter(Task.task_id == task_id, Task.user_id == user_id)
        .first()
    )
```

## Защищенные операции

### CRUD операции
- ✅ **Создание**: Задача автоматически связывается с текущим пользователем
- ✅ **Чтение**: Доступ только к собственным задачам
- ✅ **Обновление**: Обновление только собственных задач
- ✅ **Удаление**: Удаление только собственных задач

### Специальные операции
- ✅ **Поиск**: Поиск только среди собственных задач
- ✅ **Фильтрация**: Фильтрация только собственных задач
- ✅ **Статистика**: Статистика только по собственным задачам
- ✅ **Массовые операции**: Массовые изменения только собственных задач

### Связанные сущности
- ✅ **Категории**: Нельзя назначить задаче чужую категорию
- ✅ **Статусы**: Нельзя изменить статус чужой задачи
- ✅ **Приоритеты**: Нельзя изменить приоритет чужой задачи

## Примеры защиты

### Попытка доступа к чужой задаче
```http
GET /api/tasks/123
Authorization: Bearer <user2_token>

HTTP/1.1 404 Not Found
{
    "detail": "Task not found"
}
```

### Попытка обновления чужой задачи
```http
PUT /api/tasks/123
Authorization: Bearer <user2_token>
Content-Type: application/json

{
    "title": "Hacked Task"
}

HTTP/1.1 404 Not Found
{
    "detail": "Task not found"
}
```

### Массовые операции с чужими задачами
```http
PATCH /api/tasks/bulk/status
Authorization: Bearer <user2_token>
Content-Type: application/json

{
    "task_ids": [123, 124, 125],
    "new_status": "done"
}

HTTP/1.1 400 Bad Request
{
    "detail": "Failed to update tasks with IDs: [123, 124, 125]"
}
```

## Уровни защиты

| Уровень | Компонент | Защита |
|---------|-----------|--------|
| 1 | API Router | JWT аутентификация |
| 2 | Service Layer | Проверка принадлежности |
| 3 | Repository Layer | SQL фильтрация по user_id |
| 4 | Database Model | Foreign Key на user_id |

## Тестирование безопасности

### API тесты (`test_tasks_security.py`)
- Попытки доступа к чужим задачам
- Изоляция в списках и поиске
- Массовые операции безопасности
- Связь с категориями

### Service тесты (`test_task_service_security.py`)
- Проверка исключений при неправомерном доступе
- Изоляция на уровне бизнес-логики
- Статистика и агрегация данных

### Запуск тестов безопасности
```bash
# Тесты API
uv run pytest tests/test_tasks_security.py -v

# Тесты сервисного слоя
uv run pytest tests/test_task_service_security.py -v

# Все тесты безопасности
uv run pytest tests/test_*security.py -v
```

## Рекомендации по безопасности

### Для разработчиков
1. **Всегда передавайте user_id** в методы сервисов и репозиториев
2. **Не доверяйте client-side данным** - всегда проверяйте права доступа
3. **Используйте типизацию** для избежания ошибок с user_id
4. **Тестируйте негативные сценарии** - попытки несанкционированного доступа

### Для администраторов
1. **Мониторинг логов** - отслеживайте 404 ошибки как возможные попытки доступа
2. **Rate limiting** - ограничивайте количество запросов от одного пользователя
3. **Аудит операций** - логируйте все операции с задачами
4. **Резервное копирование** - регулярные бэкапы базы данных

## Возможные улучшения

### Логирование безопасности
```python
import logging

security_logger = logging.getLogger("security")

def get_task_by_id(self, task_id: int, user_id: int):
    task = self.task_repo.get_by_id(task_id, user_id)
    if not task:
        security_logger.warning(
            f"User {user_id} tried to access task {task_id} - not found"
        )
        raise HTTPException(...)
```

### Детальная информация об ошибках (только для разработки)
```python
# Только в development режиме
if settings.environment == "development":
    detail = f"Task {task_id} not found for user {user_id}"
else:
    detail = "Task not found"
```

### Роли и права доступа
```python
# Будущее расширение
class Permission(Enum):
    READ_TASK = "read:task"
    WRITE_TASK = "write:task"
    DELETE_TASK = "delete:task"

@requires_permission(Permission.READ_TASK)
def get_task_by_id(self, task_id: int, user_id: int):
    # ...
```

## Заключение

Система безопасности Task Manager API обеспечивает:
- ✅ Полную изоляцию данных между пользователями
- ✅ Защиту от всех видов несанкционированного доступа
- ✅ Прозрачную обработку ошибок безопасности
- ✅ Комплексное тестирование всех сценариев

Система протестирована и готова к использованию в продакшене.
