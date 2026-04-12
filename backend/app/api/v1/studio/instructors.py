"""
Studio Management API - Instructor endpoints (Admin only)

Endpoints:
- POST /api/v1/studio/instructors - Create new instructor
- PUT /api/v1/studio/instructors/{id} - Update instructor info
- DELETE /api/v1/studio/instructors/{id} - Disable instructor
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.v1.deps import get_current_user
from db.database import get_db
from schemas.instructor import InstructorCreate, InstructorUpdate, InstructorResponse
from models.instructor import Instructor


router = APIRouter(prefix="/instructors", tags=["studio-instructors"])


@router.post("", response_model=InstructorResponse, status_code=status.HTTP_201_CREATED)
def create_instructor(
    instructor_data: InstructorCreate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new instructor (admin only).
    
    Requires valid JWT authentication.
    """
    # Check if instructor with same name exists
    existing = db.query(Instructor).filter(
        Instructor.name == instructor_data.name,
        Instructor.is_active != False  # Allow duplicates of disabled instructors
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Instructor with this name already exists"
        )
    
    db_instructor = Instructor(
        name=instructor_data.name,
        avatar_url=instructor_data.avatar_url,
        bio=instructor_data.bio,
        is_active=True
    )
    
    db.add(db_instructor)
    db.commit()
    db.refresh(db_instructor)
    
    return db_instructor


@router.put("/{instructor_id}", response_model=InstructorResponse)
def update_instructor(
    instructor_id: int,
    instructor_data: InstructorUpdate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing instructor (admin only).
    
    Supports partial updates - only provided fields will be changed.
    """
    db_instructor = db.query(Instructor).filter(
        Instructor.id == instructor_id,
        Instructor.is_active != False  # Don't allow editing disabled instructors directly
    ).first()
    
    if not db_instructor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instructor not found"
        )
    
    update_data = instructor_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_instructor, field, value)
    
    db.commit()
    db.refresh(db_instructor)
    
    return db_instructor


@router.delete("/{instructor_id}")
def disable_instructor(
    instructor_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Disable an instructor (admin only).
    
    Sets is_active to False. Does not delete the record.
    """
    db_instructor = db.query(Instructor).filter(
        Instructor.id == instructor_id,
        Instructor.is_active != False
    ).first()
    
    if not db_instructor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instructor not found or already disabled"
        )
    
    db_instructor.is_active = False
    
    db.commit()
    
    return {
        "message": f"Instructor {instructor_id} has been disabled",
        "id": instructor_id
    }
