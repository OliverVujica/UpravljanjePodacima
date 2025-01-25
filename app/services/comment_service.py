from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.comment import Comment
from app.models.user import UserRole
from app.models.post import Post
from app.schemas.comment import CommentCreate
from fastapi import HTTPException, status

def create_comment(db: Session, comment: CommentCreate, post_id: int, author_id: int) -> Comment:
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    db_comment = Comment(content=comment.content, post_id=post_id, author_id=author_id)
    
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

def get_comment_by_id(db: Session, comment_id: int) -> Comment:
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    return comment

def list_comments_for_post(db: Session, post_id: int, skip: int = 0, limit: int = 10) -> dict:
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    query = db.query(Comment).filter(
        Comment.post_id == post_id
    ).order_by(desc(Comment.created_at))
    
    total = query.count()
    comments = query.offset(skip).limit(limit).all()
    
    return {
        "comments": comments,
        "total": total
    }

def delete_comment(db: Session, comment_id: int, user_id: int, user_role: UserRole) -> bool:
    comment = get_comment_by_id(db, comment_id)
    
    if user_role == UserRole.ADMIN or comment.author_id == user_id:
        db.delete(comment)
        db.commit()
        return True
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not authorized to delete this comment"
    )