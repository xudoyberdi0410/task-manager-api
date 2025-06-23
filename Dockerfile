# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем uv - быстрый менеджер пакетов Python
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем переменные окружения для uv
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Копируем файлы конфигурации проекта
COPY pyproject.toml ./

# Устанавливаем зависимости без создания venv (используем системный Python)
RUN uv pip install --system -r pyproject.toml

# Копируем исходный код приложения
COPY . .

# Открываем порт для FastAPI
EXPOSE 8000

# Команда для запуска приложения (без uv run, так как пакеты установлены системно)
CMD ["python", "-m", "uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]