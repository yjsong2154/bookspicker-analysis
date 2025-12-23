from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

# --- Books ---
class BookBase(BaseModel):
    isbn: str
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
    # embedding is usually large, so maybe exclude by default in list, but include if detail needed.
    # For now, let's keep it optional in response or separate.
    
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
    id_backend: Optional[int] = None

class User(UserBase):
    id: int
    id_backend: Optional[int] = None
    created_at: datetime
    preference_embedding: Optional[List[float]] = None
    preferred_tags: Optional[Dict[str, int]] = None

    class Config:
        from_attributes = True

# --- UserBooks (Read History) ---
class UserBookCreate(BaseModel):
    user_id: int
    book_id: int

class UserBook(BaseModel):
    user_id: int
    book_id: int
    read_at: datetime
    book: Optional[Book] = None

    class Config:
        from_attributes = True

class UserBookList(BaseModel):
    items: List[UserBook]

# --- Recommendations ---
class RecommendationItem(BaseModel):
    book_id: int
    isbn: str
    title: str
    author: Optional[str]
    score: float
    reasons: Optional[Dict[str, Any]] = None

class RecommendationResponse(BaseModel):
    user_id: int
    items: List[RecommendationItem]
