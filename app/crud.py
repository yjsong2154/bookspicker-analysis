from sqlalchemy.orm import Session
from . import models, schemas
from typing import List, Optional

# --- Books ---
def get_book(db: Session, book_id: int):
    return db.query(models.Book).filter(models.Book.id == book_id).first()

def get_books(db: Session, skip: int = 0, limit: int = 20, q: Optional[str] = None):
    query = db.query(models.Book)
    if q:
        query = query.filter(models.Book.title.contains(q) | models.Book.author.contains(q))
    return query.offset(skip).limit(limit).all()

def get_books_count(db: Session, q: Optional[str] = None):
    query = db.query(models.Book)
    if q:
        query = query.filter(models.Book.title.contains(q) | models.Book.author.contains(q))
    return query.count()

def create_book(db: Session, book: schemas.BookCreate):
    db_book = models.Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

# --- Users ---
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- UserBooks ---
def get_user_book(db: Session, user_id: int, book_id: int):
    return db.query(models.UserBook).filter(models.UserBook.user_id == user_id, models.UserBook.book_id == book_id).first()

def get_user_books(db: Session, user_id: int, status: Optional[str] = None):
    query = db.query(models.UserBook).filter(models.UserBook.user_id == user_id)
    if status:
        query = query.filter(models.UserBook.status == status)
    return query.all()

def create_or_update_user_book(db: Session, user_id: int, book_id: int, user_book: schemas.UserBookCreate):
    db_user_book = get_user_book(db, user_id, book_id)
    if db_user_book:
        # Update
        for key, value in user_book.dict(exclude_unset=True).items():
            setattr(db_user_book, key, value)
    else:
        # Create
        db_user_book = models.UserBook(user_id=user_id, book_id=book_id, **user_book.dict())
        db.add(db_user_book)
    
    db.commit()
    db.refresh(db_user_book)
    return db_user_book
