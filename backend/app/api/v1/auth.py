"""Authentication Endpoints - User Registration & Login"""

from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token, 
    hash_password, 
    verify_password, 
    get_current_user as get_current_user_from_token
)
from app.db.database import get_db
from app.db.models.user import User
from app.schemas.user import TokenResponse, UserCreate, UserLogin, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    注册用户并返回 JWT token
    
    - **email**: 用户邮箱（唯一标识）
    - **username**: 用户名（3-100 字符，唯一）
    - **password**: 密码（至少 8 个字符，bcrypt 加密存储）
    
    Returns:
        - access_token: JWT token for API authentication
        - token_type: Always "bearer"
        
    Raises:
        - HTTP 400: Email already registered
        - HTTP 422: Validation errors (invalid email, weak password)
    """
    # Check if email already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | 
        (User.username == user_data.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱或用户名已被注册"
        )
    
    # Create new user with hashed password and default role='user'
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
        role="user",  # Default to regular user (not admin)
        is_active=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Generate JWT token with user role in payload
    access_token = create_access_token(
        data={"sub": db_user.email, "role": db_user.role},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return TokenResponse(access_token=access_token, token_type="bearer")


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    用户登录并返回 JWT token
    
    - **email**: 注册时使用的邮箱地址
    - **password**: 密码（bcrypt 验证）
    
    Returns:
        - access_token: JWT token for API authentication  
        - token_type: Always "bearer"
        
    Raises:
        - HTTP 401: Invalid email or password
        
    Example Request:
        ```bash
        curl -X POST http://localhost:8000/api/v1/auth/login \\
          -H "Content-Type: application/json" \\
          -d '{"email": "admin@appt.local", "password": "your_password"}'
        ```
    """
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if account is active  
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被禁用，请联系管理员"
        )
    
    # Generate JWT token with user role in payload
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return TokenResponse(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user_from_token)):
    """
    获取当前登录用户信息
    
    Requires valid JWT token in Authorization header:
        Authorization: Bearer <your_access_token>
        
    Returns:
        - id: User ID
        - email: Email address
        - username: Username  
        - role: user/admin
        - is_active: Account status
        
    Raises:
        - HTTP 401: Invalid or missing token
    """
    # current_user is injected by get_current_user_from_token dependency
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        role=current_user.role,
        is_active=current_user.is_active
    )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user_from_token)):
    """
    用户登出（前端清除 token）
    
    Note: JWT tokens are stateless. This endpoint exists for audit/logging purposes only.
    The frontend should remove the access_token from localStorage/cookies after calling this.
    
    Returns:
        {"detail": "Successfully logged out"}
        
    Frontend Implementation:
        ```javascript
        // Call logout API (optional, for server-side logging)
        await apiClient.post('/auth/logout')
        
        // CRITICAL: Clear token from storage  
        localStorage.removeItem('access_token')
        
        // Redirect to login page or homepage
        window.location.href = '/'
        ```
    """
    # Token is stateless, but we can add server-side logout logic here if needed
    # e.g., token blacklist, session invalidation
    
    return {"detail": "已成功登出"}
