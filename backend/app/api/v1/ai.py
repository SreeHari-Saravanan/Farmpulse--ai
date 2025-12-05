from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import Optional
import logging
import os

from app.core.security import get_current_user
from app.core.config import settings
from app.services.ai_inference import ai_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/analyze-text")
async def analyze_text(
    text: str,
    animal_type: Optional[str] = None,
    crop_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze text symptoms using NLP model
    """
    context = {
        "animal_type": animal_type,
        "crop_type": crop_type
    }
    
    result = await ai_service.analyze_text_symptoms(text, context)
    
    logger.info(f"Text analysis for user {current_user['id']}: {result['disease_label']}")
    
    return result


@router.post("/analyze-image")
async def analyze_image(
    image: UploadFile = File(...),
    animal_type: Optional[str] = None,
    crop_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze image using computer vision model
    """
    # Save temporary image
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    temp_path = os.path.join(settings.UPLOAD_DIR, f"temp_{current_user['id']}_{image.filename}")
    
    with open(temp_path, "wb") as f:
        content = await image.read()
        f.write(content)
    
    context = {
        "animal_type": animal_type,
        "crop_type": crop_type
    }
    
    result = await ai_service.analyze_image(temp_path, context)
    
    # Clean up temp file
    try:
        os.remove(temp_path)
    except:
        pass
    
    logger.info(f"Image analysis for user {current_user['id']}: {result['disease_label']}")
    
    return result


@router.get("/similar-cases/{disease_label}")
async def get_similar_cases(
    disease_label: str,
    limit: int = 5,
    current_user: dict = Depends(get_current_user)
):
    """
    Find similar historical cases
    
    Vets only
    """
    if current_user["role"] != "vet":
        raise HTTPException(status_code=403, detail="Vets only")
    
    similar_ids = await ai_service.find_similar_cases(disease_label, limit=limit)
    
    return {"similar_case_ids": similar_ids}
