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
        
    return crud.create_or_update_user_book(db=db, user_id=user_id, book_id=book_id, user_book=user_book)

@router.get("/{user_id}/books", response_model=schemas.UserBookList)
def read_user_books(
    user_id: int, 
    status: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    items = crud.get_user_books(db, user_id=user_id, status=status)
    return {"items": items}
