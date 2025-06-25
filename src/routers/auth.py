from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.schemas.errors import AUTH_ERRORS
from src.schemas.user import UserCreate, UserResponse
from src.services.auth_service import UserService

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация пользователя",
    description="Создать новый аккаунт пользователя в системе",
    response_description="Данные созданного пользователя",
    responses=AUTH_ERRORS,
)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    ## Регистрация нового пользователя

    Создает новый аккаунт пользователя в системе управления задачами.

    ### Требования к данным:
    - **email**: должен быть уникальным и в правильном формате
    - **username**: должен быть уникальным, от 3 до 50 символов
    - **password**: минимум 8 символов

    ### Процесс регистрации:
    1. Проверка уникальности email и username
    2. Хеширование пароля
    3. Создание пользователя в базе данных
    4. Возврат данных пользователя (без пароля)

    ### После регистрации:
    Используйте эндпоинт `/token` для получения токена доступа.

    ### Коды ответов:
    - **201**: Пользователь успешно создан
    - **400**: Пользователь с таким email или username уже существует
    - **422**: Ошибка валидации данных
    """
    user_service = UserService(db)
    new_user = user_service.register_user(
        email=user_data.email, username=user_data.username, password=user_data.password
    )
    return new_user
