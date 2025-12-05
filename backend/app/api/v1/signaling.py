from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from bson import ObjectId
import logging

from app.core.security import get_current_user
from app.core.database import get_database
from app.models.report import SessionCreate

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/session/create")
async def create_signaling_session(
    session_data: SessionCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new WebRTC signaling session
    
    Called when starting a video call
    """
    db = get_database()
    
    # Verify report exists
    try:
        report = await db.reports.find_one({"_id": ObjectId(session_data.report_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid report ID")
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Create session
    session = {
        "report_id": session_data.report_id,
        "farmer_id": session_data.farmer_id,
        "vet_id": session_data.vet_id,
        "call_start": datetime.utcnow(),
        "active": True
    }
    
    result = await db.sessions.insert_one(session)
    session["id"] = str(result.inserted_id)
    
    logger.info(f"Signaling session created: {session['id']}")
    
    # Notify all vets about new session via WebSocket
    from app.api.v1.websocket import broadcast_to_vets
    await broadcast_to_vets({
        "type": "new_session",
        "session_id": session["id"],
        "report_id": session_data.report_id,
        "farmer_id": session_data.farmer_id
    })
    
    return {
        "session_id": session["id"],
        "report_id": session_data.report_id,
        "farmer_id": session_data.farmer_id,
        "vet_id": session_data.vet_id,
        "call_start": session["call_start"]
    }


@router.post("/session/{session_id}/end")
async def end_signaling_session(
    session_id: str,
    notes: str = None,
    current_user: dict = Depends(get_current_user)
):
    """
    End a WebRTC signaling session
    
    Called when video call ends
    """
    db = get_database()
    
    try:
        session = await db.sessions.find_one({"_id": ObjectId(session_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid session ID")
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Calculate duration
    call_end = datetime.utcnow()
    duration = (call_end - session["call_start"]).total_seconds()
    
    # Update session
    update_data = {
        "call_end": call_end,
        "duration_seconds": int(duration),
        "active": False
    }
    
    if notes:
        update_data["session_notes"] = notes
    
    await db.sessions.update_one(
        {"_id": ObjectId(session_id)},
        {"$set": update_data}
    )
    
    logger.info(f"Signaling session ended: {session_id}, duration: {duration}s")
    
    return {
        "session_id": session_id,
        "duration_seconds": int(duration)
    }


@router.get("/sessions/active")
async def get_active_sessions(current_user: dict = Depends(get_current_user)):
    """
    Get all active video sessions (for vets to join)
    """
    db = get_database()
    
    sessions = await db.sessions.find({"active": True, "vet_id": None}).to_list(100)
    
    return [
        {
            "id": str(session["_id"]),
            "report_id": session["report_id"],
            "farmer_id": session["farmer_id"],
            "call_start": session["call_start"]
        }
        for session in sessions
    ]


@router.patch("/session/{session_id}/join")
async def join_session(
    session_id: str,
    vet_id: str = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Vet joins an active session
    """
    db = get_database()
    
    try:
        session = await db.sessions.find_one({"_id": ObjectId(session_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid session ID")
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Update session with vet_id
    await db.sessions.update_one(
        {"_id": ObjectId(session_id)},
        {"$set": {"vet_id": current_user["id"]}}
    )
    
    logger.info(f"Vet {current_user['id']} joined session {session_id}")
    
    return {
        "session_id": session_id,
        "vet_id": current_user["id"]
    }


@router.get("/session/{session_id}")
async def get_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get session details
    """
    db = get_database()
    
    try:
        session = await db.sessions.find_one({"_id": ObjectId(session_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid session ID")
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session["id"] = str(session.pop("_id"))
    
    return session
