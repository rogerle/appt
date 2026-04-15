"""
Security Utilities - JWT Token Creation and Validation

Provides functions for creating and verifying JWT access tokens.
Uses python-jose library for industry-standard token handling.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
import bcrypt
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

from app.core.config import settings
from app.db.database import get_db
from app.db.models.user import User




def create_access_token(data: dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token.
    
    Args:
        data: Payload data to encode in token (should include sub/username)
        expires_delta: Token expiration time (defaults to ACCESS_TOKEN_EXPIRE_MINUTES)
        
    Returns:
        str: Signed JWT token
        
    Example:
        >>> token = create_access_token(data={"sub": "user123"})
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    
    return jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )


def verify_token(token: str) -> Optional[dict[str, Any]]:
    """
    Verify and decode JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload if valid, None if invalid/expired
        
    Raises:
        JWTError: If token is invalid
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()  # Return as string for DB storage


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against bcrypt hash.
    
    Uses native bcrypt library (not passlib) to avoid compatibility issues
    with newer bcrypt versions that removed __about__ attribute.
    """
    try:
        # Native bcrypt checkpw
        return bcrypt.checkpw(
            plain_password.encode(),
            hashed_password.encode()
        )
    except Exception as e:
        logger.error(f"bcrypt verification failed: {e}")
        return False


# OAuth2 scheme for JWT token extraction
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    scheme_name="JWT",
    description="Provide JWT bearer token for authentication"
)


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Dependency to extract and validate JWT token, return User object.
    
    1. Verify JWT token using verify_token()
    2. Extract email from payload (sub field)
    3. Query DB for user by email
    4. Return user or raise HTTPException(401)
    
    Usage in endpoints:
        async def some_protected_endpoint(current_user: User = Depends(get_current_user)):
            # current_user is guaranteed to be authenticated here
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效或未授权的令牌",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
    
    # Token 'sub' should contain the email
    email: Optional[str] = payload.get("sub")
    if email is None:
        raise credentials_exception
    
    # Query database for user
    user = db.query(User).filter(User.email == email).first()
    if user is None or not user.is_active:
        raise credentials_exception
    
    return user


def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency that ensures user has admin role.
    
    Usage in endpoints:
        @router.delete("/{id}")  # Admin-only operation
        async def delete_item(admin_user: User = Depends(get_current_admin_user)):
            # Only admins can reach this code
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限才能执行此操作"
        )
    return current_user
