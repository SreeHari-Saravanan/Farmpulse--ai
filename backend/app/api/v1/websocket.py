"""
WebSocket Router for Real-time Communication

Handles:
- WebRTC signaling (offer, answer, ICE candidates)
- Real-time notifications
- Chat messages during video calls
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import logging
import json

router = APIRouter()
logger = logging.getLogger(__name__)

# Active WebSocket connections
# Format: {user_id: websocket}
active_connections: Dict[str, WebSocket] = {}

# Active signaling sessions
# Format: {session_id: {farmer_ws, vet_ws}}
signaling_sessions: Dict[str, Dict[str, WebSocket]] = {}


async def broadcast_to_vets(message: dict):
    """
    Broadcast a message to all connected vets
    """
    from app.core.database import get_database
    
    db = get_database()
    
    # Get all vet user IDs
    vets = await db.users.find({"role": "vet"}).to_list(100)
    vet_ids = [str(vet["_id"]) for vet in vets]
    
    # Send to all connected vets
    disconnected = []
    for vet_id in vet_ids:
        if vet_id in active_connections:
            try:
                await active_connections[vet_id].send_json(message)
            except:
                disconnected.append(vet_id)
    
    # Clean up disconnected connections
    for vet_id in disconnected:
        active_connections.pop(vet_id, None)


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for real-time communication
    
    Handles:
    - General notifications
    - Chat messages
    - System alerts
    """
    await websocket.accept()
    active_connections[user_id] = websocket
    
    logger.info(f"WebSocket connected: user {user_id}")
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            message_type = message.get("type")
            
            if message_type == "ping":
                # Keepalive
                await websocket.send_json({"type": "pong"})
            
            elif message_type == "chat":
                # Forward chat message to recipient
                recipient_id = message.get("recipient_id")
                if recipient_id in active_connections:
                    await active_connections[recipient_id].send_json({
                        "type": "chat",
                        "from": user_id,
                        "message": message.get("message"),
                        "timestamp": message.get("timestamp")
                    })
            
            logger.debug(f"Received from {user_id}: {message_type}")
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: user {user_id}")
        active_connections.pop(user_id, None)
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        active_connections.pop(user_id, None)


@router.websocket("/ws/signaling/{session_id}/{user_id}/{role}")
async def signaling_endpoint(
    websocket: WebSocket, 
    session_id: str, 
    user_id: str,
    role: str  # "farmer" or "vet"
):
    """
    WebRTC signaling WebSocket endpoint
    
    Handles peer-to-peer connection negotiation:
    - SDP offer/answer exchange
    - ICE candidate exchange
    
    Flow:
    1. Both peers connect to this endpoint
    2. Farmer sends offer -> forwarded to vet
    3. Vet sends answer -> forwarded to farmer
    4. Both exchange ICE candidates
    5. Direct P2P connection established
    """
    await websocket.accept()
    
    # Initialize session if needed
    if session_id not in signaling_sessions:
        signaling_sessions[session_id] = {}
    
    # Store WebSocket for this role
    signaling_sessions[session_id][role] = websocket
    
    logger.info(f"Signaling WebSocket connected: session {session_id}, role {role}")
    
    try:
        while True:
            # Receive signaling message
            data = await websocket.receive_text()
            message = json.loads(data)
            
            message_type = message.get("type")
            
            # Forward to peer
            peer_role = "vet" if role == "farmer" else "farmer"
            peer_ws = signaling_sessions[session_id].get(peer_role)
            
            if message_type == "ready":
                logger.info(f"{role} is ready in session {session_id}")
                # Notify peer that this user is ready
                if peer_ws:
                    await peer_ws.send_json({
                        "type": "ready",
                        "from": role
                    })
            
            elif peer_ws:
                if message_type == "offer":
                    logger.info(f"Forwarding offer from {role} to {peer_role}")
                    await peer_ws.send_json({
                        "type": "offer",
                        "sdp": message.get("sdp"),
                        "from": role
                    })
                
                elif message_type == "answer":
                    logger.info(f"Forwarding answer from {role} to {peer_role}")
                    await peer_ws.send_json({
                        "type": "answer",
                        "sdp": message.get("sdp"),
                        "from": role
                    })
                
                elif message_type == "ice-candidate":
                    logger.debug(f"Forwarding ICE candidate from {role} to {peer_role}")
                    await peer_ws.send_json({
                        "type": "ice-candidate",
                        "candidate": message.get("candidate"),
                        "from": role
                    })
                
                elif message_type == "hangup":
                    logger.info(f"Hangup signal from {role}")
                    await peer_ws.send_json({
                        "type": "hangup",
                        "from": role
                    })
                    break
            else:
                logger.warning(f"Peer {peer_role} not connected for session {session_id}")
    
    except WebSocketDisconnect:
        logger.info(f"Signaling WebSocket disconnected: session {session_id}, role {role}")
    except Exception as e:
        logger.error(f"Signaling WebSocket error: {e}")
    finally:
        # Cleanup
        if session_id in signaling_sessions:
            signaling_sessions[session_id].pop(role, None)
            # Notify peer about disconnect
            peer_role = "vet" if role == "farmer" else "farmer"
            peer_ws = signaling_sessions[session_id].get(peer_role)
            if peer_ws:
                try:
                    await peer_ws.send_json({
                        "type": "peer-disconnected",
                        "from": role
                    })
                except:
                    pass
            # Remove session if both disconnected
            if not signaling_sessions[session_id]:
                del signaling_sessions[session_id]


async def send_notification_to_user(user_id: str, notification: dict):
    """
    Send notification to a specific user via WebSocket
    
    Called by notification service
    """
    if user_id in active_connections:
        try:
            await active_connections[user_id].send_json(notification)
            logger.info(f"Notification sent to user {user_id}")
        except Exception as e:
            logger.error(f"Failed to send notification to user {user_id}: {e}")
            active_connections.pop(user_id, None)
