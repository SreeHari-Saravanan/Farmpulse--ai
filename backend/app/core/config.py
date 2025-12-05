from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "farmpulse"
    
    # JWT
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    UPLOAD_DIR: str = "./uploads"
    
    # API
    API_V1_PREFIX: str = "/api"
    
    # External APIs (Optional)
    GOOGLE_TRANSLATE_API_KEY: str = ""
    GOOGLE_SPEECH_API_KEY: str = ""
    GOOGLE_APPLICATION_CREDENTIALS: str = ""
    AGORA_APP_ID: str = ""
    AGORA_APP_CERTIFICATE: str = ""
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_API_KEY: str = ""
    TWILIO_API_SECRET: str = ""
    SMS_API_KEY: str = ""
    SMS_PROVIDER: str = "twilio"
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@farmpulse.ai"
    
    # Outbreak Detection
    OUTBREAK_THRESHOLD: int = 5
    OUTBREAK_RADIUS_KM: float = 50.0
    OUTBREAK_TIME_WINDOW_HOURS: int = 168  # 7 days
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Environment
    ENVIRONMENT: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
