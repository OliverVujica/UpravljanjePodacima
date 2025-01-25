from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.services.user_service import get_user_by_username
from app.schemas.post import (
    PostCreate, 
    PostResponse, 
    PostListResponse,
    PostFilter
)
from app.services.post_service import (
    create_post, 
    list_posts, 
    get_post_by_id,
    update_post,
    delete_post,
    like_post
)
from app.models.user import UserRole
from app.schemas.user import TokenData

router = APIRouter()

@router.post(
    "/", 
    response_model=PostResponse, 
    status_code=status.HTTP_201_CREATED
)
def create_new_post(post: PostCreate, db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    user = get_user_by_username(db, current_user.username)
    
    return create_post(
        db, 
        post=post, 
        author_id=user.id
    )

@router.get(
    "/", 
    response_model=PostListResponse
)
def read_posts(
    skip: int = 0,
    limit: int = 10,
    category_id: Optional[int] = None,
    author_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    filters = PostFilter(
        category_id=category_id,
        author_id=author_id,
        start_date=start_date,
        end_date=end_date
    )
    
    result = list_posts(
        db, 
        skip=skip, 
        limit=limit, 
        filters=filters
    )
    
    return {
        "posts": result["posts"],
        "total": result["total"]
    }

@router.get(
    "/{post_id}", 
    response_model=PostResponse
)
def read_post(
    post_id: int,
    db: Session = Depends(get_db)
):
    return get_post_by_id(db, post_id)

@router.put(
    "/{post_id}", 
    response_model=PostResponse
)
def update_existing_post(
    post_id: int,
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    user = get_user_by_username(db, current_user.username)
    
    return update_post(
        db, 
        post_id=post_id, 
        post_update=post,
        user_id=user.id,
        user_role=user.role
    )

@router.delete(
    "/{post_id}", 
    status_code=status.HTTP_204_NO_CONTENT
)
def remove_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    user = get_user_by_username(db, current_user.username)
    
    delete_post(
        db, 
        post_id=post_id, 
        user_id=user.id, 
        user_role=user.role
    )
    
    return None

@router.post(
    "/{post_id}/like", 
    response_model=PostResponse
)
def toggle_like(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    user = get_user_by_username(db, current_user.username)

    return like_post(
        db, 
        post_id=post_id, 
        user_id=user.id,
        username = user.username
    )