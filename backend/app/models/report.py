from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class ReportStatus(str, Enum):
    """Report status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CLOSED = "closed"


class ReportPriority(str, Enum):
    """Report priority enumeration"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class SymptomInput(BaseModel):
    """Symptom input model"""
    text: Optional[str] = None
    images: Optional[List[str]] = []  # List of image URLs/paths
    voice_transcript: Optional[str] = None
    location: Optional[dict] = None  # {"type": "Point", "coordinates": [lng, lat]}


class AIprediction(BaseModel):
    """AI prediction model"""
    disease_label: str
    confidence: float = Field(ge=0.0, le=1.0)
    explanation: Optional[str] = None
    highlighted_features: Optional[List[str]] = []
    bounding_boxes: Optional[List[dict]] = []
    similar_cases: Optional[List[str]] = []  # List of similar report IDs


class ReportCreate(BaseModel):
    """Report creation model"""
    symptoms: SymptomInput
    animal_type: Optional[str] = None  # For livestock
    crop_type: Optional[str] = None    # For crops


class ReportUpdate(BaseModel):
    """Report update model (for vets)"""
    status: Optional[ReportStatus] = None
    priority: Optional[ReportPriority] = None
    vet_notes: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    prescription: Optional[str] = None
    final_disease_label: Optional[str] = None


class ReportResponse(BaseModel):
    """Report response model"""
    id: str
    farmer_id: str
    farmer_name: Optional[str] = None
    vet_id: Optional[str] = None
    vet_name: Optional[str] = None
    status: ReportStatus
    priority: ReportPriority
    symptoms: SymptomInput
    ai_prediction: Optional[AIprediction] = None
    vet_notes: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    prescription: Optional[str] = None
    animal_type: Optional[str] = None
    crop_type: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None
    pdf_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class FeedbackCreate(BaseModel):
    """Feedback creation model"""
    report_id: str
    vet_id: str
    original_prediction: str
    corrected_prediction: str
    confidence: float
    notes: Optional[str] = None


class SessionCreate(BaseModel):
    """Video session creation model"""
    report_id: str
    farmer_id: str
    vet_id: Optional[str] = None


class SessionResponse(BaseModel):
    """Video session response model"""
    id: str
    report_id: str
    farmer_id: str
    vet_id: str
    call_start: datetime
    call_end: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    session_notes: Optional[str] = None
    
    class Config:
        from_attributes = True
