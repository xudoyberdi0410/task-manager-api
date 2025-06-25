# Makefile для управления Docker контейнерами

# Переменные
COMPOSE_FILE=docker-compose.yml
COMPOSE_PROD_FILE=docker-compose.prod.yml
COMPOSE_SERVICES_FILE=docker-compose.services.yml

# Команды для разработки
.PHONY: help
help: ## Показать справку
	@echo "Доступные команды:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: build
build: ## Собрать Docker образ
	docker compose build

.PHONY: up
up: ## Запустить сервисы в режиме разработки
	docker compose up -d

.PHONY: services
services: ## Запустить только базы данных и сервисы (для локальной разработки)
	docker compose -f $(COMPOSE_SERVICES_FILE) up -d

.PHONY: services-down
services-down: ## Остановить только сервисы
	docker compose -f $(COMPOSE_SERVICES_FILE) down

.PHONY: services-logs
services-logs: ## Показать логи сервисов
	docker compose -f $(COMPOSE_SERVICES_FILE) logs -f

.PHONY: dev-local
dev-local: services ## Запустить сервисы в Docker и показать команду для локального запуска API
	@echo "Сервисы запущены! Теперь запустите API локально:"
	@echo "  uv run uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload"
	@echo ""
	@echo "Доступные сервисы:"
	@echo "  - PostgreSQL: localhost:5432"
	@echo "  - Redis: localhost:6379"
	@echo "  - pgAdmin: http://localhost:5050"

.PHONY: down
down: ## Остановить сервисы
	docker compose down

.PHONY: logs
logs: ## Показать логи всех сервисов
	docker compose logs -f

.PHONY: logs-api
logs-api: ## Показать логи API
	docker compose logs -f api

.PHONY: shell
shell: ## Подключиться к контейнеру API
	docker compose exec api bash

.PHONY: test
test: ## Запустить тесты
	docker compose exec api uv run pytest

.PHONY: lint
lint: ## Проверить код линтером
	docker compose exec api uv run flake8 src/
	docker compose exec api uv run black --check src/

.PHONY: format
format: ## Отформатировать код
	docker compose exec api uv run black src/
	docker compose exec api uv run isort src/

# Команды для продакшена
.PHONY: prod-build
prod-build: ## Собрать образ для продакшена
	docker compose -f $(COMPOSE_PROD_FILE) build

.PHONY: prod-up
prod-up: ## Запустить в продакшене
	docker compose -f $(COMPOSE_PROD_FILE) up -d

.PHONY: prod-down
prod-down: ## Остановить продакшен
	docker compose -f $(COMPOSE_PROD_FILE) down

.PHONY: prod-logs
prod-logs: ## Логи продакшена
	docker compose -f $(COMPOSE_PROD_FILE) logs -f

# Утилиты
.PHONY: clean
clean: ## Очистить Docker ресурсы
	docker compose down -v --remove-orphans
	docker system prune -f

.PHONY: reset
reset: ## Полный сброс (удалить все данные)
	docker compose down -v --remove-orphans
	docker volume rm $$(docker volume ls -q | grep task-manager) 2>/dev/null || true
	docker compose build --no-cache

.PHONY: init
init: ## Первоначальная настройка проекта
	cp .env.example .env
	uv sync
	docker compose build
	docker compose up -d

# Команды для локальной разработки (без Docker)
.PHONY: install
install: ## Установить зависимости
	uv sync

.PHONY: dev
dev: ## Установить зависимости для разработки
	uv sync --dev

.PHONY: run-local
run-local: ## Запустить API локально
	uv run uvicorn src.app:app --reload --host 0.0.0.0 --port 8000

.PHONY: test-local
test-local: ## Запустить тесты локально
	uv run pytest tests/ -v

.PHONY: test-verbose
test-verbose: ## Запустить тесты с подробным выводом
	uv run pytest tests/ -v -s

.PHONY: test-auth
test-auth: ## Запустить тесты аутентификации
	uv run pytest tests/test_users.py -v -k "auth or register or login"

.PHONY: test-users
test-users: ## Запустить тесты пользователей
	uv run pytest tests/test_users.py -v

.PHONY: test-repositories
test-repositories: ## Запустить тесты репозиториев
	uv run pytest tests/test_repositories.py -v

.PHONY: test-services
test-services: ## Запустить тесты сервисов
	uv run pytest tests/test_services.py -v

.PHONY: test-coverage
test-coverage: ## Запустить тесты с покрытием кода
	uv run pytest tests/ --cov=src --cov-report=html --cov-report=term

.PHONY: lint-local
lint-local: ## Проверить код линтерами локально
	uv run flake8 src/ tests/
	uv run mypy src/ --explicit-package-bases --ignore-missing-imports

.PHONY: format-local
format-local: ## Отформатировать код локально
	uv run black src/ tests/
	uv run isort src/ tests/

.PHONY: clean-local
clean-local: ## Очистить временные файлы
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf test.db
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

.PHONY: db-upgrade-local
db-upgrade-local: ## Применить миграции локально
	uv run alembic upgrade head

.PHONY: db-migrate-local
db-migrate-local: ## Создать новую миграцию локально
	@read -p "Enter migration message: " MESSAGE; \
	uv run alembic revision --autogenerate -m "$$MESSAGE"

# Команды для CI/CD и инструментов разработки
.PHONY: ci-install
ci-install: ## Установить зависимости для CI (включая dev)
	uv pip install --system -e ".[dev]"

.PHONY: ci-test
ci-test: ## Запустить тесты в CI окружении
	python -m pytest tests/ -v --tb=short --cov=src --cov-report=html --cov-report=term-missing

.PHONY: ci-lint
ci-lint: ## Запустить линтеры в CI окружении
	ruff check src/ tests/
	black --check src/ tests/
	mypy src/ --explicit-package-bases --ignore-missing-imports

.PHONY: ci-security
ci-security: ## Запустить проверки безопасности
	bandit -r src/ -f json -o bandit-report.json || true
	safety check --json --output safety-report.json || true

.PHONY: format
format: ## Автоматически отформатировать код
	ruff format src/ tests/
	black src/ tests/

.PHONY: lint
lint: ## Запустить все проверки кода
	ruff check src/ tests/
	black --check src/ tests/
	mypy src/ --explicit-package-bases --ignore-missing-imports

.PHONY: security
security: ## Запустить проверки безопасности
	bandit -r src/
	safety check

.PHONY: pre-commit
pre-commit: format lint test-local ## Выполнить все проверки перед коммитом

.PHONY: docker-build
docker-build: ## Собрать Docker образ
	docker build -t task-manager-api:latest .

.PHONY: docker-run
docker-run: ## Запустить Docker контейнер
	docker run -p 8000:8000 --env-file .env task-manager-api:latest

.PHONY: check-deps
check-deps: ## Проверить зависимости на уязвимости
	pip-audit --desc
	safety check
