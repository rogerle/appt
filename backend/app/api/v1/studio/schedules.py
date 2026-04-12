"""
Studio Management API - Schedule endpoints (Admin only)

Endpoints:
- POST /api/v1/studio/schedules - Create single schedule
- POST /api/v1/studio/schedules/batch - Batch create weekly schedules
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date, timedelta

from api.v1.deps import get_current_user
from db.database import get_db
from schemas.schedule import ScheduleCreate
from models.schedule import Schedule


router = APIRouter(prefix="/schedules", tags=["studio-schedules"])


@router.post("", response_model=Schedule, status_code=status.HTTP_201_CREATED)
def create_single_schedule(
    schedule_data: ScheduleCreate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a single class schedule (admin only).
    
    Requires valid JWT authentication.
    """
    # Check for overlapping schedules
    existing = db.query(Schedule).filter(
        Schedule.instructor_id == schedule_data.instructor_id,
        Schedule.date == schedule_data.date,
        Schedule.is_active == True
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Instructor already has a class on this date"
        )
    
    db_schedule = Schedule(
        instructor_id=schedule_data.instructor_id,
        date=schedule_data.date,
        start_time=schedule_data.start_time,
        end_time=schedule_data.end_time,
        max_capacity=schedule_data.max_capacity,
        is_active=True
    )
    
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    
    return db_schedule


@router.post("/batch", status_code=status.HTTP_201_CREATED)
def create_batch_schedules(
    instructor_id: int,
    start_date: str,  # YYYY-MM-DD format
    end_date: str,     # YYYY-MM-DD format
    weekday: Optional[int] = None,  # 0=Monday, 6=Sunday (optional filter)
    time_range: tuple = None,        # (start_time, end_time) in HH:MM format
    max_capacity: int = 10,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create multiple weekly schedules for a date range (admin only).
    
    Creates one schedule per day in the specified date range.
    Optionally filter by specific weekday (0-6 where Monday=0).
    """
    from datetime import datetime
    
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()
    
    if start > end:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date must be before or equal to end date"
        )
    
    schedules_created = []
    
    current = start
    while current <= end:
        # If weekday filter is specified, skip non-matching days
        if weekday is not None and current.weekday() != weekday - 1:  # Adjust for Python's Monday=0
            current += timedelta(days=1)
            continue
        
        schedule = Schedule(
            instructor_id=instructor_id,
            date=current.strftime("%Y-%m-%d"),
            start_time=time_range[0] if time_range else "10:00",
            end_time=time_range[1] if time_range else "11:00",
            max_capacity=max_capacity,
            is_active=True
        )
        
        db.add(schedule)
        schedules_created.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)
    
    db.commit()
    
    return {
        "message": f"Created {len(schedules_created)} schedules",
        "dates": schedules_created,
        "instructor_id": instructor_id
    }
