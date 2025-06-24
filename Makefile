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
