#!/bin/bash

# Скрипт для запуска миграций Alembic
# Использует переменные окружения для подключения к БД

set -e

echo "Running Alembic migrations..."

# Проверяем, что DATABASE_URL установлен
if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: DATABASE_URL environment variable is not set"
    exit 1
fi

echo "Using database URL: $DATABASE_URL"

# Запускаем миграции
alembic upgrade head

echo "Migrations completed successfully!"
