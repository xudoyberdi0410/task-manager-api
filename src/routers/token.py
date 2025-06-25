from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.database import get_db
from src.schemas.errors import LOGIN_ERRORS
from src.schemas.token import Token
from src.services.auth_service import AuthService

router = APIRouter()


@router.post(
    "/token",
    response_model=Token,
    summary="Получить токен доступа",
    description="Аутентификация пользователя и получение JWT токена",
    response_description="JWT токен для доступа к защищенным эндпоинтам",
    status_code=status.HTTP_200_OK,
    responses=LOGIN_ERRORS,
)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
) -> Token:
    """
    ## Аутентификация и получение токена доступа

    Этот эндпоинт позволяет пользователю войти в систему и получить JWT токен
    для доступа к защищенным ресурсам API.

    ### Использование:
    1. Отправьте POST запрос с данными формы
    2. Получите access_token в ответе
    3. Используйте токен в заголовке Authorization: `Bearer <access_token>`

    ### Форма данных:
    - **username**: имя пользователя или email
    - **password**: пароль пользователя

    ### Пример использования токена:
    ```
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    ```

    ### Коды ответов:
    - **200**: Успешная аутентификация, токен выдан
    - **401**: Неверные учетные данные
    - **422**: Ошибка валидации данных формы
    """
    auth_service = AuthService(db)
    token_data = auth_service.login(form_data.username, form_data.password)
    return Token(**token_data)
