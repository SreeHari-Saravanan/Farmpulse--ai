from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Global database client
mongo_client: Optional[AsyncIOMotorClient] = None
database: Optional[AsyncIOMotorDatabase] = None


async def connect_to_mongo():
    """Connect to MongoDB"""
    global mongo_client, database
    
    try:
        logger.info(f"Connecting to MongoDB at {settings.MONGODB_URL}")
        mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
        database = mongo_client[settings.DATABASE_NAME]
        
        # Test connection
        await database.command("ping")
        logger.info("Successfully connected to MongoDB")
        
        # Create indexes
        await create_indexes()
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def close_mongo_connection():
    """Close MongoDB connection"""
    global mongo_client
    
    if mongo_client:
        logger.info("Closing MongoDB connection")
        mongo_client.close()


async def create_indexes():
    """Create database indexes for optimized queries"""
    try:
        # Users collection indexes
        await database.users.create_index("email", unique=True)
        await database.users.create_index("role")
        
        # Reports collection indexes
        await database.reports.create_index("farmer_id")
        await database.reports.create_index("vet_id")
        await database.reports.create_index("status")
        await database.reports.create_index("created_at")
        await database.reports.create_index("disease_label")
        await database.reports.create_index([("location", "2dsphere")])  # Geospatial index
        await database.reports.create_index([("created_at", -1), ("status", 1)])  # Compound index
        
        # Feedback collection indexes
        await database.feedback.create_index("report_id")
        await database.feedback.create_index("created_at")
        
        # Sessions collection indexes
        await database.sessions.create_index("report_id")
        await database.sessions.create_index("farmer_id")
        await database.sessions.create_index("vet_id")
        await database.sessions.create_index("created_at")
        
        # Alerts collection indexes
        await database.alerts.create_index("user_id")
        await database.alerts.create_index("created_at")
        await database.alerts.create_index("is_read")
        await database.alerts.create_index([("location", "2dsphere")])
        
        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")


def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    if database is None:
        raise RuntimeError("Database not initialized")
    return database
