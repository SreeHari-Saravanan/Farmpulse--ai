from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration"""
    FARMER = "farmer"
    VET = "vet"
    ADMIN = "admin"


class UserBase(BaseModel):
    """Base user model"""
    email: EmailStr
    full_name: str
    role: UserRole
    phone: Optional[str] = None
    location: Optional[dict] = None  # {"type": "Point", "coordinates": [lng, lat]}


class UserCreate(UserBase):
    """User creation model"""
    password: str


class UserLogin(BaseModel):
    """User login model"""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """User response model"""
    id: str
    created_at: datetime
    is_active: bool = True
    
    class Config:
        from_attributes = True


class UserInDB(UserBase):
    """User database model"""
    id: str
    hashed_password: str
    created_at: datetime
    is_active: bool = True


class Token(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenPayload(BaseModel):
    """Token payload model"""
    sub: str
    email: str
    role: str
    exp: Optional[datetime] = None
