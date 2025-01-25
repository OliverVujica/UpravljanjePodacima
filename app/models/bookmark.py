from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.user import Base, User
from app.models.post import Post

class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="bookmarks")
    post = relationship("Post", back_populates="bookmarkers")

    def __repr__(self):
        return f"<Bookmark User {self.user_id} - Post {self.post_id}>"

User.bookmarks = relationship("Bookmark", back_populates="user", cascade="all, delete-orphan")
Post.bookmarkers = relationship("Bookmark", back_populates="post", cascade="all, delete-orphan")