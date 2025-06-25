# GitHub Actions CI/CD

Этот проект использует GitHub Actions для автоматизации процессов непрерывной интеграции и развертывания (CI/CD).

## Обзор Workflows

### 1. CI/CD Pipeline (`.github/workflows/ci-cd.yml`)

Основной workflow, который запускается при каждом push и pull request в ветки `main` и `develop`.

**Этапы:**
- **Test**: Запуск тестов с PostgreSQL
- **Lint**: Проверка кода с помощью ruff, black, mypy
- **Security**: Сканирование безопасности с bandit и safety
- **Build**: Сборка и публикация Docker образа
- **Deploy**: Развертывание в staging (develop) и production (main)

### 2. Release (`.github/workflows/release.yml`)

Создание релизов при создании тегов версии.

**Триггеры:**
- Push тегов в формате `v*` (например, `v1.0.0`)

**Действия:**
- Создание GitHub Release с changelog
- Сборка и публикация Docker образа с тегами версии

### 3. Dependency Check (`.github/workflows/dependency-check.yml`)

Еженедельная проверка зависимостей на уязвимости.

**Расписание:**
- Каждый понедельник в 9:00 UTC
- Можно запустить вручную

**Действия:**
- Сканирование зависимостей с pip-audit и safety
- Создание issue при обнаружении уязвимостей

## Настройка

### 1. Секреты GitHub

Для работы workflows необходимо настроить следующие секреты в репозитории:

- `GITHUB_TOKEN` - автоматически предоставляется GitHub
- Дополнительные секреты для развертывания (настраиваются по необходимости)

### 2. Environments

Рекомендуется создать environments в GitHub для staging и production:

1. Перейдите в Settings → Environments
2. Создайте `staging` и `production` environments
3. Настройте protection rules при необходимости

### 3. Docker Registry

По умолчанию используется GitHub Container Registry (ghcr.io). Docker образы публикуются автоматически при успешной сборке.

## Локальная разработка

### Установка инструментов разработки

```bash
# Установка зависимостей для разработки
uv pip install --system -e ".[dev]"
```

### Запуск проверок локально

```bash
# Линтинг
ruff check src/ tests/
ruff format src/ tests/

# Форматирование
black src/ tests/

# Проверка типов
mypy src/

# Безопасность
bandit -r src/
safety check

# Тесты
pytest tests/ -v --cov=src
```

## Использование

### Создание Pull Request

1. Создайте ветку от `develop`
2. Внесите изменения
3. Убедитесь, что все проверки проходят локально
4. Создайте Pull Request в `develop`
5. После ревью и merge в `develop`, изменения автоматически развернутся в staging

### Создание Release

1. Убедитесь, что все изменения в `develop` протестированы
2. Создайте Pull Request из `develop` в `main`
3. После merge в `main` создайте тег версии:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
4. Автоматически создастся GitHub Release и образ будет опубликован

### Мониторинг

- Просматривайте результаты workflows в разделе Actions
- Следите за issues, создаваемыми dependency check
- Проверяйте логи развертывания в соответствующих environments

## Кастомизация

### Изменение условий запуска

Отредактируйте секцию `on:` в соответствующем workflow файле:

```yaml
on:
  push:
    branches: [ main, develop, feature/* ]
  pull_request:
    branches: [ main ]
```

### Добавление новых проверок

Добавьте новый job в `.github/workflows/ci-cd.yml`:

```yaml
new-check:
  name: New Check
  runs-on: ubuntu-latest
  steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Run custom check
      run: |
        echo "Custom check logic"
```

### Настройка развертывания

Отредактируйте jobs `deploy-staging` и `deploy-production` в соответствии с вашей инфраструктурой:

```yaml
deploy-production:
  name: Deploy to Production
  runs-on: ubuntu-latest
  needs: [build]
  if: github.ref == 'refs/heads/main'
  environment: production
  
  steps:
    - name: Deploy
      run: |
        # Команды для развертывания
        kubectl apply -f k8s/
```

## Troubleshooting

### Сбой тестов

1. Проверьте логи в разделе Actions
2. Убедитесь, что тесты проходят локально
3. Проверьте совместимость зависимостей

### Сбой сборки Docker

1. Проверьте Dockerfile на синтаксические ошибки
2. Убедитесь, что все необходимые файлы включены в контекст сборки
3. Проверьте наличие .dockerignore файла

### Проблемы с развертыванием

1. Проверьте настройки environments
2. Убедитесь, что все необходимые секреты настроены
3. Проверьте права доступа для GITHUB_TOKEN
