"""
Schedule API Endpoints - Class Slot Management and Batch Operations

Provides schedule creation, listing, and batch weekly scheduling.
Includes time conflict detection for instructors.
"""

from datetime import date, datetime, time
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.schemas.schedule import (
    ScheduleCreate,
    ScheduleResponse,
    ScheduleBatchCreateRequest,
    ScheduleSlotResponse
)


router = APIRouter(
    prefix="/schedules",
    tags=["Schedules"],
)


def check_time_conflict(db: Session, instructor_id: int, 
                        schedule_date: date, start_time: time, end_time: time) -> bool:
    """Check if there's a scheduling conflict for the instructor."""
    
    from app.db.models.schedule import Schedule
    
    # Query existing schedules that overlap with new time slot
    conflicting = db.query(Schedule).filter(
        Schedule.instructor_id == instructor_id,
        Schedule.schedule_date == schedule_date,
        (Schedule.start_time < end_time) & (Schedule.end_time > start_time),
        ~Schedule.is_recurring  # Don't count recurring schedules as conflicts for now
    ).first()
    
    return conflicting is not None


@router.post("/", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED,
             summary="Create single class schedule")
async def create_schedule(
    schedule_data: ScheduleCreate,
    db: Session = Depends(get_db),
    admin_token: str = Depends(lambda token: settings.ADMIN_USERNAME)  # TODO: JWT validation
):
    """Create a new yoga class time slot."""
    
    from app.db.models.schedule import Schedule
    
    # Check for scheduling conflicts
    if check_time_conflict(
        db, 
        schedule_data.instructor_id,
        schedule_data.schedule_date,
        schedule_data.start_time,
        schedule_data.end_time
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Time slot conflicts with existing class for this instructor"
        )
    
    # Create and save new schedule
    db_schedule = Schedule(
        instructor_id=schedule_data.instructor_id,
        schedule_date=schedule_data.schedule_date,
        start_time=schedule_data.start_time,
        end_time=schedule_data.end_time,
        max_bookings=schedule_data.max_bookings or 1,
        is_recurring=False
    )
    
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    
    return ScheduleResponse(
        id=db_schedule.id,
        instructor_id=db_schedule.instructor_id,
        start_time=db_schedule.start_time,
        end_time=db_schedule.end_time,
        max_bookings=db_schedule.max_bookings,
        available_spots=db_schedule.max_bookings  # Initially all spots are available
    )


@router.post("/batch", response_model=List[ScheduleResponse], 
             summary="Batch create weekly schedules")
async def batch_create_schedules(
    request: ScheduleBatchCreateRequest,
    db: Session = Depends(get_db),
    admin_token: str = Depends(lambda token: settings.ADMIN_USERNAME)  # TODO: JWT validation
):
    """Create multiple schedule slots in one operation (weekly recurring)."""
    
    from app.db.models.schedule import Schedule
    
    created_schedules = []
    weekdays_map = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 
                   4: "Thursday", 5: "Friday", 6: "Saturday", 7: "Sunday"}
    
    # Generate all dates in the range that match requested weekdays
    current_date = request.start_date
    
    while current_date <= request.end_date:
        if current_date.weekday() + 1 in request.weekdays:
            # Check for conflicts before creating
            if not check_time_conflict(
                db,
                request.instructor_id,
                current_date,
                request.start_time,
                request.end_time
            ):
                schedule = Schedule(
                    instructor_id=request.instructor_id,
                    schedule_date=current_date,
                    start_time=request.start_time,
                    end_time=request.end_time,
                    max_bookings=1,  # Default to individual session
                    is_recurring=False  # Store as individual days for flexibility
                )
                
                db.add(schedule)
                created_schedules.append(schedule)
        
        current_date += __import__('datetime').timedelta(days=1)
    
    db.commit()
    
    # Return all created schedules with available spots info
    response = []
    for schedule in created_schedules:
        db.refresh(schedule)
        response.append(ScheduleResponse(
            id=schedule.id,
            instructor_id=schedule.instructor_id,
            start_time=schedule.start_time,
            end_time=schedule.end_time,
            max_bookings=schedule.max_bookings,
            available_spots=schedule.max_bookings
        ))
    
    return response


@router.get("/", response_model=List[ScheduleSlotResponse], 
             summary="Get available time slots")
async def list_available_slots(
    db: Session = Depends(get_db),
    date_param: date = Query(..., description="Query date (YYYY-MM-DD)"),
    instructor_id: Optional[int] = Query(None, description="Filter by instructor ID")
):
    """Get all available time slots for a specific date."""
    
    from app.db.models.schedule import Schedule
    
    query = db.query(Schedule).filter(
        Schedule.schedule_date == date_param,
        ~Schedule.is_recurring
    )
    
    if instructor_id:
        query = query.filter(Schedule.instructor_id == instructor_id)
    
    schedules = query.all()
    
    # Calculate available spots (excluding confirmed bookings)
    from app.db.models.booking import Booking
    
    response = []
    for schedule in schedules:
        booked_count = db.query(Booking).filter(
            Booking.schedule_id == schedule.id,
            Booking.status == 'confirmed'
        ).count()
        
        available_spots = max(0, schedule.max_bookings - booked_count)
        
        response.append(ScheduleSlotResponse(
            id=schedule.id,
            start_time=schedule.start_time,
            end_time=schedule.end_time,
            available_spots=available_spots
        ))
    
    return response
