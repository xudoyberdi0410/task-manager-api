#!/bin/bash

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода заголовков
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Функция для проверки успешности выполнения команды
check_success() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $1 прошло успешно${NC}"
        return 0
    else
        echo -e "${RED}✗ $1 завершилось с ошибкой${NC}"
        return 1
    fi
}

# Переменная для отслеживания ошибок
ERRORS=0

echo -e "${YELLOW}Запуск локальной CI проверки...${NC}\n"

# 1. Форматирование кода
print_header "Форматирование кода"
uv run ruff format src/ tests/
uv run black src/ tests/
check_success "Форматирование" || ((ERRORS++))

# 2. Линтинг
print_header "Проверка стиля кода (Linting)"
uv run ruff check src/ tests/
check_success "Ruff linting" || ((ERRORS++))

uv run black --check src/ tests/
check_success "Black formatting check" || ((ERRORS++))

# 3. Проверка типов
print_header "Проверка типов (MyPy)"
uv run mypy src/ --explicit-package-bases --ignore-missing-imports
check_success "Type checking" || ((ERRORS++))

# 4. Проверка безопасности
print_header "Проверка безопасности"
uv run bandit -r src/ -ll --skip B104
check_success "Bandit security check" || ((ERRORS++))

uv run pip-audit
check_success "Dependency vulnerability check" || ((ERRORS++))

# 5. Тесты
print_header "Запуск тестов"
uv run pytest tests/ -v --tb=short --cov=src --cov-report=term-missing
check_success "Tests" || ((ERRORS++))

# 6. Сборка Docker образа
print_header "Сборка Docker образа"
docker build -t task-manager-api:ci-test . > /dev/null 2>&1
check_success "Docker build" || ((ERRORS++))

# Результаты
echo -e "\n${BLUE}================================${NC}"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ Все проверки прошли успешно!${NC}"
    echo -e "${GREEN}Код готов для коммита.${NC}"
    exit 0
else
    echo -e "${RED}✗ Обнаружено $ERRORS ошибок${NC}"
    echo -e "${RED}Исправьте ошибки перед коммитом.${NC}"
    exit 1
fi
