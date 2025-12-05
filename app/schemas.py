from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

# --- Books ---
class BookBase(BaseModel):
    title: str
    author: Optional[str] = None
    description: Optional[str] = None
    published_year: Optional[int] = None
    tags: Optional[Dict[str, Any]] = None

class BookCreate(BookBase):
    embedding: Optional[List[float]] = None

class Book(BookBase):
    id: int
    created_at: datetime
    # embedding is usually not returned in list view, maybe in detail if needed
    
    class Config:
        from_attributes = True

class BookList(BaseModel):
    items: List[Book]
    total: int

# --- Users ---
class UserBase(BaseModel):
    name: str
    email: Optional[str] = None

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- UserBooks ---
class UserBookBase(BaseModel):
    status: str = "finished"
    rating: Optional[int] = None
    progress: Optional[float] = None

class UserBookCreate(UserBookBase):
    pass

class UserBook(UserBookBase):
    user_id: int
    book_id: int
    last_read_at: datetime
    book: Optional[Book] = None # For including book info in user's list

    class Config:
        from_attributes = True

class UserBookList(BaseModel):
    items: List[UserBook]

# --- Recommendations ---
class RecommendationItem(BaseModel):
    book_id: int
    title: str
    author: Optional[str]
    score: float
    reasons: Optional[Dict[str, Any]] = None

class RecommendationResponse(BaseModel):
    user_id: int
    strategy: str
    items: List[RecommendationItem]
