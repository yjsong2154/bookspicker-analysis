from fastapi import FastAPI
from . import models
from .database import engine
from .routers import books, users, recommendations

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Book Recommendation Server")

app.include_router(books.router)
app.include_router(users.router)
app.include_router(recommendations.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Book Recommendation Server"}
