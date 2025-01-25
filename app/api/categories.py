from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Optional
from app.models.user import UserRole
from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.schemas.category import (
    CategoryCreate, 
    CategoryResponse, 
    CategoryListResponse
)
from app.services.category_service import (
    create_category, 
    list_categories, 
    get_category_by_id,
    update_category,
    delete_category
)
from app.services.user_service import get_user_by_username
from app.schemas.user import TokenData

router = APIRouter()

@router.post(
    "/", 
    response_model=CategoryResponse, 
    status_code=status.HTTP_201_CREATED
)
def create_new_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    user = get_user_by_username(db, current_user.username)
    require_role(user.role)
    
    return create_category(db, category)

@router.get(
    "/", 
    response_model=CategoryListResponse
)
def read_categories(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    result = list_categories(
        db, 
        skip=skip, 
        limit=limit
    )
    
    return {
        "categories": result["categories"],
        "total": result["total"]
    }

@router.get(
    "/{category_id}", 
    response_model=CategoryResponse
)
def read_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    return get_category_by_id(db, category_id)

@router.put(
    "/{category_id}", 
    response_model=CategoryResponse
)
def update_existing_category(
    category_id: int,
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    user = get_user_by_username(db, current_user.username)
    require_role(user.role)
    
    return update_category(db, category_id, category)

@router.delete(
    "/{category_id}", 
    status_code=status.HTTP_204_NO_CONTENT
)
def remove_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    user = get_user_by_username(db, current_user.username)
    require_role(user.role)
    
    delete_category(db, category_id)
    return None