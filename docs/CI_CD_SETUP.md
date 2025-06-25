# Настройка CI/CD для Task Manager API

Этот документ описывает процесс настройки системы непрерывной интеграции и развертывания (CI/CD) для проекта Task Manager API с использованием GitHub Actions.

## Предварительные требования

1. **GitHub репозиторий** с проектом Task Manager API
2. **Права администратора** на репозиторий для настройки секретов и environments
3. **Docker Hub или GitHub Container Registry** для публикации образов (опционально)

## Быстрая настройка

### 1. Активация GitHub Actions

GitHub Actions активируется автоматически при наличии файлов workflow в директории `.github/workflows/`. 

В проекте уже настроены следующие workflows:
- `.github/workflows/ci-cd.yml` - Основной CI/CD пайплайн
- `.github/workflows/release.yml` - Создание релизов
- `.github/workflows/dependency-check.yml` - Проверка безопасности зависимостей

### 2. Настройка Environments (Рекомендуется)

1. Перейдите в **Settings** → **Environments** в вашем GitHub репозитории
2. Создайте два environment:
   - `staging` - для тестовой среды
   - `production` - для продакшена

3. Для каждого environment настройте:
   - **Protection rules** (опционально):
     - Required reviewers для production
     - Wait timer для production
   - **Environment secrets** (если требуются специфичные для среды секреты)

### 3. Настройка секретов (Если требуется деплой)

Если планируете автоматический деплой, добавьте необходимые секреты в **Settings** → **Secrets and variables** → **Actions**:

```
DEPLOY_HOST          # Хост для деплоя
DEPLOY_USER          # Пользователь для деплоя  
DEPLOY_KEY           # SSH ключ или токен
DATABASE_URL         # URL продакшн базы данных
SECRET_KEY          # Секретный ключ для JWT
```

## Конфигурация Workflows

### CI/CD Pipeline (`ci-cd.yml`)

**Триггеры:**
- Push в ветки `main` и `develop`
- Pull Request в ветки `main` и `develop`

**Этапы:**
1. **Test** - Запуск тестов с PostgreSQL в Docker
2. **Lint** - Проверка кода (ruff, black, mypy)
3. **Security** - Сканирование безопасности (bandit, safety)
4. **Build** - Сборка Docker образа (только при push)
5. **Deploy Staging** - Деплой в staging (при push в develop)
6. **Deploy Production** - Деплой в production (при push в main)

### Release Workflow (`release.yml`)

**Триггеры:**
- Создание тегов вида `v*` (например, `v1.0.0`)

**Действия:**
- Создание GitHub Release с автоматическим changelog
- Сборка и публикация Docker образа с версионными тегами

### Dependency Check (`dependency-check.yml`)

**Расписание:**
- Каждый понедельник в 9:00 UTC
- Можно запустить вручную

**Действия:**
- Сканирование зависимостей на уязвимости
- Создание issue при обнаружении проблем

## Локальная проверка перед коммитом

Запустите локальные проверки перед push:

```bash
# Установка зависимостей для разработки
uv sync

# Запуск всех проверок
./scripts/ci-check.sh

# Или по отдельности:
uv run ruff check src/ tests/         # Линтинг
uv run black src/ tests/              # Форматирование
uv run mypy src/                      # Проверка типов
uv run bandit -r src/                 # Безопасность
uv run pytest tests/                  # Тесты
```

## Workflow с ветками

### Рекомендуемый GitFlow:

1. **Разработка новых функций:**
   ```bash
   git checkout -b feature/new-feature
   # ... разработка
   git push origin feature/new-feature
   # Создать Pull Request в develop
   ```

2. **Тестирование в staging:**
   ```bash
   # После merge в develop
   git checkout develop
   git pull origin develop
   # Автоматический деплой в staging
   ```

3. **Релиз в продакшен:**
   ```bash
   # Создать Pull Request из develop в main
   # После merge в main
   git checkout main
   git pull origin main
   git tag v1.0.0
   git push origin v1.0.0
   # Автоматический деплой в production и создание релиза
   ```

## Мониторинг и отладка

### Просмотр статуса

1. **GitHub Actions** - вкладка Actions в репозитории
2. **Статус badges** - в README.md отображаются текущие статусы
3. **Environments** - в разделе Environments видны статусы развертываний

### Отладка при ошибках

1. **Просмотр логов:**
   - Перейдите в Actions → выберите workflow → выберите job
   - Разверните шаги для просмотра подробных логов

2. **Локальное воспроизведение:**
   ```bash
   # Запустить те же команды локально
   ./scripts/ci-check.sh
   
   # Сборка Docker образа
   docker build -t task-manager-api .
   ```

3. **Отладка тестов:**
   ```bash
   # Запуск тестов с подробным выводом
   uv run pytest tests/ -v -s
   
   # Тесты с покрытием
   uv run pytest tests/ --cov=src --cov-report=html
   ```

## Кастомизация

### Изменение условий запуска

Отредактируйте секцию `on:` в соответствующем workflow:

```yaml
on:
  push:
    branches: [ main, develop, feature/* ]
  pull_request:
    branches: [ main ]
```

### Добавление новых проверок

Добавьте новый job в workflow:

```yaml
custom-check:
  name: Custom Check
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Run custom check
      run: |
        echo "Custom logic here"
```

### Настройка деплоя

Отредактируйте jobs деплоя под вашу инфраструктуру:

```yaml
deploy-production:
  name: Deploy to Production
  if: github.ref == 'refs/heads/main'
  environment: production
  steps:
    - name: Deploy to server
      run: |
        # SSH в сервер и деплой
        ssh user@server 'cd /app && git pull && docker-compose up -d'
```

## Безопасность

1. **Никогда не коммитьте секреты** в код
2. **Используйте GitHub Secrets** для хранения чувствительных данных
3. **Настройте protection rules** для production environment
4. **Регулярно обновляйте зависимости** на основе результатов dependency-check
5. **Используйте минимальные права доступа** для токенов

## Troubleshooting

### Частые проблемы:

1. **Сбой тестов:**
   - Проверьте, что тесты проходят локально
   - Убедитесь в совместимости версий зависимостей

2. **Сбой линтинга:**
   ```bash
   # Запустить и исправить локально
   uv run ruff check src/ tests/ --fix
   uv run black src/ tests/
   ```

3. **Проблемы с Docker:**
   - Проверьте Dockerfile на синтаксические ошибки
   - Убедитесь, что .dockerignore настроен правильно

4. **Проблемы с секретами:**
   - Убедитесь, что все необходимые секреты добавлены
   - Проверьте права доступа GITHUB_TOKEN

Подробнее о GitHub Actions CI/CD см. в [GITHUB_ACTIONS.md](GITHUB_ACTIONS.md).
