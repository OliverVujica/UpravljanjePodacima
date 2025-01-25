from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserRole

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.USER

class UserResponse(UserBase):
    id: int
    role: UserRole

    class Config:
        orm_mode = True

class TokenData(BaseModel):
    username: str = None
    role: UserRole = None

class Token(BaseModel):
    access_token: str
    token_type: str