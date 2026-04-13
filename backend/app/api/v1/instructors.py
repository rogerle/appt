"""
Instructor API Endpoints - CRUD Operations and Available Time Slots

Provides instructor management for studio owners.
Includes available time slot calculation for public viewing.
"""

from datetime import date, datetime, time, timedelta
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.schemas.instructor import (
    InstructorCreate,
    InstructorUpdate, 
    InstructorResponse,
    InstructorWithSlotsResponse,
    TimeSlot
)


router = APIRouter(
    prefix="/instructors",
    tags=["Instructors"],
)


@router.post("/", response_model=InstructorResponse, status_code=status.HTTP_201_CREATED,
             summary="Create new instructor")
async def create_instructor(
    instructor_data: InstructorCreate,
    db: Session = Depends(get_db),
    admin_token: str = Depends(lambda token: settings.ADMIN_USERNAME)  # TODO: JWT validation
):
    """Add a new yoga instructor to the studio."""
    
    from app.db.models.instructor import Instructor
    
    # Create and save new instructor
    db_instructor = Instructor(
        name=instructor_data.name,
        description=instructor_data.description,
        is_active=True
    )
    
    db.add(db_instructor)
    db.commit()
    db.refresh(db_instructor)
    
    return InstructorResponse(
        id=db_instructor.id,
        name=db_instructor.name,
        description=db_instructor.description,
        avatar_url=None,  # TODO: Handle image upload
        is_active=db_instructor.is_active,
        created_at=datetime.utcnow()
    )


@router.get("/", response_model=List[InstructorWithSlotsResponse], 
            summary="Get all instructors")
async def list_instructors(
    db: Session = Depends(get_db),
    date_param: Optional[date] = Query(None, alias="date", description="Filter by date"),
    is_active_only: bool = Query(False, description="Only show active instructors")
):
    """Get all yoga instructors with their available time slots."""
    
    from app.db.models.instructor import Instructor
    
    query = db.query(Instructor)
    
    if is_active_only:
        query = query.filter(Instructor.is_active == True)
    
    instructors = query.all()
    
    # Calculate available slots for each instructor (simplified logic)
    response_data = []
    target_date = date_param or datetime.utcnow().date()
    
    for instructor in instructors:
        # TODO: Implement proper slot calculation from schedules table
        available_slots = [
            TimeSlot(start_time=time(10, 0), end_time=time(11, 0), available_spots=5),
            TimeSlot(start_time=time(15, 0), end_time=time(16, 0), available_spots=3)
        ]
        
        response_data.append(InstructorWithSlotsResponse(
            id=instructor.id,
            name=instructor.name,
            description=instructor.description,
            avatar_url=None,
            is_active=instructor.is_active,
            created_at=datetime.utcnow(),
            available_slots=available_slots if date_param else []
        ))
    
    return response_data


@router.get("/{instructor_id}", response_model=InstructorResponse, 
            summary="Get instructor by ID")
async def get_instructor(
    instructor_id: int,
    db: Session = Depends(get_db)
):
    """Retrieve specific instructor information."""
    
    from app.db.models.instructor import Instructor
    
    instructor = db.query(Instructor).filter(Instructor.id == instructor_id).first()
    
    if not instructor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instructor not found"
        )
    
    return InstructorResponse(
        id=instructor.id,
        name=instructor.name,
        description=instructor.description,
        avatar_url=None,
        is_active=instructor.is_active,
        created_at=datetime.utcnow()  # TODO: Use actual timestamp
    )


@router.put("/{instructor_id}", response_model=InstructorResponse, 
            summary="Update instructor information")
async def update_instructor(
    instructor_id: int,
    update_data: InstructorUpdate,
    db: Session = Depends(get_db),
    admin_token: str = Depends(lambda token: settings.ADMIN_USERNAME)  # TODO: JWT validation
):
    """Update existing instructor information."""
    
    from app.db.models.instructor import Instructor
    
    instructor = db.query(Instructor).filter(Instructor.id == instructor_id).first()
    
    if not instructor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instructor not found"
        )
    
    # Update fields (only provided ones)
    update_dict = update_data.model_dump(exclude_unset=True)
    
    for field, value in update_dict.items():
        setattr(instructor, field, value)
    
    db.commit()
    db.refresh(instructor)
    
    return InstructorResponse(
        id=instructor.id,
        name=instructor.name,
        description=instructor.description,
        avatar_url=None,
        is_active=instructor.is_active,
        created_at=datetime.utcnow()
    )


@router.delete("/{instructor_id}", status_code=status.HTTP_204_NO_CONTENT, 
               summary="Delete instructor")
async def delete_instructor(
    instructor_id: int,
    db: Session = Depends(get_db),
    admin_token: str = Depends(lambda token: settings.ADMIN_USERNAME)  # TODO: JWT validation
):
    """Soft-delete an instructor (set is_active=False)."""
    
    from app.db.models.instructor import Instructor
    
    instructor = db.query(Instructor).filter(Instructor.id == instructor_id).first()
    
    if not instructor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instructor not found"
        )
    
    # Soft delete (don't actually remove from database)
    instructor.is_active = False
    db.commit()
    
    return None  # No content response
