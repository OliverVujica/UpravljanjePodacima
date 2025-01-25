from pydantic import BaseModel
from datetime import datetime
from typing import List

class BookmarkBase(BaseModel):
    post_id: int

class BookmarkCreate(BookmarkBase):
    pass

class BookmarkResponse(BookmarkBase):
    id: int
    user_id: int
    created_at: datetime
    post_title: str = None

    class Config:
        from_attributes = True

class BookmarkListResponse(BaseModel):
    bookmarks: List[BookmarkResponse]
    total: int