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
    isbn: str = Form(...),
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
        isbn=isbn,
        title=title,
        author=author,
        description=analysis_result.get("description"),
        tags=analysis_result.get("tags"),
        embedding=analysis_result.get("embedding")
    )
    
    return crud.create_book(db=db, book=book_create)

@router.post("/", response_model=schemas.Book)
def create_book_manually(book: schemas.BookCreate, db: Session = Depends(get_db)):
    """
    Manually create a book with analysis data (tags, vectors).
    """
    return crud.create_book(db=db, book=book)

@router.post("/with-cover", response_model=schemas.Book)
async def create_book_with_cover(
    isbn: str = Form(...),
    title: str = Form(...),
    author: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    published_year: Optional[int] = Form(None),
    cover_image: Optional[UploadFile] = File(None),
    tags: Optional[str] = Form(None), # JSON string
    embedding: Optional[str] = Form(None), # JSON string
    db: Session = Depends(get_db)
):
    import json
    import traceback
    
    try:
        cover_url = None
        if cover_image:
            COVER_DIR = "storage/covers"
            os.makedirs(COVER_DIR, exist_ok=True)
            # Sanitize filename?
            file_name = f"{isbn}_{cover_image.filename}"
            file_path = os.path.join(COVER_DIR, file_name)
            
            # Using async read might be safer with UploadFile, but shutil.copyfileobj works with .file
            # If using async: content = await cover_image.read()
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(cover_image.file, buffer)
            
            cover_url = f"/storage/covers/{file_name}"

        tags_data = json.loads(tags) if tags else None
        embedding_list = json.loads(embedding) if embedding else None

        # Fix for pydantic validation: Frontend sends list, schema expects dict
        if isinstance(tags_data, list):
             tags_dict = {t: 1 for t in tags_data}
        else:
             tags_dict = tags_data

        book_create = schemas.BookCreate(
            isbn=isbn,
            title=title,
            author=author,
            description=description,
            published_year=published_year,
            tags=tags_dict,
            embedding=embedding_list,
            cover_image=cover_url
        )
        return crud.create_book(db=db, book=book_create)
    except Exception as e:
        import traceback
        with open("server_error.log", "w") as f:
            f.write(traceback.format_exc())
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to create book with cover: {str(e)}")

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

# --- Comments Endpoints ---

@router.get("/{isbn}/comments", response_model=List[schemas.Comment])
def read_comments(isbn: str, db: Session = Depends(get_db)):
    book = crud.get_book_by_isbn(db, isbn)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return crud.get_comments_by_book(db, book.id)

@router.post("/{isbn}/comment", response_model=schemas.Comment)
def create_comment(isbn: str, comment: schemas.CommentCreate, db: Session = Depends(get_db)):
    book = crud.get_book_by_isbn(db, isbn)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    user = crud.get_user(db, comment.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return crud.create_comment(db, comment, book.id)

@router.put("/{isbn}/comment/{comment_id}", response_model=schemas.Comment)
def update_comment(isbn: str, comment_id: int, comment: schemas.CommentUpdate, db: Session = Depends(get_db)):
    book = crud.get_book_by_isbn(db, isbn)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    db_comment = crud.get_comment(db, comment_id)
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if db_comment.user_id != comment.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this comment")
    
    return crud.update_comment(db, comment_id, comment.content)

@router.delete("/{isbn}/comment/{comment_id}")
def delete_comment(isbn: str, comment_id: int, user_id: int, db: Session = Depends(get_db)):
    book = crud.get_book_by_isbn(db, isbn)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    db_comment = crud.get_comment(db, comment_id)
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
        
    if db_comment.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")

    crud.delete_comment(db, comment_id)
    return {"detail": "Comment deleted"}
