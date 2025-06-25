from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database import get_db
from src.schemas.user import UserBase
from src.services.auth_service import UserService

router = APIRouter()


class UserCreate(BaseModel):
    """Схема для создания пользователя"""

    email: str
    username: str
    password: str


@router.post("/register", response_model=UserBase)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Регистрация нового пользователя"""
    user_service = UserService(db)
    new_user = user_service.register_user(
        email=user_data.email, username=user_data.username, password=user_data.password
    )
    return new_user
