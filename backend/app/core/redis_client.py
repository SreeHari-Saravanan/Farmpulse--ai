import redis.asyncio as redis
from typing import Optional
import logging
import json

from app.core.config import settings

logger = logging.getLogger(__name__)

# Global Redis client
redis_client: Optional[redis.Redis] = None


async def connect_to_redis():
    """Connect to Redis"""
    global redis_client
    
    try:
        logger.info(f"Connecting to Redis at {settings.REDIS_URL}")
        redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        
        # Test connection
        await redis_client.ping()
        logger.info("Successfully connected to Redis")
        
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        # Don't raise - Redis is optional for basic functionality
        redis_client = None


async def close_redis_connection():
    """Close Redis connection"""
    global redis_client
    
    if redis_client:
        logger.info("Closing Redis connection")
        await redis_client.close()


def get_redis() -> Optional[redis.Redis]:
    """Get Redis client instance"""
    return redis_client


async def cache_set(key: str, value: dict, expire: int = 3600):
    """Set a cache value with expiration (in seconds)"""
    if redis_client:
        try:
            await redis_client.setex(key, expire, json.dumps(value))
        except Exception as e:
            logger.error(f"Redis cache set error: {e}")


async def cache_get(key: str) -> Optional[dict]:
    """Get a cache value"""
    if redis_client:
        try:
            value = await redis_client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"Redis cache get error: {e}")
    return None


async def cache_delete(key: str):
    """Delete a cache value"""
    if redis_client:
        try:
            await redis_client.delete(key)
        except Exception as e:
            logger.error(f"Redis cache delete error: {e}")


async def publish_message(channel: str, message: dict):
    """Publish a message to a Redis channel"""
    if redis_client:
        try:
            await redis_client.publish(channel, json.dumps(message))
        except Exception as e:
            logger.error(f"Redis publish error: {e}")
