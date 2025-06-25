"""
Роутер для работы с категориями.
Содержит все эндпоинты для управления категориями.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from src.database import get_db
from src.services.category_service import CategoryService
from src.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryList
from src.auth.jwt import get_current_user
from src.schemas.user import UserResponse

router = APIRouter(
    prefix="/categories",
    tags=["categories"]
)


@router.get("/", response_model=CategoryList)
async def get_categories(
    skip: int = Query(0, ge=0, description="Количество записей для пропуска"),
    limit: int = Query(100, ge=1, le=1000, description="Максимальное количество записей"),
    search: Optional[str] = Query(None, description="Поиск по названию категории"),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить список категорий пользователя"""
    service = CategoryService(db)
    
    if search:
        categories, total = service.search_categories(search, current_user.user_id, skip, limit)
    else:
        categories, total = service.get_categories_by_user(current_user.user_id, skip, limit)
    
    page = (skip // limit) + 1
    
    return CategoryList(
        categories=categories,
        total=total,
        page=page,
        per_page=limit
    )


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить категорию по ID"""
    service = CategoryService(db)
    category = service.get_category_by_id(category_id, current_user.user_id)
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категория не найдена"
        )
    
    return category


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создать новую категорию"""
    service = CategoryService(db)
    category = service.create_category(category_data, current_user.user_id)
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Категория с таким названием уже существует"
        )
    
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновить категорию"""
    service = CategoryService(db)
    category = service.update_category(category_id, category_data, current_user.user_id)
    
    if not category:
        # Проверяем, существует ли категория
        if not service.category_exists(category_id, current_user.user_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Категория не найдена"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Категория с таким названием уже существует"
            )
    
    return category


@router.patch("/{category_id}", response_model=CategoryResponse)
async def partial_update_category(
    category_id: int,
    category_data: CategoryUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Частично обновить категорию"""
    return await update_category(category_id, category_data, current_user, db)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Удалить категорию"""
    service = CategoryService(db)
    success = service.delete_category(category_id, current_user.user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категория не найдена"
        )


@router.get("/stats/count")
async def get_categories_count(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить количество категорий пользователя"""
    service = CategoryService(db)
    count = service.get_category_count_by_user(current_user.user_id)
    
    return {"count": count}
