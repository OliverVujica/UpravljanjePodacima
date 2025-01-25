from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.user import Base, User

post_likes = Table('post_likes', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('post_id', Integer, ForeignKey('posts.id'), primary_key=True)
)

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    
    author = relationship("User", back_populates="posts")
    category = relationship("Category", back_populates="posts")

    likers = relationship(
        "User", 
        secondary=post_likes, 
        back_populates="liked_posts"
    )

    @property
    def likes_count(self):
        return len(self.likers)
    
    def __repr__(self):
        category_info = f" in category {self.category_id}" if self.category_id else ""
        return f"<Post {self.title} by User {self.author_id}{category_info}>"

User.posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")