from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.models.user import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)

    posts = relationship("Post", back_populates="category")

    def __repr__(self):
        return f"<Category {self.name}>"