"""Admin Users API - User management for admins."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_admin_user
from app.db.database import get_db
from app.db.models.user import User
from app.schemas.admin import UserResponse, RoleUpdate, StatusUpdate, UserRole


router = APIRouter(prefix="/users", tags=["Admin - Users"])


@router.get("", response_model=list[UserResponse])
async def list_users(
    search: str | None = None,
    role_filter: UserRole | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_admin_user)
):
    """List all users with optional filters."""
    
    query = db.query(User)
    
    if search:
        query = query.filter(
            (User.email.ilike(f"%{search}%")) | 
            (User.username.ilike(f"%{search}%"))
        )
    
    if role_filter:
        query = query.filter(User.role == role_filter)

    return query.order_by(User.created_at.desc()).all()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_admin_user)):
    """Get a specific user."""
    
    target_user = db.query(User).filter(User.id == user_id).first()
    
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    return target_user


@router.patch("/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: int, 
    role_data: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update user role."""
    
    target_user = db.query(User).filter(User.id == user_id).first()
    
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Prevent self-demotion
    if user_id == current_user.id and role_data.role != 'admin':
        raise HTTPException(
            status_code=403, 
            detail="Cannot change your own role. Ask another admin to help."
        )

    target_user.role = role_data.role  # Already string from schema
    
    db.commit()
    db.refresh(target_user)

    return target_user


@router.patch("/{user_id}/status", response_model=UserResponse)
async def update_user_status(
    user_id: int, 
    status_data: StatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update user account status."""
    
    target_user = db.query(User).filter(User.id == user_id).first()
    
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Prevent self-deactivation
    if user_id == current_user.id and not status_data.is_active:
        raise HTTPException(
            status_code=403, 
            detail="Cannot deactivate your own account"
        )

    target_user.is_active = status_data.is_active
    
    db.commit()
    db.refresh(target_user)

    return target_user
