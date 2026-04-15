"""Admin Instructors API - CRUD operations for instructor management."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_admin_user
from app.db.database import get_db
from app.db.models.user import User
from app.db.models.instructor import Instructor
from app.schemas.admin import InstructorCreate, InstructorUpdate, InstructorResponse


router = APIRouter(prefix="/instructors", tags=["Admin - Instructors"])


@router.get("", response_model=list[InstructorResponse])
async def list_instructors(
    search: str | None = None, 
    active_only: bool = False,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_admin_user)
):
    """List all instructors with optional filters."""
    
    query = db.query(Instructor)
    
    if search:
        query = query.filter(Instructor.name.ilike(f"%{search}%"))
    
    if active_only:
        query = query.filter(Instructor.is_active == True)
    
    return query.order_by(Instructor.created_at.desc()).all()


@router.post("", response_model=InstructorResponse, status_code=status.HTTP_201_CREATED)
async def create_instructor(
    instructor_data: InstructorCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_admin_user)
):
    """Create a new instructor."""
    
    # Create instructor record (using actual model fields)
    db_instructor = Instructor(
        name=instructor_data.name,
        studio_id=instructor_data.studio_id,
        avatar_url=instructor_data.avatar_url,
        description=instructor_data.description,
        is_active=True
    )

    db.add(db_instructor)
    db.commit()
    db.refresh(db_instructor)

    return db_instructor


@router.get("/{instructor_id}", response_model=InstructorResponse)
async def get_instructor(instructor_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_admin_user)):
    """Get a specific instructor by ID."""
    
    instructor = db.query(Instructor).filter(Instructor.id == instructor_id).first()
    
    if not instructor:
        raise HTTPException(status_code=404, detail="Instructor not found")

    return instructor


@router.put("/{instructor_id}", response_model=InstructorResponse)
async def update_instructor(
    instructor_id: int, 
    instructor_data: InstructorUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_admin_user)
):
    """Update an instructor (partial update)."""
    
    instructor = db.query(Instructor).filter(Instructor.id == instructor_id).first()
    
    if not instructor:
        raise HTTPException(status_code=404, detail="Instructor not found")

    # Update only provided fields
    update_data = instructor_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(instructor, field, value)

    db.commit()
    db.refresh(instructor)

    return instructor


@router.delete("/{instructor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_instructor(
    instructor_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_admin_user)
):
    """Soft delete an instructor (mark as inactive)."""
    
    from app.db.models.schedule import Schedule
    
    instructor = db.query(Instructor).filter(Instructor.id == instructor_id).first()
    
    if not instructor:
        raise HTTPException(status_code=404, detail="Instructor not found")

    # Check if has active schedules
    active_schedules = db.query(Schedule).filter(
        Schedule.instructor_id == instructor_id,
        Schedule.is_recurring == False  # Only check non-recurring for now
    ).count()
    
    if active_schedules > 0:
        raise HTTPException(
            status_code=409, 
            detail=f"Cannot delete instructor with {active_schedules} active schedules. Please remove or reassign schedules first."
        )

    # Soft delete by marking inactive
    instructor.is_active = False
    
    db.commit()


@router.patch("/{instructor_id}/toggle-status", response_model=InstructorResponse)
async def toggle_instructor_status(
    instructor_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_admin_user)
):
    """Toggle instructor active/inactive status."""
    
    instructor = db.query(Instructor).filter(Instructor.id == instructor_id).first()
    
    if not instructor:
        raise HTTPException(status_code=404, detail="Instructor not found")

    instructor.is_active = not instructor.is_active
    
    db.commit()
    db.refresh(instructor)

    return instructor
