"""
Instructor API endpoints - User-facing instructor listing

Endpoints:
- GET /api/v1/instructors - List all active instructors
- GET /api/v1/instructors?date=YYYY-MM-DD - Filter by date
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from db.database import get_db
from models.instructor import Instructor
from schemas.instructor import InstructorResponse


router = APIRouter(prefix="/instructors", tags=["instructors"])


@router.get("", response_model=List[InstructorResponse])
def list_instructors(
    date: Optional[str] = Query(None, description="Filter instructors by date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Get list of active instructors.
    
    Optionally filter by specific date to show only instructors scheduled for that day.
    """
    query = db.query(Instructor).filter(Instructor.is_active == True)
    
    if date:
        # Use joinedload for eager loading to avoid N+1 queries
        from models.schedule import Schedule
        query = query.options(joinedload(Instructor.schedules)).join(
            Schedule, Instructor.id == Schedule.instructor_id
        ).filter(
            Schedule.date == date
        )
    
    instructors = query.distinct().all()
    return instructors
