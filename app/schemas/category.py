from pydantic import BaseModel, Field
from typing import Optional, List

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Name of the category")
    description: Optional[str] = Field(None, description="Optional description of the category")

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    post_count: Optional[int] = 0

    class Config:
        orm_mode = True

class CategoryListResponse(BaseModel):
    categories: List[CategoryResponse]
    total: int