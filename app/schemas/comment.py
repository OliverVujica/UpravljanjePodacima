from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class CommentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000, description="Content of the comment")

class CommentCreate(CommentBase):
    pass

class CommentResponse(CommentBase):
    id: int
    post_id: int
    author_id: int
    created_at: datetime

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

class CommentListResponse(BaseModel):
    comments: list[CommentResponse]
    total: int