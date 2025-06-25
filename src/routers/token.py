from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.database import get_db
from src.schemas.token import Token
from src.services.auth_service import AuthService

router = APIRouter()


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
) -> Token:
    """Эндпоинт для аутентификации и получения токена доступа"""
    auth_service = AuthService(db)
    token_data = auth_service.login(form_data.username, form_data.password)
    return Token(**token_data)
