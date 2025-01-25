from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Dict, Optional

from app.models.bookmark import Bookmark
from app.models.post import Post
from app.schemas.bookmark import BookmarkCreate, BookmarkResponse
from fastapi import HTTPException, status

def create_bookmark(db: Session, bookmark: BookmarkCreate, user_id: int) -> BookmarkResponse:
    post = db.query(Post).filter(Post.id == bookmark.post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Post not found"
        )
    
    existing_bookmark = db.query(Bookmark).filter(
        Bookmark.user_id == user_id, 
        Bookmark.post_id == bookmark.post_id
    ).first()
    
    if existing_bookmark:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Bookmark already exists"
        )
    
    new_bookmark = Bookmark(
        user_id=user_id,
        post_id=bookmark.post_id
    )
    
    try:
        db.add(new_bookmark)
        db.commit()
        db.refresh(new_bookmark)
        
        return BookmarkResponse(
            id=new_bookmark.id,
            user_id=new_bookmark.user_id,
            post_id=new_bookmark.post_id,
            created_at=new_bookmark.created_at,
            post_title=post.title
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Could not create bookmark"
        )

def list_user_bookmarks(db: Session, user_id: int, skip: int = 0, limit: int = 10) -> Dict[str, List[BookmarkResponse]]:
    query = (
        db.query(Bookmark, Post.title)
        .join(Post)
        .filter(Bookmark.user_id == user_id)
        .order_by(Bookmark.created_at.desc())
    )
    
    total = query.count()
    
    bookmarks_with_titles = (
        query
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    bookmarks = [
        BookmarkResponse(
            id=bookmark.id,
            user_id=bookmark.user_id,
            post_id=bookmark.post_id,
            created_at=bookmark.created_at,
            post_title=post_title
        ) for bookmark, post_title in bookmarks_with_titles
    ]
    
    return {
        "bookmarks": bookmarks,
        "total": total
    }

def get_bookmark_by_id(db: Session, bookmark_id: int) -> Bookmark:
    bookmark = db.query(Bookmark).filter(Bookmark.id == bookmark_id).first()
    
    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Bookmark not found"
        )
    
    return bookmark

def delete_bookmark(db: Session, bookmark_id: int):
    bookmark = get_bookmark_by_id(db, bookmark_id)
    
    db.delete(bookmark)
    db.commit()