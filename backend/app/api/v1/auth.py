from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
import logging

from app.models.user import UserCreate, UserLogin, Token, UserResponse, UserRole
from app.core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token,
    get_current_user
)
from app.core.database import get_database

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate):
    """
    Register a new user
    
    Roles: farmer, vet, admin
    """
    db = get_database()
    
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user_dict = user_data.dict(exclude={"password"})
    user_dict["hashed_password"] = get_password_hash(user_data.password)
    user_dict["created_at"] = datetime.utcnow()
    user_dict["is_active"] = True
    
    result = await db.users.insert_one(user_dict)
    user_dict["id"] = str(result.inserted_id)
    user_dict["_id"] = result.inserted_id
    
    # Create access token
    access_token = create_access_token({
        "sub": user_dict["id"],
        "email": user_dict["email"],
        "role": user_dict["role"]
    })
    
    logger.info(f"New user registered: {user_data.email} ({user_data.role})")
    
    return Token(
        access_token=access_token,
        user=UserResponse(
            id=user_dict["id"],
            email=user_dict["email"],
            full_name=user_dict["full_name"],
            role=user_dict["role"],
            phone=user_dict.get("phone"),
            location=user_dict.get("location"),
            created_at=user_dict["created_at"],
            is_active=user_dict["is_active"]
        )
    )


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """
    Login with email and password
    
    Returns JWT access token
    """
    db = get_database()
    
    # Find user by email
    user = await db.users.find_one({"email": credentials.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if user is active
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    
    # Create access token
    access_token = create_access_token({
        "sub": str(user["_id"]),
        "email": user["email"],
        "role": user["role"]
    })
    
    logger.info(f"User logged in: {credentials.email}")
    
    return Token(
        access_token=access_token,
        user=UserResponse(
            id=str(user["_id"]),
            email=user["email"],
            full_name=user["full_name"],
            role=user["role"],
            phone=user.get("phone"),
            location=user.get("location"),
            created_at=user["created_at"],
            is_active=user.get("is_active", True)
        )
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current user information
    
    Requires authentication
    """
    from bson import ObjectId
    db = get_database()
    
    user = await db.users.find_one({"_id": ObjectId(current_user["id"])})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=str(user["_id"]),
        email=user["email"],
        full_name=user["full_name"],
        role=user["role"],
        phone=user.get("phone"),
        location=user.get("location"),
        created_at=user["created_at"],
        is_active=user.get("is_active", True)
    )


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout (client should discard token)
    """
    logger.info(f"User logged out: {current_user['email']}")
    return {"message": "Successfully logged out"}
