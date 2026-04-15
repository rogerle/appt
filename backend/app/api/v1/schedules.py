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
    ScheduleUpdate,
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


@router.get("/{schedule_id}", response_model=ScheduleResponse,
             summary="Get single schedule by ID")
async def get_schedule(
    schedule_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific schedule.
    Includes booking count and instructor details.
    """
    
    from app.db.models.schedule import Schedule
    from sqlalchemy.orm import joinedload
    from app.db.models.booking import Booking
    
    # Use joinedload for efficient querying
    schedule = db.query(Schedule).options(
        joinedload(Schedule.instructor)
    ).filter(Schedule.id == schedule_id).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="课程不存在"
        )
    
    # Count confirmed bookings
    booking_count = db.query(Booking).filter(
        Booking.schedule_id == schedule.id,
        Booking.status == "confirmed"
    ).count()
    
    available_spots = max(0, schedule.max_bookings - booking_count)
    
    instructor_name = schedule.instructor.name if schedule.instructor else "Unknown"
    
    return ScheduleResponse(
        id=schedule.id,
        instructor_id=schedule.instructor_id,
        instructor_name=instructor_name,
        schedule_date=schedule.schedule_date.isoformat(),
        start_time=schedule.start_time.strftime("%H:%M"),
        end_time=schedule.end_time.strftime("%H:%M"),
        max_bookings=schedule.max_bookings,
        available_spots=available_spots,
        booking_count=booking_count
    )


@router.get("/", response_model=list[ScheduleResponse], 
            summary="Get schedules with advanced filtering (admin)")
async def get_schedules(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Page offset"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    date_from: Optional[date] = Query(None, alias="date_from", description="Start date (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, alias="date_to", description="End date (YYYY-MM-DD)"),
    instructor_id: Optional[int] = Query(None, description="Filter by instructor ID")
):
    """
    Get schedules with advanced filtering for admin management.
    
    Query params:
      - date_from/date_to: Date range filter
      - instructor_id: Filter specific instructor's classes  
      - skip/limit: Pagination (default 20 per page)
    
    Returns paginated list with booking counts and details.
    """
    
    from app.db.models.schedule import Schedule
    from sqlalchemy.orm import joinedload
    
    query = db.query(Schedule).options(
        joinedload(Schedule.instructor)  # Eager load instructor data
    )
    
    # Apply date range filter (if provided)
    if date_from:
        query = query.filter(Schedule.schedule_date >= date_from)
    if date_to:
        query = query.filter(Schedule.schedule_date <= date_to)
    
    # Apply instructor filter (if provided)
    if instructor_id:
        query = query.filter(Schedule.instructor_id == instructor_id)
    
    # Count total for pagination
    total_count = query.count()
    
    # Apply sorting and pagination
    schedules = query.order_by(
        Schedule.schedule_date.desc(),
        Schedule.start_time.asc()
    ).offset(skip).limit(limit).all()
    
    from app.db.models.booking import Booking
    
    # Build response with booking counts
    response_data = []
    for schedule in schedules:
        booking_count = db.query(Booking).filter(
            Booking.schedule_id == schedule.id,
            Booking.status == "confirmed"
        ).count()
        
        available_spots = max(0, schedule.max_bookings - booking_count)
        
        # Get instructor name for display
        instructor_name = schedule.instructor.name if schedule.instructor else "Unknown"
        
        response_data.append(ScheduleResponse(
            id=schedule.id,
            instructor_id=schedule.instructor_id,
            instructor_name=instructor_name,  # Denormalized for admin view
            schedule_date=schedule.schedule_date.isoformat(),
            start_time=schedule.start_time.strftime("%H:%M"),
            end_time=schedule.end_time.strftime("%H:%M"),
            max_bookings=schedule.max_bookings,
            available_spots=available_spots,
            booking_count=booking_count
        ))
    
    return response_data


@router.post("/", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED,
             summary="Create single class schedule (admin only)")
async def create_schedule(
    schedule_data: ScheduleCreate,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_admin_user)  # Will add JWT auth in Phase 5
):
    """
    Create new class schedule with conflict detection.
    
    Validates:
      - Instructor exists and is active
      - End time > start time  
      - Capacity within range (1-50)
      - No overlapping schedules for same instructor on same date
    
    Returns created schedule or 409 Conflict if time overlaps exist.
    """
    
    from app.db.models.schedule import Schedule
    from app.db.models.instructor import Instructor
    
    # Verify instructor exists and is active
    instructor = db.query(Instructor).filter(
        Instructor.id == schedule_data.instructor_id,
        Instructor.is_active == True,
        Instructor.studio_id == 1
    ).first()
    
    if not instructor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="教练不存在或已停用"
        )
    
    # Validate time range
    if schedule_data.end_time <= schedule_data.start_time:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="结束时间必须晚于开始时间"
        )
    
    # Check for overlapping schedules (conflict detection)
    conflicts = db.query(Schedule).filter(
        Schedule.instructor_id == schedule_data.instructor_id,
        Schedule.schedule_date == schedule_data.schedule_date,
        ~Schedule.is_recurring,  # Only check non-recurring schedules
        
        # Overlap condition: new start < existing end AND new end > existing start
        (Schedule.start_time < schedule_data.end_time),
        (Schedule.end_time > schedule_data.start_time)
    ).first()
    
    if conflicts:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"时间冲突：该教练在 {schedule_data.schedule_date.strftime('%Y-%m-%d')} 已有其他课程安排在此时间段"
        )
    
    # Create new schedule
    db_schedule = Schedule(
        instructor_id=schedule_data.instructor_id,
        schedule_date=schedule_data.schedule_date,
        start_time=schedule_data.start_time,
        end_time=schedule_data.end_time,
        max_bookings=schedule_data.max_bookings or 1,  # Default to 1 if not provided
        is_recurring=False
    )
    
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    
    # Build response with instructor name
    return ScheduleResponse(
        id=db_schedule.id,
        instructor_id=instructor.id,
        instructor_name=instructor.name,  # Denormalized for display
        schedule_date=db_schedule.schedule_date.isoformat(),
        start_time=db_schedule.start_time.strftime("%H:%M"),
        end_time=db_schedule.end_time.strftime("%H:%M"),
        max_bookings=db_schedule.max_bookings,
        available_spots=db_schedule.max_bookings,  # Initially all spots are available
        booking_count=0  # New schedule has no bookings yet
    )


@router.patch("/{schedule_id}", response_model=ScheduleResponse,
            summary="Update schedule (partial update, admin only)")
async def update_schedule(
    schedule_id: int,
    updates: ScheduleUpdate,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_admin_user)  # Will add JWT auth in Phase 5
):
    """
    Update schedule with conflict detection for time changes.
    
    Partially updates provided fields and re-checks for overlapping schedules.
    Prevents capacity reduction below existing booking count.
    """
    
    from app.db.models.schedule import Schedule
    from app.db.models.booking import Booking
    
    # Find schedule
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="课程不存在"
        )
    
    # Check for time/date changes - need conflict detection
    has_time_changes = any(
        field in ['schedule_date', 'start_time', 'end_time', 'instructor_id'] 
        for field in updates.model_dump(exclude_unset=True).keys()
    )
    
    if has_time_changes:
        # Build temporary schedule object with proposed changes
        proposed_date = getattr(updates, 'schedule_date', schedule.schedule_date)
        proposed_start = getattr(updates, 'start_time', schedule.start_time)
        proposed_end = getattr(updates, 'end_time', schedule.end_time)
        proposed_instructor = getattr(updates, 'instructor_id', schedule.instructor_id)
        
        # Check for conflicts (excluding current record)
        conflicts = db.query(Schedule).filter(
            Schedule.id != schedule_id,  # Exclude self
            Schedule.instructor_id == proposed_instructor,
            Schedule.schedule_date == proposed_date,
            ~Schedule.is_recurring,
            (Schedule.start_time < proposed_end),
            (Schedule.end_time > proposed_start)
        ).first()
        
        if conflicts:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="时间冲突：修改后的时间段与其他课程重叠"
            )
    
    # Check capacity changes - cannot reduce below existing bookings
    update_dict = updates.model_dump(exclude_unset=True)
    if 'max_bookings' in update_dict:
        new_capacity = update_dict['max_bookings']
        
        # Count confirmed bookings
        booking_count = db.query(Booking).filter(
            Booking.schedule_id == schedule.id,
            Booking.status == "confirmed"
        ).count()
        
        if new_capacity < booking_count:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"无法减少容量：该课程已有 {booking_count} 个预约，容量至少需要设置为 {booking_count}"
            )
    
    # Apply all updates
    for field, value in update_dict.items():
        setattr(schedule, field, value)
    
    # Recalculate available spots after capacity change or new bookings
    booking_count = db.query(Booking).filter(
        Booking.schedule_id == schedule.id,
        Booking.status == "confirmed"
    ).count()
    schedule.available_spots = max(0, schedule.max_bookings - booking_count)
    
    # Get instructor for response
    from sqlalchemy.orm import joinedload
    schedule_with_instructor = db.query(Schedule).options(
        joinedload(Schedule.instructor)
    ).get(schedule_id)
    
    instructor_name = schedule_with_instructor.instructor.name if schedule_with_instructor.instructor else "Unknown"
    
    return ScheduleResponse(
        id=schedule.id,
        instructor_id=schedule.instructor_id,
        instructor_name=instructor_name,
        schedule_date=schedule.schedule_date.isoformat(),
        start_time=schedule.start_time.strftime("%H:%M"),
        end_time=schedule.end_time.strftime("%H:%M"),
        max_bookings=schedule.max_bookings,
        available_spots=schedule.available_spots,
        booking_count=booking_count
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
    date: date = Query(..., alias="date", description="Query date (YYYY-MM-DD)"),
    instructor_id: Optional[int] = Query(None, description="Filter by instructor ID")
):
    """Get all available time slots for a specific date."""
    
    from app.db.models.schedule import Schedule
    
    query = db.query(Schedule).filter(
        Schedule.schedule_date == date,
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


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Soft delete schedule (admin only)")
async def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    force: bool = Query(False, description="Force delete and cancel bookings"),
    # current_user: User = Depends(get_current_admin_user)  # Will add JWT auth in Phase 5
):
    """
    Soft delete schedule (mark as inactive).
    
    If schedule has confirmed bookings:
      - force=false (default): Return 409 error, prevent deletion
      - force=true: Cancel all bookings and mark schedule as deleted
    
    Note: Schedule model doesn't have is_active field.
    We'll use max_bookings=0 to effectively disable it.
    """
    
    from app.db.models.schedule import Schedule
    from app.db.models.booking import Booking
    
    # Find schedule
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="课程不存在"
        )
    
    # Check for existing bookings
    booking_count = db.query(Booking).filter(
        Booking.schedule_id == schedule.id,
        Booking.status == "confirmed"
    ).count()
    
    if booking_count > 0:
        if not force:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"该课程有 {booking_count} 个预约，请先取消所有预约或使用 ?force=true 强制删除",
                headers={"X-Booking-Count": str(booking_count)}
            )
        else:
            # Force mode: Cancel all confirmed bookings
            db.query(Booking).filter(
                Booking.schedule_id == schedule.id,
                Booking.status == "confirmed"
            ).update({"status": "cancelled"})
    
    # Mark as inactive by setting capacity to 0
    # In production, consider adding an 'is_deleted' boolean column
    schedule.max_bookings = 0
    
    db.commit()
    
    return None  # 204 No Content
