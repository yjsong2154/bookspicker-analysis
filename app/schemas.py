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
    cover_image: Optional[str] = None

class BookCreate(BookBase):
    embedding: Optional[List[float]] = None

class Book(BookBase):
    id: int
    created_at: datetime
    # embedding is usually large, so maybe exclude by default in list, but include if detail needed.
    # For now, let's keep it optional in response or separate.
    comments: List["Comment"] = []
    
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

class UserReadBookRequest(BaseModel):
    id_backend: int
    isbn: str


# --- Recommendations ---
class RecommendationItem(BaseModel):
    book_id: int
    isbn: str
    title: str
    author: Optional[str]
    score: float
    reasons: Optional[Dict[str, Any]] = None
    cover_image: Optional[str] = None

class RecommendationResponse(BaseModel):
    user_id: int
    items: List[RecommendationItem]

# --- Advanced Recommendations ---
class BookSimple(BaseModel):
    id: int
    isbn: str
    title: str
    author: Optional[str] = None
    description: Optional[str] = None
    published_year: Optional[int] = None
    cover_image: Optional[str] = None
    # No embedding, no tags

    class Config:
        from_attributes = True

class RecommendationSection(BaseModel):
    title: str
    books: List[BookSimple]

class AdvancedRecommendationResponse(BaseModel):
    sections: List[RecommendationSection]

# --- Comments ---
class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    user_id: int # or id_backend

class CommentUpdate(BaseModel):
    content: str
    user_id: int # for verification

class Comment(CommentBase):
    id: int
    user_id: int
    book_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    user: Optional[UserBase] = None

    class Config:
        from_attributes = True


# Resolve forward references
Book.model_rebuild()
