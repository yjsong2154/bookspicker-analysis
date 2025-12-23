from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os
import uuid
from ..services import analysis
from pydantic import BaseModel
from typing import Dict, Any, List

router = APIRouter(
    prefix="/analysis",
    tags=["analysis"],
)

UPLOAD_DIR = "storage/temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class AnalysisResponse(BaseModel):
    tags: Dict[str, Any]
    vector: List[float]

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_epub_file(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".epub"):
        raise HTTPException(status_code=400, detail="Only EPUB files are allowed.")

    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.epub")
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Determine strict mode from some param? For now just run analysis.
        # The existing analysis service returns {"tags": ..., "embedding": ...}
        # "vector" in requirement vs "embedding" in code. I will map it.
        
        result = analysis.analyze_epub(file_path)
        
        return {
            "tags": result.get("tags", {}),
            "vector": result.get("embedding", [])
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # User might want to keep the file? The prompt implies "input epub -> output json".
        # It's a functional transformation. We can clean up the input file.
        if os.path.exists(file_path):
            os.remove(file_path)
