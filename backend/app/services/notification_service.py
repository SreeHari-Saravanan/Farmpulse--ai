"""
Notification Service

Handles sending notifications via multiple channels:
- In-app notifications (WebSocket)
- Email (SMTP)
- SMS (Twilio or other providers)
- Push notifications (Firebase Cloud Messaging)

TODO: Configure external service API keys in .env
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import settings
from app.core.database import get_database
from app.core.redis_client import publish_message

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for sending notifications"""
    
    async def send_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        channels: List[str] = ["in_app"],
        data: Optional[Dict] = None
    ):
        """
        Send notification via specified channels
        
        Args:
            user_id: Target user ID
            title: Notification title
            message: Notification message
            channels: List of channels ["in_app", "email", "sms", "push"]
            data: Additional data payload
        """
        logger.info(f"Sending notification to user {user_id}: {title}")
        
        # Get user details
        db = get_database()
        user = await db.users.find_one({"_id": user_id})
        
        if not user:
            logger.error(f"User {user_id} not found")
            return
        
        # Send via each channel
        for channel in channels:
            try:
                if channel == "in_app":
                    await self._send_in_app(user_id, title, message, data)
                elif channel == "email":
                    await self._send_email(user, title, message)
                elif channel == "sms":
                    await self._send_sms(user, message)
                elif channel == "push":
                    await self._send_push(user, title, message, data)
            except Exception as e:
                logger.error(f"Error sending {channel} notification: {e}")
    
    async def _send_in_app(
        self, 
        user_id: str, 
        title: str, 
        message: str, 
        data: Optional[Dict]
    ):
        """Send in-app notification via WebSocket"""
        # Publish to Redis for WebSocket delivery
        await publish_message(f"notifications:{user_id}", {
            "type": "notification",
            "title": title,
            "message": message,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Store in database
        db = get_database()
        await db.notifications.insert_one({
            "user_id": user_id,
            "title": title,
            "message": message,
            "data": data,
            "is_read": False,
            "created_at": datetime.utcnow()
        })
    
    async def _send_email(self, user: Dict, title: str, message: str):
        """
        Send email notification
        
        TODO: Configure SMTP settings in .env
        - SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD
        """
        if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            logger.warning("SMTP not configured, skipping email")
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = settings.EMAIL_FROM
            msg['To'] = user['email']
            msg['Subject'] = title
            
            body = f"""
            <html>
                <body>
                    <h2>{title}</h2>
                    <p>{message}</p>
                    <hr>
                    <p>FarmPulse AI - Agricultural Health Platform</p>
                </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
            
            logger.info(f"Email sent to {user['email']}")
        except Exception as e:
            logger.error(f"Email sending failed: {e}")
    
    async def _send_sms(self, user: Dict, message: str):
        """
        Send SMS notification
        
        TODO: Configure Twilio or other SMS provider
        - TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER
        
        Example with Twilio:
            from twilio.rest import Client
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            client.messages.create(
                to=user['phone'],
                from_=settings.TWILIO_PHONE_NUMBER,
                body=message
            )
        """
        if not user.get('phone'):
            logger.warning(f"No phone number for user {user['_id']}")
            return
        
        if not settings.TWILIO_ACCOUNT_SID:
            logger.warning("SMS service not configured")
            return
        
        logger.info(f"SMS would be sent to {user['phone']}: {message}")
        # Implement actual SMS sending when credentials are configured
    
    async def _send_push(
        self, 
        user: Dict, 
        title: str, 
        message: str, 
        data: Optional[Dict]
    ):
        """
        Send push notification
        
        TODO: Configure Firebase Cloud Messaging
        - Install firebase-admin package
        - Add Firebase service account JSON
        
        Example:
            import firebase_admin
            from firebase_admin import messaging
            
            message = messaging.Message(
                notification=messaging.Notification(title=title, body=message),
                data=data,
                token=user['fcm_token']
            )
            messaging.send(message)
        """
        logger.info(f"Push notification would be sent to user {user['_id']}")
        # Implement actual push when Firebase is configured
    
    async def create_outbreak_alert(
        self,
        disease_label: str,
        location: Dict,
        radius_km: float,
        affected_count: int
    ):
        """
        Create and send outbreak alerts to nearby farmers
        
        Args:
            disease_label: Disease causing outbreak
            location: Center point {"type": "Point", "coordinates": [lng, lat]}
            radius_km: Alert radius in kilometers
            affected_count: Number of affected reports
        """
        logger.info(f"Creating outbreak alert for {disease_label} at {location}")
        
        db = get_database()
        
        # Convert radius to radians for MongoDB geospatial query
        radius_radians = radius_km / 6371.0  # Earth radius in km
        
        # Find nearby farmers
        nearby_farmers = await db.users.find({
            "role": "farmer",
            "location": {
                "$near": {
                    "$geometry": location,
                    "$maxDistance": radius_km * 1000  # Convert to meters
                }
            }
        }).to_list(length=None)
        
        alert_message = (
            f"⚠️ Outbreak Alert: {disease_label} detected in your area. "
            f"{affected_count} cases reported within {radius_km}km. "
            f"Please monitor your crops/animals and consult a veterinarian if you notice symptoms."
        )
        
        # Send alerts to all nearby farmers
        for farmer in nearby_farmers:
            await self.send_notification(
                user_id=str(farmer['_id']),
                title=f"Outbreak Alert: {disease_label}",
                message=alert_message,
                channels=["in_app", "sms"],  # Can add "email" if needed
                data={
                    "alert_type": "outbreak",
                    "disease": disease_label,
                    "affected_count": affected_count,
                    "radius_km": radius_km
                }
            )
        
        logger.info(f"Outbreak alerts sent to {len(nearby_farmers)} farmers")


# Singleton instance
notification_service = NotificationService()
