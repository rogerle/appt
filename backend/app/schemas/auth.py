"""
Authentication Schemas - Login/Register/Token Validation

Provides Pydantic models for authentication endpoints.
Supports JWT token creation and validation.
"""

from datetime import datetime, timedelta
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class LoginRequest(BaseModel):
    """Request model for user login."""
    
    username: str = Field(..., min_length=3, max_length=50, description="Username or email")
    password: str = Field(..., min_length=6, max_length=128, description="User password")


class RegisterRequest(BaseModel):
    """Request model for new user registration (studio owner)."""
    
    studio_name: str = Field(..., min_length=3, max_length=100, description="Yoga studio name")
    phone: str = Field(..., pattern=r'^\d{11}$', description="Contact phone number (11 digits)")
    password: str = Field(..., min_length=8, max_length=128, description="Password (min 8 characters)")
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v):
        """Validate password meets security requirements."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


class TokenResponse(BaseModel):
    """Response model for successful authentication."""
    
    access_token: str = Field(..., description="JWT bearer token")
    token_type: str = Field("bearer", description="Token type (always 'bearer')")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class TokenData(BaseModel):
    """Internal model for JWT payload data."""
    
    username: Optional[str] = None
    user_id: Optional[int] = None
    exp: datetime  # Expiration timestamp (set during token creation)


class UserResponse(BaseModel):
    """Response model for authenticated user information."""
    
    id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    studio_name: Optional[str] = Field(None, description="Associated studio name (if owner)")
    phone: Optional[str] = Field(None, description="Contact phone number")


class PasswordUpdateRequest(BaseModel):
    """Request model for password change."""
    
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password (min 8 characters)")
