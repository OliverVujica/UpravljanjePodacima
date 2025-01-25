from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List

from app.schemas.category import CategoryResponse

class PostBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255, description="Title of the post")
    content: str = Field(..., min_length=10, description="Content of the post")
    category_id: Optional[int] = Field(None, description="Optional category ID for the post")

class PostCreate(PostBase):
    @validator('category_id', pre=True, always=True)
    def validate_category_id(cls, v):
        if v == 0:
            return None
        if v is not None and v <= 0:
            raise ValueError('Category ID must be a positive integer or 0 for no category')
        return v

class PostResponse(PostBase):
    id: int
    author_id: int
    category: Optional[CategoryResponse] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    likes_count: int = 0

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

class PostListResponse(BaseModel):
    posts: List[PostResponse]
    total: int

class PostFilter(BaseModel):
    category_id: Optional[int] = None
    author_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None