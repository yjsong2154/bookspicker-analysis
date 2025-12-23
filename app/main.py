from fastapi import FastAPI
from . import models
from .database import engine
from .routers import books, users, recommendations

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Book Recommendation Server")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?", # Allow all localhost ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(books.router)
app.include_router(users.router)
app.include_router(recommendations.router)
from .routers import analysis
app.include_router(analysis.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Book Recommendation Server"}
