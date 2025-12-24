from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import crud, models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.post("/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@router.get("/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.post("/{user_id}/books/{book_id}", response_model=schemas.UserBook)
def record_user_book(
    user_id: int, 
    book_id: int, 
    user_book: schemas.UserBookCreate, 
    db: Session = Depends(get_db)
):
    # Check if user and book exist
    db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_book = crud.get_book(db, book_id=book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
        
    return crud.record_read_book(db=db, user_id=user_id, book_id=book_id)

@router.post("/record-read", response_model=schemas.UserBook)
def record_read_book_by_external_ids(
    request: schemas.UserReadBookRequest,
    db: Session = Depends(get_db)
):
    # Find User
    db_user = crud.get_user_by_backend_id(db, request.id_backend)
    if not db_user:
        raise HTTPException(status_code=404, detail=f"User with backend id {request.id_backend} not found")
        
    # Find Book
    db_book = crud.get_book_by_isbn(db, request.isbn)
    if not db_book:
        raise HTTPException(status_code=404, detail=f"Book with ISBN {request.isbn} not found")
        
    return crud.record_read_book(db=db, user_id=db_user.id, book_id=db_book.id)

@router.get("/{user_id}/books", response_model=schemas.UserBookList)
def read_user_books(
    user_id: int, 
    status: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    items = crud.get_user_read_history(db, user_id=user_id)
    return {"items": items}
@router.post("/{id_backend}/books/isbn/{isbn}")
def record_read_history_by_external_ids(
    id_backend: int, 
    isbn: str,
    db: Session = Depends(get_db)
):
    # Find User
    db_user = crud.get_user_by_backend_id(db, id_backend)
    if not db_user:
        # User requested 200 even if not found? 
        # "if post but already ... or delete but not found ... 200"
        # If user not found, we can't record. But maybe just return 200 with message "User skipped"?
        # User said "already exists ... 200". Did not say "if user not found 200".
        # I'll Assume standard 404 for missing user/book, but 200 for "relation already exists".
        # BUT, "if put in library ... post ... if already 200".
        # So I only silence "Already Exists" error.
        raise HTTPException(status_code=404, detail="User not found")
        
    db_book = crud.get_book_by_isbn(db, isbn)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
        
    crud.record_read_book(db, db_user.id, db_book.id)
    return {"message": "recorded"}

@router.delete("/{id_backend}/books/isbn/{isbn}")
def delete_read_history_by_external_ids(
    id_backend: int, 
    isbn: str,
    db: Session = Depends(get_db)
):
    db_user = crud.get_user_by_backend_id(db, id_backend)
    if not db_user:
        return {"message": "User not found, nothing to delete"} # Idempotent 200
        
    db_book = crud.get_book_by_isbn(db, isbn)
    if not db_book:
        return {"message": "Book not found, nothing to delete"} # Idempotent 200
        
    crud.delete_read_history(db, db_user.id, db_book.id)
    return {"message": "deleted"}

@router.get("/{id_backend}/wordcloud")
def get_user_wordcloud(
    id_backend: int,
    db: Session = Depends(get_db)
):
    db_user = crud.get_user_by_backend_id(db, id_backend)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return crud.get_user_wordcloud(db, db_user.id)
