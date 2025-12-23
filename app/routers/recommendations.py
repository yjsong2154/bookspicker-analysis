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
            "cover_image": rec["book"].cover_image,
            "score": rec["score"],
            "reasons": {"vector_similarity": rec["score"]}
        })
        
    return {
        "user_id": user_id,
        "strategy": strategy,
        "items": items
    }

@router.get("/{id_backend}/advanced-recommendations", response_model=schemas.AdvancedRecommendationResponse)
def get_advanced_recommendations(
    id_backend: int,
    db: Session = Depends(get_db)
):
    # 1. Get User by Backend ID
    user = crud.get_user_by_backend_id(db, id_backend)
    if not user:
        # If user not found, maybe return generic recommendations?
        # For now, raise 404
        raise HTTPException(status_code=404, detail="User not found")

    # 2. Get User's Read History
    user_books = crud.get_user_read_history(db, user_id=user.id)
    
    # 3. Calculate Profile (Vector & Tags)
    read_vectors = []
    tag_counts = {}
    
    read_book_ids = set()

    for ub in user_books:
        read_book_ids.add(ub.book_id)
        if ub.book:
            # Vector
            if ub.book.embedding:
                read_vectors.append(ub.book.embedding)
            
            # Tags
            if ub.book.tags:
                for tag, weight in ub.book.tags.items():
                    # Check if weight is int or float or what. Assuming int/float.
                    # If dict is {tag: count}
                    current = tag_counts.get(tag, 0)
                    tag_counts[tag] = current + (weight if isinstance(weight, (int, float)) else 1)

    # If no history, we can't recommend based on profile. Return empty or popular?
    # Requirement: "user books를 기준으로 한번 계산을 해줘"
    if not read_vectors:
        return {"sections": []} # Or handle cold start

    # Compute Average Vector
    avg_vector = np.mean(read_vectors, axis=0).tolist()
    
    # Update User Profile in DB
    crud.update_user_preferences(db, user.id, avg_vector, tag_counts)
    
    # 4. Fetch Candidates
    all_books = crud.get_all_books_with_embedding(db)
    candidates = [b for b in all_books if b.id not in read_book_ids]
    
    sections = []
    
    # Helper for converting to BookSimple
    def to_simple(books):
        return [schemas.BookSimple.model_validate(b) for b in books]

    # --- 5.1 Vector Best Match (Top 1) ---
    # Calc similarities
    scored_candidates = []
    for book in candidates:
        sim = cosine_similarity(avg_vector, book.embedding)
        scored_candidates.append((book, sim))
    
    # Sort by similarity desc
    scored_candidates.sort(key=lambda x: x[1], reverse=True)
    
    if scored_candidates:
        best_book = scored_candidates[0][0]
        sections.append(schemas.RecommendationSection(
            title="ai가 가장 추천",
            books=to_simple([best_book])
        ))
    
    # --- 5.2 Vector Next Matches (Top 2-11) ---
    next_books = [x[0] for x in scored_candidates[1:11]]
    if next_books:
        sections.append(schemas.RecommendationSection(
            title="ai가 추천하는 책",
            books=to_simple(next_books)
        ))
        
    # --- 5.3 Top 3 Tags ---
    # Sort tags by count
    sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    top_3_tags = [t[0] for t in sorted_tags[:3]]
    
    for tag in top_3_tags:
        # Filter candidates by tag presence and sort by tag weight/relevance if available? 
        # Or just vector similarity again?
        # "해당 태그의 책 10권". Let's pick books that HAVE this tag, sorted by that tag's weight desc.
        
        tag_books = []
        for book in candidates:
            if book.tags and tag in book.tags:
                weight = book.tags[tag]
                tag_books.append((book, weight))
        
        # Sort by weight desc
        tag_books.sort(key=lambda x: x[1], reverse=True)
        
        top_tag_books = [x[0] for x in tag_books[:10]]
        if top_tag_books:
            sections.append(schemas.RecommendationSection(
                title=f"{tag}",
                books=to_simple(top_tag_books)
            ))
            
    return {"sections": sections}
