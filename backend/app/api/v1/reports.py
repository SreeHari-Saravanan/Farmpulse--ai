from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
import logging
import os
import aiofiles

from app.models.report import (
    ReportCreate, ReportResponse, ReportUpdate, ReportStatus, 
    ReportPriority, SymptomInput
)
from app.core.security import get_current_user
from app.core.database import get_database
from app.core.config import settings
from app.services.ai_inference import ai_service
from app.services.notification_service import notification_service

router = APIRouter()
logger = logging.getLogger(__name__)


def report_to_response(report: dict, db_users: dict = None) -> ReportResponse:
    """Convert database report to response model"""
    farmer_name = None
    vet_name = None
    
    if db_users:
        farmer = db_users.get(report.get("farmer_id"))
        vet = db_users.get(report.get("vet_id"))
        farmer_name = farmer.get("full_name") if farmer else None
        vet_name = vet.get("full_name") if vet else None
    
    return ReportResponse(
        id=str(report["_id"]),
        farmer_id=report["farmer_id"],
        farmer_name=farmer_name,
        vet_id=report.get("vet_id"),
        vet_name=vet_name,
        status=report["status"],
        priority=report["priority"],
        symptoms=report["symptoms"],
        ai_prediction=report.get("ai_prediction"),
        vet_notes=report.get("vet_notes"),
        diagnosis=report.get("diagnosis"),
        treatment=report.get("treatment"),
        prescription=report.get("prescription"),
        animal_type=report.get("animal_type"),
        crop_type=report.get("crop_type"),
        created_at=report["created_at"],
        updated_at=report["updated_at"],
        closed_at=report.get("closed_at"),
        pdf_url=report.get("pdf_url")
    )


