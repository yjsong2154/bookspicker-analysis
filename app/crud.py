from sqlalchemy.orm import Session
from . import models, schemas
from typing import List, Optional

# --- Books ---
def get_book(db: Session, book_id: int):
    return db.query(models.Book).filter(models.Book.id == book_id).first()

def get_book_by_isbn(db: Session, isbn: str):
    return db.query(models.Book).filter(models.Book.isbn == isbn).first()

def get_books(db: Session, skip: int = 0, limit: int = 20, q: Optional[str] = None):
    query = db.query(models.Book)
    if q:
        query = query.filter(models.Book.title.contains(q) | models.Book.author.contains(q))
    return query.offset(skip).limit(limit).all()

def get_all_books_with_embedding(db: Session):
    # Fetch all books that have embeddings for recommendation candidates
    return db.query(models.Book).filter(models.Book.embedding.isnot(None)).all()

def get_books_count(db: Session, q: Optional[str] = None):
    query = db.query(models.Book)
    if q:
        query = query.filter(models.Book.title.contains(q) | models.Book.author.contains(q))
    return query.count()

def create_book(db: Session, book: schemas.BookCreate):
    # Check if ISBN exists
    existing = get_book_by_isbn(db, book.isbn)
    if existing:
        return existing
        
    db_book = models.Book(
        isbn=book.isbn,
        title=book.title,
        author=book.author,
        description=book.description,
        published_year=book.published_year,
        tags=book.tags,
        embedding=book.embedding
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

# --- Users ---
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_backend_id(db: Session, id_backend: int):
    return db.query(models.User).filter(models.User.id_backend == id_backend).first()

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(name=user.name, email=user.email)
    if user.id_backend is not None:
        db_user.id_backend = user.id_backend
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_preferences(db: Session, user_id: int, embedding: List[float], tags: dict):
    user = get_user(db, user_id)
    if user:
        user.preference_embedding = embedding
        user.preferred_tags = tags
        db.commit()
        db.refresh(user)
    return user

# --- UserBooks (Interaction) ---
def record_read_book(db: Session, user_id: int, book_id: int):
    # Check if already recorded
    exists = db.query(models.UserBook).filter_by(user_id=user_id, book_id=book_id).first()
    if not exists:
        user_book = models.UserBook(user_id=user_id, book_id=book_id)
        db.add(user_book)
        db.commit()
        return user_book
    return exists

def get_user_read_history(db: Session, user_id: int):
    return db.query(models.UserBook).filter(models.UserBook.user_id == user_id).all()
