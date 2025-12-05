from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class AlertType(str, Enum):
    """Alert type enumeration"""
    OUTBREAK = "outbreak"
    APPOINTMENT = "appointment"
    REPORT_UPDATE = "report_update"
    SYSTEM = "system"


class AlertCreate(BaseModel):
    """Alert creation model"""
    user_id: str
    alert_type: AlertType
    title: str
    message: str
    data: Optional[dict] = None
    location: Optional[dict] = None


class AlertResponse(BaseModel):
    """Alert response model"""
    id: str
    user_id: str
    alert_type: AlertType
    title: str
    message: str
    data: Optional[dict] = None
    location: Optional[dict] = None
    is_read: bool = False
    created_at: datetime
    
    class Config:
        from_attributes = True


class NotificationCreate(BaseModel):
    """Notification creation model"""
    user_id: str
    channel: str  # "email", "sms", "push", "in_app"
    title: str
    message: str
    data: Optional[dict] = None
