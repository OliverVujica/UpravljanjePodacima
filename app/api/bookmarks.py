from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.bookmark import (
    BookmarkCreate, 
    BookmarkResponse, 
    BookmarkListResponse
)
from app.services.bookmark_service import (
    create_bookmark, 
    list_user_bookmarks, 
    delete_bookmark, 
    get_bookmark_by_id
)
from app.services.user_service import get_user_by_username
from app.schemas.user import TokenData

router = APIRouter()

@router.post(
    "/", 
    response_model=BookmarkResponse, 
    status_code=status.HTTP_201_CREATED
)
def add_bookmark(
    bookmark: BookmarkCreate, 
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    user = get_user_by_username(db, current_user.username)
    
    db_bookmark = create_bookmark(
        db, 
        bookmark=bookmark, 
        user_id=user.id
    )
    
    return db_bookmark

@router.get("/", response_model=BookmarkListResponse)
def read_user_bookmarks(
    skip: int = 0, 
    limit: int = 10, 
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    user = get_user_by_username(db, current_user.username)
    
    result = list_user_bookmarks(
        db, 
        user_id=user.id, 
        skip=skip, 
        limit=limit
    )
    return {
        "bookmarks": result["bookmarks"],
        "total": result["total"]
    }

@router.delete("/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_bookmark(
    bookmark_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    user = get_user_by_username(db, current_user.username)
    
    bookmark = get_bookmark_by_id(db, bookmark_id)
    
    if bookmark.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to delete this bookmark"
        )
    
    delete_bookmark(
        db, 
        bookmark_id=bookmark_id
    )

    return None