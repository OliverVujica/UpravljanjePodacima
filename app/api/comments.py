from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.schemas.comment import (
    CommentCreate, 
    CommentResponse, 
    CommentListResponse
)
from app.services.comment_service import (
    create_comment, 
    list_comments_for_post, 
    delete_comment
)
from app.services.user_service import get_user_by_username
from app.models.user import UserRole
from app.schemas.user import TokenData

router = APIRouter()

@router.post(
    "/posts/{post_id}", 
    response_model=CommentResponse, 
    status_code=status.HTTP_201_CREATED
)
def add_comment(
    post_id: int,
    comment: CommentCreate, 
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    user = get_user_by_username(db, current_user.username)
    
    db_comment = create_comment(
        db, 
        comment=comment, 
        post_id=post_id,
        author_id=user.id
    )
    
    return db_comment

@router.get("/posts/{post_id}", response_model=CommentListResponse)
def read_post_comments(
    post_id: int,
    skip: int = 0, 
    limit: int = 10, 
    db: Session = Depends(get_db)
):
    result = list_comments_for_post(
        db, 
        post_id=post_id, 
        skip=skip, 
        limit=limit
    )
    return {
        "comments": result["comments"],
        "total": result["total"]
    }

@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    user = get_user_by_username(db, current_user.username)
    
    delete_comment(
        db, 
        comment_id=comment_id, 
        user_id=user.id, 
        user_role=user.role
    )

    return None