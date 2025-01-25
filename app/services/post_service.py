from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from app.models.post import Post
from app.models.category import Category
from app.models.user import User, Base
from app.models.user import UserRole
from app.schemas.post import PostCreate, PostFilter
from app.services.category_service import get_category_by_id
from fastapi import HTTPException, status
from typing import Optional, Dict, Any
from app.services.redis_cache_service import (cache_post, cache_posts_list, get_cached_post, get_cached_posts_list, invalidate_post_cache, invalidate_posts_list_cache)

def create_post(db: Session, post: PostCreate, author_id: int) -> Post:
    category_id = None if post.category_id == 0 else post.category_id

    if category_id is not None:
        get_category_by_id(db, category_id)
    
    db_post = Post(
        title=post.title,
        content=post.content,
        author_id=author_id,
        category_id=post.category_id
    )
    
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    
    invalidate_posts_list_cache()
    
    cache_post({
        'id': db_post.id,
        'title': db_post.title,
        'content': db_post.content,
        'author_id': db_post.author_id,
        'category_id': db_post.category_id,
        'created_at': db_post.created_at.isoformat() if db_post.created_at else None,
        'category': db_post.category.name if db_post.category else None
    })
    
    return db_post

def get_post_by_id(db: Session, post_id: int) -> Post:
    cached_post = get_cached_post(post_id)
    if cached_post:
        return db.query(Post).options(joinedload(Post.category)).filter(Post.id == post_id).first()
    
    post = db.query(Post).options(joinedload(Post.category)).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    cache_post({
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'author_id': post.author_id,
        'category_id': post.category_id,
        'created_at': post.created_at.isoformat() if post.created_at else None,
        'category': post.category.name if post.category else None
    })
    
    return post

def list_posts(db: Session, skip: int = 0, limit: int = 10, filters: Optional[PostFilter] = None) -> Dict[str, Any]:
    filter_dict = {
        'category_id': filters.category_id if filters else None,
        'author_id': filters.author_id if filters else None,
        'start_date': str(filters.start_date) if filters and filters.start_date else None,
        'end_date': str(filters.end_date) if filters and filters.end_date else None,
        'skip': skip,
        'limit': limit
    }
    
    cached_posts = get_cached_posts_list(filter_dict)
    if cached_posts:
        post_ids = [post['id'] for post in cached_posts['posts']]
        posts = (
            db.query(Post)
            .options(joinedload(Post.category))
            .filter(Post.id.in_(post_ids))
            .order_by(Post.id) 
            .all()
        )
        
        return {
            "posts": posts,
            "total": cached_posts['total']
        }
    
    query = db.query(Post).options(joinedload(Post.category)).order_by(desc(Post.created_at))
    
    if filters:
        if filters.category_id is not None:
            query = query.filter(Post.category_id == filters.category_id)
        
        if filters.author_id is not None:
            query = query.filter(Post.author_id == filters.author_id)
        
        if filters.start_date:
            query = query.filter(Post.created_at >= filters.start_date)
        
        if filters.end_date:
            query = query.filter(Post.created_at <= filters.end_date)
    
    total = query.count()
    posts = query.offset(skip).limit(limit).all()
    
    cached_posts_data = {
        'posts': [
            {
                'id': post.id,
                'title': post.title,
                'content': post.content,
                'author_id': post.author_id,
                'category_id': post.category_id,
                'created_at': post.created_at.isoformat() if post.created_at else None,
                'category': post.category.name if post.category else None
            } for post in posts
        ],
        'total': total
    }
    
    cache_posts_list(cached_posts_data, filter_dict)
    
    return {
        "posts": posts,
        "total": total
    }

def update_post(db: Session, post_id: int, post_update: PostCreate, user_id: int, user_role: UserRole) -> Post:
    db_post = get_post_by_id(db, post_id)
    
    if user_role != UserRole.ADMIN and db_post.author_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this post")
    
    if post_update.category_id is not None:
        get_category_by_id(db, post_update.category_id)
    
    db_post.title = post_update.title
    db_post.content = post_update.content
    db_post.category_id = post_update.category_id
    
    db.commit()
    db.refresh(db_post)
    
    invalidate_post_cache(post_id)
    invalidate_posts_list_cache()
    
    return db_post

def delete_post(db: Session, post_id: int, user_id: int, user_role: UserRole) -> bool:
    post = get_post_by_id(db, post_id)
    
    if user_role == UserRole.ADMIN or post.author_id == user_id:
        db.delete(post)
        db.commit()
        
        invalidate_post_cache(post_id)
        invalidate_posts_list_cache()
        
        return True
    
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this post")

def like_post(db: Session, post_id: int, user_id: int, username: str) -> Post:
    post = get_post_by_id(db, post_id)
    
    if any(liker.id == user_id for liker in post.likers):
        post.likers = [liker for liker in post.likers if liker.id != user_id]
    else:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        post.likers.append(user)
    
    db.commit()
    db.refresh(post)
    
    invalidate_post_cache(post_id)
    invalidate_posts_list_cache()
    
    return post