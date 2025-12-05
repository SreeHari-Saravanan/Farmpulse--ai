from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List
from datetime import datetime, timedelta
import logging

from app.core.security import get_current_user
from app.core.database import get_database

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health")
async def health_check(current_user: dict = Depends(get_current_user)):
    """
    System health check
    
    Admin only
    """
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    db = get_database()
    
    # Check database connection
    try:
        await db.command("ping")
        db_status = "healthy"
    except:
        db_status = "unhealthy"
    
    # Get system stats
    total_users = await db.users.count_documents({})
    total_reports = await db.reports.count_documents({})
    pending_reports = await db.reports.count_documents({"status": "pending"})
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "stats": {
            "total_users": total_users,
            "total_reports": total_reports,
            "pending_reports": pending_reports
        },
        "timestamp": datetime.utcnow()
    }


@router.get("/analytics")
async def get_analytics(
    days: int = 30,
    current_user: dict = Depends(get_current_user)
):
    """
    Get system analytics
    
    Admin only
    """
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    db = get_database()
    
    # Date range
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Reports by status
    pipeline_status = [
        {"$match": {"created_at": {"$gte": start_date}}},
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]
    reports_by_status = await db.reports.aggregate(pipeline_status).to_list(length=None)
    
    # Reports by disease
    pipeline_disease = [
        {"$match": {"created_at": {"$gte": start_date}, "ai_prediction.disease_label": {"$exists": True}}},
        {"$group": {"_id": "$ai_prediction.disease_label", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    reports_by_disease = await db.reports.aggregate(pipeline_disease).to_list(length=None)
    
    # Reports by priority
    pipeline_priority = [
        {"$match": {"created_at": {"$gte": start_date}}},
        {"$group": {"_id": "$priority", "count": {"$sum": 1}}}
    ]
    reports_by_priority = await db.reports.aggregate(pipeline_priority).to_list(length=None)
    
    # User registrations
    new_users = await db.users.count_documents({"created_at": {"$gte": start_date}})
    
    # Average resolution time (completed reports)
    pipeline_resolution = [
        {"$match": {"status": "completed", "closed_at": {"$exists": True}}},
        {"$project": {
            "resolution_time": {
                "$subtract": ["$closed_at", "$created_at"]
            }
        }},
        {"$group": {
            "_id": None,
            "avg_resolution_ms": {"$avg": "$resolution_time"}
        }}
    ]
    resolution_data = await db.reports.aggregate(pipeline_resolution).to_list(length=None)
    avg_resolution_hours = None
    if resolution_data:
        avg_resolution_hours = resolution_data[0].get("avg_resolution_ms", 0) / (1000 * 3600)
    
    return {
        "date_range": {
            "start": start_date,
            "end": datetime.utcnow(),
            "days": days
        },
        "reports_by_status": {item["_id"]: item["count"] for item in reports_by_status},
        "top_diseases": [{"disease": item["_id"], "count": item["count"]} for item in reports_by_disease],
        "reports_by_priority": {item["_id"]: item["count"] for item in reports_by_priority},
        "new_users": new_users,
        "avg_resolution_hours": round(avg_resolution_hours, 2) if avg_resolution_hours else None
    }


@router.get("/users")
async def get_users(
    role: str = None,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    """
    Get list of users
    
    Admin only
    """
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    db = get_database()
    
    query = {}
    if role:
        query["role"] = role
    
    users = await db.users.find(query).limit(limit).to_list(length=limit)
    
    # Remove sensitive data
    for user in users:
        user.pop("hashed_password", None)
        user["id"] = str(user.pop("_id"))
    
    return {"users": users, "total": len(users)}


@router.get("/export/reports")
async def export_reports(
    format: str = "json",
    days: int = 30,
    current_user: dict = Depends(get_current_user)
):
    """
    Export reports data
    
    Admin only. Formats: json, csv
    """
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    db = get_database()
    
    start_date = datetime.utcnow() - timedelta(days=days)
    reports = await db.reports.find({"created_at": {"$gte": start_date}}).to_list(length=None)
    
    if format == "csv":
        # Convert to CSV format
        import io
        import csv
        
        output = io.StringIO()
        if reports:
            fieldnames = ["id", "farmer_id", "status", "priority", "disease", "confidence", "created_at"]
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            
            for report in reports:
                writer.writerow({
                    "id": str(report["_id"]),
                    "farmer_id": report.get("farmer_id"),
                    "status": report.get("status"),
                    "priority": report.get("priority"),
                    "disease": report.get("ai_prediction", {}).get("disease_label", ""),
                    "confidence": report.get("ai_prediction", {}).get("confidence", ""),
                    "created_at": report.get("created_at")
                })
        
        return {"data": output.getvalue(), "format": "csv"}
    
    # Default JSON format
    for report in reports:
        report["id"] = str(report.pop("_id"))
    
    return {"data": reports, "format": "json", "total": len(reports)}


@router.get("/geo-heatmap")
async def get_geo_heatmap(
    disease: str = None,
    days: int = 30,
    current_user: dict = Depends(get_current_user)
):
    """
    Get geographic heatmap data for disease distribution
    
    Admin only
    """
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    db = get_database()
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = {
        "created_at": {"$gte": start_date},
        "symptoms.location": {"$exists": True}
    }
    
    if disease:
        query["ai_prediction.disease_label"] = disease
    
    reports = await db.reports.find(query).to_list(length=None)
    
    # Extract locations
    heatmap_data = []
    for report in reports:
        location = report.get("symptoms", {}).get("location")
        if location and location.get("coordinates"):
            lng, lat = location["coordinates"]
            heatmap_data.append({
                "lat": lat,
                "lng": lng,
                "disease": report.get("ai_prediction", {}).get("disease_label"),
                "intensity": report.get("ai_prediction", {}).get("confidence", 0.5)
            })
    
    return {
        "points": heatmap_data,
        "total": len(heatmap_data),
        "disease_filter": disease,
        "days": days
    }
