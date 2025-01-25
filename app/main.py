from fastapi import FastAPI
from app.api import auth
from app.core.database import engine
from app.models.user import Base
from app.models.post import Post
from app.models.category import Category
from app.api import posts, comments, categories, bookmarks
from app.models.notification import Notification

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Blog API")

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

app.include_router(posts.router, prefix="/posts", tags=["Posts"])

app.include_router(categories.router, prefix="/categories", tags=["Categories"])

app.include_router(comments.router, prefix="/comments", tags=["Comments"])

app.include_router(bookmarks.router, prefix="/bookmarks", tags=["Bookmarks"])

@app.get("/")
def read_root():
    return {
        "Poruka": "Blog API je pokrenut",
    }