@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    text_symptoms: Optional[str] = Form(None),
    voice_transcript: Optional[str] = Form(None),
    animal_type: Optional[str] = Form(None),
    crop_type: Optional[str] = Form(None),
    location_lng: Optional[float] = Form(None),
    location_lat: Optional[float] = Form(None),
    images: List[UploadFile] = File(None),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new report with symptoms
    
    Farmers only. Supports text, voice, and image inputs.
    """
    if current_user["role"] != "farmer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only farmers can create reports"
        )
    
    db = get_database()
    
    # Save uploaded images
    image_paths = []
    if images:
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        for image in images:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"{current_user['id']}_{timestamp}_{image.filename}"
            file_path = os.path.join(settings.UPLOAD_DIR, filename)
            
            async with aiofiles.open(file_path, 'wb') as f:
                content = await image.read()
                await f.write(content)
            
            image_paths.append(f"/uploads/{filename}")
    
    # Prepare location
    location = None
    if location_lng is not None and location_lat is not None:
        location = {
            "type": "Point",
            "coordinates": [location_lng, location_lat]
        }
    
    # Prepare symptoms
    symptoms = SymptomInput(
        text=text_symptoms,
        images=image_paths,
        voice_transcript=voice_transcript,
        location=location
    )
    
    # Run AI analysis
    context = {
        "animal_type": animal_type,
        "crop_type": crop_type
    }
    
    ai_prediction = await ai_service.hybrid_analysis(
        text=text_symptoms or voice_transcript,
        images=[os.path.join(settings.UPLOAD_DIR, os.path.basename(path)) for path in image_paths] if image_paths else None,
        context=context
    )
    
    # Find similar cases
    similar_cases = await ai_service.find_similar_cases(
        disease_label=ai_prediction["disease_label"]
    )
    ai_prediction["similar_cases"] = similar_cases
    
    # Determine priority based on confidence and disease type
    priority = ReportPriority.NORMAL
    if ai_prediction["confidence"] > 0.85:
        # High confidence predictions might need urgent attention
        if "urgent" in ai_prediction["disease_label"].lower():
            priority = ReportPriority.URGENT
        else:
            priority = ReportPriority.HIGH
    
    # Create report
    report_data = {
        "farmer_id": current_user["id"],
        "status": ReportStatus.PENDING,
        "priority": priority,
        "symptoms": symptoms.dict(),
        "ai_prediction": ai_prediction,
        "animal_type": animal_type,
        "crop_type": crop_type,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await db.reports.insert_one(report_data)
    report_data["_id"] = result.inserted_id
    report_data["id"] = str(result.inserted_id)
    
    logger.info(f"Report created: {report_data['id']} by farmer {current_user['id']}")
    
    # Check for outbreak conditions
    await check_and_alert_outbreak(db, ai_prediction["disease_label"], location)
    
    return report_to_response(report_data)


@router.get("/", response_model=List[ReportResponse])
async def get_reports(
    status_filter: Optional[ReportStatus] = None,
    priority_filter: Optional[ReportPriority] = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """
    Get reports based on user role
    
    - Farmers: their own reports
    - Vets: all pending/in-progress reports (case queue)
    - Admin: all reports
    """
    db = get_database()
    
    # Build query based on role
    query = {}
    if current_user["role"] == "farmer":
        query["farmer_id"] = current_user["id"]
    elif current_user["role"] == "vet":
        # Vets see unassigned or their assigned cases
        query["$or"] = [
            {"status": {"$in": [ReportStatus.PENDING, ReportStatus.IN_PROGRESS]}},
            {"vet_id": current_user["id"]}
        ]
    
    # Apply filters
    if status_filter:
        query["status"] = status_filter
    if priority_filter:
        query["priority"] = priority_filter
    
    # Fetch reports
    reports = await db.reports.find(query).sort("created_at", -1).limit(limit).to_list(length=limit)
    
    # Fetch user details for names
    user_ids = set()
    for report in reports:
        user_ids.add(report.get("farmer_id"))
        if report.get("vet_id"):
            user_ids.add(report["vet_id"])
    
    users = await db.users.find({"_id": {"$in": list(user_ids)}}).to_list(length=None)
    user_map = {str(user["_id"]): user for user in users}
    
    return [report_to_response(report, user_map) for report in reports]


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(report_id: str, current_user: dict = Depends(get_current_user)):
    """
    Get a specific report by ID
    
    Access control: farmers see their own, vets see assigned/available, admin sees all
    """
    db = get_database()
    
    try:
        report = await db.reports.find_one({"_id": ObjectId(report_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid report ID")
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Access control
    if current_user["role"] == "farmer" and report["farmer_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized to view this report")
    
    # Fetch user details
    users = await db.users.find({
        "_id": {"$in": [report.get("farmer_id"), report.get("vet_id")]}
    }).to_list(length=None)
    user_map = {str(user["_id"]): user for user in users}
    
    return report_to_response(report, user_map)


@router.patch("/{report_id}", response_model=ReportResponse)
async def update_report(
    report_id: str,
    update_data: ReportUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update a report (for vets)
    
    Vets can update status, diagnosis, treatment, prescription
    """
    if current_user["role"] != "vet":
        raise HTTPException(status_code=403, detail="Only vets can update reports")
    
    db = get_database()
    
    try:
        report = await db.reports.find_one({"_id": ObjectId(report_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid report ID")
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Prepare update
    update_dict = {
        "updated_at": datetime.utcnow()
    }
    
    if update_data.status:
        update_dict["status"] = update_data.status
        if update_data.status == ReportStatus.IN_PROGRESS and not report.get("vet_id"):
            update_dict["vet_id"] = current_user["id"]
        if update_data.status == ReportStatus.CLOSED:
            update_dict["closed_at"] = datetime.utcnow()
    
    if update_data.priority:
        update_dict["priority"] = update_data.priority
    if update_data.vet_notes:
        update_dict["vet_notes"] = update_data.vet_notes
    if update_data.diagnosis:
        update_dict["diagnosis"] = update_data.diagnosis
    if update_data.treatment:
        update_dict["treatment"] = update_data.treatment
    if update_data.prescription:
        update_dict["prescription"] = update_data.prescription
    
    # Log feedback if vet overrides AI prediction
    if update_data.final_disease_label and report.get("ai_prediction"):
        original_label = report["ai_prediction"]["disease_label"]
        if original_label != update_data.final_disease_label:
            await ai_service.log_feedback(
                report_id=report_id,
                original_prediction=original_label,
                corrected_prediction=update_data.final_disease_label,
                inputs={
                    "text": report["symptoms"].get("text"),
                    "images": report["symptoms"].get("images")
                },
                vet_id=current_user["id"]
            )
            # Update AI prediction with corrected label
            update_dict["ai_prediction.disease_label"] = update_data.final_disease_label
    
    # Update report
    await db.reports.update_one(
        {"_id": ObjectId(report_id)},
        {"$set": update_dict}
    )
    
    # Notify farmer
    await notification_service.send_notification(
        user_id=report["farmer_id"],
        title="Report Updated",
        message=f"Your report has been updated by a veterinarian.",
        channels=["in_app"],
        data={"report_id": report_id}
    )
    
    # Fetch updated report
    updated_report = await db.reports.find_one({"_id": ObjectId(report_id)})
    
    logger.info(f"Report {report_id} updated by vet {current_user['id']}")
    
    return report_to_response(updated_report)


async def check_and_alert_outbreak(db, disease_label: str, location: dict):
    """
    Check if disease reports indicate an outbreak and send alerts
    """
    if not location:
        return
    
    # Count recent similar reports in area
    from datetime import timedelta
    time_threshold = datetime.utcnow() - timedelta(hours=settings.OUTBREAK_TIME_WINDOW_HOURS)
    
    nearby_reports = await db.reports.count_documents({
        "ai_prediction.disease_label": disease_label,
        "created_at": {"$gte": time_threshold},
        "symptoms.location": {
            "$near": {
                "$geometry": location,
                "$maxDistance": settings.OUTBREAK_RADIUS_KM * 1000
            }
        }
    })
    
    if nearby_reports >= settings.OUTBREAK_THRESHOLD:
        logger.warning(f"Outbreak detected: {disease_label} with {nearby_reports} cases")
        await notification_service.create_outbreak_alert(
            disease_label=disease_label,
            location=location,
            radius_km=settings.OUTBREAK_RADIUS_KM,
            affected_count=nearby_reports
        )
