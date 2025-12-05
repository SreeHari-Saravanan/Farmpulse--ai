from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
import os

from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection
from app.core.redis_client import connect_to_redis, close_redis_connection
from app.api.v1 import auth, reports, ai, admin, signaling
from app.api.v1.websocket import router as websocket_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting FarmPulse AI application...")
    await connect_to_mongo()
    await connect_to_redis()
    
    # Ensure upload directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    logger.info("Application started successfully")
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    await close_mongo_connection()
    await close_redis_connection()
    logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="FarmPulse AI",
    description="AI-powered crop and animal disease detection and management platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Authentication"])
app.include_router(reports.router, prefix=f"{settings.API_V1_PREFIX}/reports", tags=["Reports"])
app.include_router(ai.router, prefix=f"{settings.API_V1_PREFIX}/ai", tags=["AI Analysis"])
app.include_router(admin.router, prefix=f"{settings.API_V1_PREFIX}/admin", tags=["Admin"])
app.include_router(signaling.router, prefix=f"{settings.API_V1_PREFIX}/signaling", tags=["WebRTC Signaling"])
app.include_router(websocket_router, tags=["WebSocket"])

# Mount static files for uploads
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to FarmPulse AI",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "farmpulse-api",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
