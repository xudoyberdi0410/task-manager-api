# Установка инструментов разработки

## Автоматическая установка

```bash
# Установить все зависимости для разработки
uv pip install --system -e ".[dev]"

# Или установить pre-commit отдельно
pip install pre-commit
pre-commit install
```

## Ручная установка инструментов

```bash
# Основные инструменты
pip install ruff black mypy

# Безопасность
pip install bandit safety pip-audit

# Тестирование
pip install pytest pytest-cov

# Pre-commit hooks (опционально)
pip install pre-commit
```

## Проверка установки

```bash
# Проверить, что все инструменты доступны
ruff --version
black --version
mypy --version
bandit --version
safety --version
pytest --version
```

## Быстрый тест

```bash
# Запустить локальные CI проверки
./scripts/ci-check.sh
```
