"""
Сервис для работы с аутентификацией и пользователями.
Содержит бизнес-логику приложения.
"""
from datetime import timedelta
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.repositories.user_repository import UserRepository
from src.utils.password import verify_password
from src.auth.jwt import create_access_token
from src.models.user import User
from src.config import settings


class AuthService:
    """Сервис для аутентификации"""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
    
    def authenticate_user(self, login: str, password: str) -> Optional[User]:
        """Аутентификация пользователя по email или username"""
        # Сначала пробуем найти по email
        user = self.user_repo.get_by_email(login)
        
        # Если не найден по email, пробуем по username
        if not user:
            user = self.user_repo.get_by_username(login)
        
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    def create_access_token_for_user(self, user: User) -> str:
        """Создание токена доступа для пользователя"""
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user.email}, 
            expires_delta=access_token_expires
        )
        return access_token
    
    def login(self, login: str, password: str) -> dict:
        """Вход в систему по email или username"""
        user = self.authenticate_user(login, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email/username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token = self.create_access_token_for_user(user)
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }


class UserService:
    """Сервис для работы с пользователями"""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
    
    def get_all_users(self, skip: int = 0, limit: int = 100) -> dict:
        """Получить список всех пользователей с пагинацией"""
        users, total = self.user_repo.get_all(skip=skip, limit=limit)
        
        return {
            "users": users,
            "total": total,
            "page": (skip // limit) + 1 if limit > 0 else 1,
            "per_page": limit
        }

    def search_users(self, query: str, skip: int = 0, limit: int = 100) -> dict:
        """Поиск пользователей"""
        users, total = self.user_repo.search_users(query=query, skip=skip, limit=limit)
        
        return {
            "users": users,
            "total": total,
            "page": (skip // limit) + 1 if limit > 0 else 1,
            "per_page": limit
        }
    
    def register_user(self, email: str, username: str, password: str) -> User:
        """Регистрация нового пользователя"""
        # Проверяем существование пользователя с таким email
        if self.user_repo.exists_by_email(email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Проверяем существование пользователя с таким username
        if self.user_repo.exists_by_username(username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Создаем пользователя
        return self.user_repo.create_user(email, username, password)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        return self.user_repo.get_by_email(email)
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        return self.user_repo.get_by_id(user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Получить пользователя по username"""
        return self.user_repo.get_by_username(username)

    def update_user(self, user_id: int, email: Optional[str] = None, 
                   username: Optional[str] = None, password: Optional[str] = None) -> User:
        """Обновить данные пользователя"""
        # Проверяем существование пользователя
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Проверяем уникальность email (если обновляется)
        if email and email != user.email:
            if self.user_repo.exists_by_email_except_user(email, user_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )

        # Проверяем уникальность username (если обновляется)
        if username and username != user.username:
            if self.user_repo.exists_by_username_except_user(username, user_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )

        # Обновляем данные
        updated_user = self.user_repo.update_user_partial(
            user_id=user_id,
            email=email,
            username=username,
            password=password
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user"
            )
        
        return updated_user

    def delete_user(self, user_id: int) -> bool:
        """Удалить пользователя"""
        # Проверяем существование пользователя
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return self.user_repo.delete_user(user_id)
