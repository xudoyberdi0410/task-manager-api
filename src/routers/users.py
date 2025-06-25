from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.auth.jwt import get_current_active_user
from src.models.user import User
from src.schemas.user import UserResponse, UserUpdate, UserList
from src.services.auth_service import UserService
from src.database import get_db

router = APIRouter()

@router.get("/users/me", response_model=UserResponse)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Получение информации о текущем пользователе"""
    return current_user

@router.put("/users/me", response_model=UserResponse)
async def update_users_me(
    user_update: UserUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    """Обновление информации о текущем пользователе"""
    user_service = UserService(db)
    return user_service.update_user(
        user_id=current_user.user_id,
        email=user_update.email,
        username=user_update.username,
        password=user_update.password
    )

@router.delete("/users/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    """Удаление аккаунта текущего пользователя"""
    user_service = UserService(db)
    if not user_service.delete_user(current_user.user_id):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )

@router.get("/users", response_model=UserList)
async def get_users(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Количество пользователей для пропуска"),
    limit: int = Query(100, ge=1, le=1000, description="Количество пользователей для возврата"),
    search: Optional[str] = Query(None, description="Поиск по email или username")
):
    """Получение списка пользователей с пагинацией и поиском"""
    user_service = UserService(db)
    
    if search:
        result = user_service.search_users(query=search, skip=skip, limit=limit)
    else:
        result = user_service.get_all_users(skip=skip, limit=limit)
    
    return UserList(**result)

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    """Получение пользователя по ID"""
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    """Обновление пользователя по ID (требует административных прав)"""
    # Здесь можно добавить проверку прав администратора
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    user_service = UserService(db)
    return user_service.update_user(
        user_id=user_id,
        email=user_update.email,
        username=user_update.username,
        password=user_update.password
    )

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    """Удаление пользователя по ID (требует административных прав)"""
    # Здесь можно добавить проверку прав администратора
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    user_service = UserService(db)
    if not user_service.delete_user(user_id):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )

@router.get("/users/me/tasks")
async def read_own_tasks(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    """Получение задач текущего пользователя"""
    # Здесь можно добавить логику получения задач пользователя
    return {"tasks": [], "owner": current_user.username}
