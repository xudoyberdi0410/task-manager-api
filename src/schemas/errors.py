"""
Схемы для документации ошибок в Swagger
"""

from typing import Any

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Детали ошибки"""

    loc: list[str | int] = Field(
        ...,
        description="Местоположение ошибки в запросе",
        examples=[["body", "email"], ["query", "limit"]],
    )
    msg: str = Field(
        ...,
        description="Сообщение об ошибке",
        examples=["field required", "ensure this value is greater than 0"],
    )
    type: str = Field(
        ..., description="Тип ошибки", examples=["value_error", "type_error", "missing"]
    )


class ValidationError(BaseModel):
    """Ошибка валидации (422)"""

    detail: list[ErrorDetail] = Field(..., description="Список ошибок валидации")


class HTTPError(BaseModel):
    """Базовая схема HTTP ошибки"""

    detail: str = Field(
        ...,
        description="Описание ошибки",
        examples=[
            "Task not found",
            "User already exists",
            "Invalid credentials",
            "Access denied",
        ],
    )


class NotFoundError(HTTPError):
    """Ошибка 404 - не найдено"""

    detail: str = Field(
        default="Resource not found",
        examples=["Task not found", "Category not found", "User not found"],
    )


class UnauthorizedError(HTTPError):
    """Ошибка 401 - не авторизован"""

    detail: str = Field(
        default="Could not validate credentials",
        examples=[
            "Could not validate credentials",
            "Token has expired",
            "Invalid token",
        ],
    )


class ForbiddenError(HTTPError):
    """Ошибка 403 - доступ запрещен"""

    detail: str = Field(
        default="Access denied",
        examples=[
            "Access denied",
            "Insufficient permissions",
            "You can only access your own resources",
        ],
    )


class ConflictError(HTTPError):
    """Ошибка 409 - конфликт"""

    detail: str = Field(
        default="Resource already exists",
        examples=[
            "User with this email already exists",
            "Username already taken",
            "Category with this name already exists",
        ],
    )


class BadRequestError(HTTPError):
    """Ошибка 400 - неверный запрос"""

    detail: str = Field(
        default="Bad request",
        examples=[
            "Invalid request data",
            "Missing required fields",
            "Invalid parameter values",
        ],
    )


class InternalServerError(HTTPError):
    """Ошибка 500 - внутренняя ошибка сервера"""

    detail: str = Field(
        default="Internal server error",
        examples=[
            "Internal server error",
            "Database connection failed",
            "Unexpected error occurred",
        ],
    )


# Готовые наборы ошибок для разных эндпоинтов
COMMON_ERRORS: dict[int | str, dict[str, Any]] = {
    401: {"model": UnauthorizedError, "description": "Не авторизован"},
    422: {"model": ValidationError, "description": "Ошибка валидации"},
    500: {"model": InternalServerError, "description": "Внутренняя ошибка сервера"},
}

CRUD_ERRORS: dict[int | str, dict[str, Any]] = {
    **COMMON_ERRORS,
    404: {"model": NotFoundError, "description": "Ресурс не найден"},
    403: {"model": ForbiddenError, "description": "Доступ запрещен"},
}

AUTH_ERRORS: dict[int | str, dict[str, Any]] = {
    400: {"model": BadRequestError, "description": "Неверные данные"},
    409: {"model": ConflictError, "description": "Пользователь уже существует"},
    422: {"model": ValidationError, "description": "Ошибка валидации"},
    500: {"model": InternalServerError, "description": "Внутренняя ошибка сервера"},
}

LOGIN_ERRORS: dict[int | str, dict[str, Any]] = {
    401: {"model": UnauthorizedError, "description": "Неверные учетные данные"},
    422: {"model": ValidationError, "description": "Ошибка валидации"},
    500: {"model": InternalServerError, "description": "Внутренняя ошибка сервера"},
}
