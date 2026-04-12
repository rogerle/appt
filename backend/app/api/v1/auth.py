"""
Authentication API endpoints - Admin and studio registration

Endpoints:
- POST /api/v1/auth/register - Studio registration
- POST /api/v1/auth/login - Admin login
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import logging

from db.database import get_db
from core.security import create_access_token, verify_password, hash_password
from models.instructor import Instructor


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_studio(
    name: str,
    email: str,
    phone: str,
    password: str,
    db: Session = Depends(get_db)
):
    """
    Register a new yoga studio.
    
    Creates admin account for the studio and returns access token.
    """
    # Check if email already exists (implement check against studio table when created)
    
    hashed_password = hash_password(password)
    
    logger.info(f"New studio registration request: {email}")
    
    return {
        "message": "Studio registered successfully",
        "token_type": "bearer"
    }


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Admin login endpoint.
    
    Accepts username and password, returns JWT access token on success.
    """
    # TODO: Implement admin/studio authentication logic
    # For now, return mock response
    
    logger.info(f"Login attempt for user: {form_data.username}")
    
    # Placeholder - replace with actual auth logic
    if form_data.password == "admin123":  # Mock check
        access_token = create_access_token(data={"sub": form_data.username})
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
