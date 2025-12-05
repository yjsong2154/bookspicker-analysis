from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
import os
import uuid

from .. import crud, models, schemas
from ..database import get_db
from ..services import analysis

router = APIRouter(
    prefix="/books",
    tags=["books"],
)

UPLOAD_DIR = "storage/epubs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=schemas.Book)
async def upload_book(
    title: str = Form(...),
    author: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename.lower().endswith(".epub"):
        raise HTTPException(status_code=400, detail="Only EPUB files are allowed.")

    # Save file
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.epub")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Analyze
    try:
        analysis_result = analysis.analyze_epub(file_path)
    except Exception as e:
        print(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    # Create Book in DB
    book_create = schemas.BookCreate(
        title=title,
        author=author,
        description=analysis_result.get("description"),
        tags=analysis_result.get("tags"),
        embedding=analysis_result.get("embedding")
    )
    
    return crud.create_book(db=db, book=book_create)

@router.get("/{book_id}", response_model=schemas.Book)
def read_book(book_id: int, db: Session = Depends(get_db)):
    db_book = crud.get_book(db, book_id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

@router.get("/", response_model=schemas.BookList)
def read_books(
    skip: int = 0, 
    limit: int = 20, 
    q: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    items = crud.get_books(db, skip=skip, limit=limit, q=q)
    total = crud.get_books_count(db, q=q)
    return {"items": items, "total": total}
