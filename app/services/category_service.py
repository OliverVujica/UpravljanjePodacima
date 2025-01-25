from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.category import Category
from app.models.post import Post
from app.schemas.category import CategoryCreate, CategoryResponse
from fastapi import HTTPException, status
from typing import List, Optional

def create_category(db: Session, category: CategoryCreate) -> Category:
    existing_category = db.query(Category).filter(
        func.lower(Category.name) == func.lower(category.name)
    ).first()

    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A category with this name already exists"
        )

    db_category = Category(
        name=category.name,
        description=category.description
    )

    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def get_category_by_id(db: Session, category_id: int) -> Optional[Category]:
    category = db.query(Category).filter(Category.id == category_id).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    return category


def get_category_by_name(db: Session, category_name: str) -> Optional[Category]:
    return db.query(Category).filter(
        func.lower(Category.name) == func.lower(category_name)
    ).first()


def list_categories(db: Session, skip: int = 0, limit: int = 10) -> dict:
    query = db.query(Category, func.count(Post.id).label('post_count')) \
        .outerjoin(Post, Category.id == Post.category_id) \
        .group_by(Category.id)

    total = query.count()
    
    categories_with_count = query.offset(skip).limit(limit).all()
    
    categories = []
    for category, post_count in categories_with_count:
        category_dict = category.__dict__.copy()
        category_dict['post_count'] = post_count
        categories.append(category_dict)

    return {
        "categories": categories,
        "total": total
    }

def update_category(db: Session, category_id: int, category_update: CategoryCreate) -> Category:
    db_category = get_category_by_id(db, category_id)

    if category_update.name.lower() != db_category.name.lower():
        existing_category = get_category_by_name(db, category_update.name)
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A category with this name already exists"
            )

    db_category.name = category_update.name
    db_category.description = category_update.description

    db.commit()
    db.refresh(db_category)
    return db_category


def delete_category(db: Session, category_id: int) -> bool:
    db_category = get_category_by_id(db, category_id)

    post_count = db.query(Post).filter(Post.category_id == category_id).count()
    
    if post_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete category with existing posts"
        )

    db.delete(db_category)
    db.commit()
    return True