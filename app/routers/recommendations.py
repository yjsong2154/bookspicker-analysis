from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import numpy as np

from .. import crud, models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/users",
    tags=["recommendations"],
)

def cosine_similarity(v1, v2):
    if v1 is None or v2 is None:
        return 0.0
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

@router.get("/{user_id}/recommendations", response_model=schemas.RecommendationResponse)
def get_recommendations(
    user_id: int, 
    top_k: int = 10, 
    strategy: str = "hybrid", 
    db: Session = Depends(get_db)
):
    # 1. Get user's read books
    user_books = crud.get_user_books(db, user_id=user_id)
    if not user_books:
        return {"user_id": user_id, "strategy": strategy, "items": []}

    # 2. Calculate user profile vector
    read_vectors = []
    for ub in user_books:
        if ub.book and ub.book.embedding:
            read_vectors.append(ub.book.embedding)
    
    if not read_vectors:
        return {"user_id": user_id, "strategy": strategy, "items": []}
    
    user_vector = np.mean(read_vectors, axis=0)

    # 3. Get all books (candidate pool)
    # Exclude books already read
    read_book_ids = {ub.book_id for ub in user_books}
    all_books = crud.get_books(db, limit=1000) # Simple limit for now
    candidates = [b for b in all_books if b.id not in read_book_ids and b.embedding]

    # 4. Calculate scores
    recommendations = []
    for book in candidates:
        sim = cosine_similarity(user_vector, book.embedding)
        
        recommendations.append({
            "book": book,
            "score": float(sim)
        })
    
    # 5. Sort and return top K
    recommendations.sort(key=lambda x: x["score"], reverse=True)
    top_recs = recommendations[:top_k]
    
    items = []
    for rec in top_recs:
        items.append({
            "book_id": rec["book"].id,
            "title": rec["book"].title,
            "author": rec["book"].author,
            "score": rec["score"],
            "reasons": {"vector_similarity": rec["score"]}
        })
        
    return {
        "user_id": user_id,
        "strategy": strategy,
        "items": items
    }
