"""
Authentication API Endpoints - Login, Register, Token Management

Provides JWT-based authentication for studio owners.
Includes password hashing and token validation.
"""

from datetime import datetime, timedelta
from typing import Annotated

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.schemas.auth import (
    LoginRequest, 
    RegisterRequest, 
    TokenResponse,
    UserResponse
)

# JWT configuration
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against bcrypt hash."""
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def get_password_hash(password: str) -> str:
    """Generate bcrypt hash for password."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


@router.post("/login", response_model=TokenResponse, summary="User login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    """Authenticate user and return JWT token."""
    
    # For now, use hardcoded admin credentials (will be replaced with DB lookup)
    username = settings.ADMIN_USERNAME
    stored_hash = getattr(settings, '_password_hash', None)
    
    if not stored_hash:
        stored_hash = get_password_hash(settings.ADMIN_PASSWORD)
        settings._password_hash = stored_hash
    
    if form_data.username != username or not verify_password(form_data.password, stored_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create JWT token (simplified - use python-jose in production)
    from app.core.security import create_access_token
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"username": username, "user_id": 1},
        expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, 
             summary="Register new studio owner")
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """Register a new yoga studio and owner account."""
    
    # TODO: Implement actual registration with database storage
    # For now, return mock response
    
    hashed_password = get_password_hash(request.password)
    
    return UserResponse(
        id=1,  # Mock ID
        username=request.phone,
        studio_name=request.studio_name,
        phone=request.phone
    )


@router.get("/me", response_model=UserResponse, summary="Get current user info")
async def get_current_user_info(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Retrieve information about the currently authenticated user."""
    
    # TODO: Validate JWT token and return user data from database
    return UserResponse(
        id=1,
        username=settings.ADMIN_USERNAME,
        studio_name="阳光瑜伽馆",  # Mock data
        phone="13800138000"
    )
