"""
Репозиторий для работы с пользователями в базе данных.
Содержит все операции CRUD для модели User.
"""

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.models.user import User
from src.utils.password import get_password_hash


class UserRepository:
    """Репозиторий для работы с пользователями"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        """Получить пользователя по email"""
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: int) -> User | None:
        """Получить пользователя по ID"""
        return self.db.query(User).filter(User.user_id == user_id).first()

    def get_by_username(self, username: str) -> User | None:
        """Получить пользователя по username"""
        return self.db.query(User).filter(User.username == username).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> tuple[list[User], int]:
        """Получить список всех пользователей с пагинацией"""
        # Получаем общее количество пользователей
        total = self.db.query(func.count(User.user_id)).scalar()

        # Получаем пользователей с пагинацией
        users = self.db.query(User).offset(skip).limit(limit).all()

        return users, total

    def search_users(
        self, query: str, skip: int = 0, limit: int = 100
    ) -> tuple[list[User], int]:
        """Поиск пользователей по email или username"""
        search_filter = User.email.ilike(f"%{query}%") | User.username.ilike(
            f"%{query}%"
        )

        # Получаем общее количество найденных пользователей
        total = self.db.query(func.count(User.user_id)).filter(search_filter).scalar()

        # Получаем пользователей с пагинацией
        users = (
            self.db.query(User).filter(search_filter).offset(skip).limit(limit).all()
        )

        return users, total

    def create_user(self, email: str, username: str, password: str) -> User:
        """Создать нового пользователя"""
        hashed_password = get_password_hash(password)
        new_user = User(email=email, username=username, hashed_password=hashed_password)
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

    def update_user(self, user_id: int, **kwargs) -> User | None:
        """Обновить данные пользователя"""
        user = self.get_by_id(user_id)
        if not user:
            return None

        for key, value in kwargs.items():
            if value is not None and hasattr(user, key):
                if key == "password":
                    # Хешируем пароль при обновлении
                    user.hashed_password = get_password_hash(value)
                else:
                    setattr(user, key, value)

        self.db.commit()
        self.db.refresh(user)
        return user

    def update_user_partial(
        self,
        user_id: int,
        email: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ) -> User | None:
        """Частичное обновление данных пользователя"""
        user = self.get_by_id(user_id)
        if not user:
            return None

        if email is not None:
            user.email = email
        if username is not None:
            user.username = username
        if password is not None:
            user.hashed_password = get_password_hash(password)

        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user_id: int) -> bool:
        """Удалить пользователя"""
        user = self.get_by_id(user_id)
        if not user:
            return False

        self.db.delete(user)
        self.db.commit()
        return True

    def exists_by_email(self, email: str) -> bool:
        """Проверить существование пользователя по email"""
        return self.db.query(User).filter(User.email == email).first() is not None

    def exists_by_username(self, username: str) -> bool:
        """Проверить существование пользователя по username"""
        return self.db.query(User).filter(User.username == username).first() is not None

    def exists_by_email_except_user(self, email: str, user_id: int) -> bool:
        """Проверить существование пользователя по email, исключая указанного пользователя"""
        return (
            self.db.query(User)
            .filter(User.email == email, User.user_id != user_id)
            .first()
            is not None
        )

    def exists_by_username_except_user(self, username: str, user_id: int) -> bool:
        """Проверить существование пользователя по username, исключая указанного пользователя"""
        return (
            self.db.query(User)
            .filter(User.username == username, User.user_id != user_id)
            .first()
            is not None
        )
