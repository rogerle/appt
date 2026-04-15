"""Admin Schedules API - CRUD operations for schedule management."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_admin_user
from app.db.database import get_db
from app.db.models.user import User
from app.db.models.schedule import Schedule
from app.schemas.admin import ScheduleCreate, ScheduleUpdate, ScheduleResponse


router = APIRouter(prefix="/schedules", tags=["Admin - Schedules"])


@router.get("", response_model=list[ScheduleResponse])
async def list_schedules(
    instructor_id: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_admin_user)
):
    """List schedules with optional filter."""
    
    query = db.query(Schedule)
    
    if instructor_id:
        query = query.filter(Schedule.instructor_id == instructor_id)
    
    return query.order_by(Schedule.schedule_date.desc()).all()


@router.post("", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    schedule_data: ScheduleCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_admin_user)
):
    """Create a new schedule."""
    
    from app.db.models.instructor import Instructor
    
    # Verify instructor exists
    instructor = db.query(Instructor).filter(Instructor.id == schedule_data.instructor_id).first()
    if not instructor:
        raise HTTPException(status_code=404, detail="Instructor not found")

    db_schedule = Schedule(
        instructor_id=schedule_data.instructor_id,
        schedule_date=schedule_data.schedule_date,
        start_time=schedule_data.start_time,
        end_time=schedule_data.end_time,
        max_bookings=schedule_data.max_bookings
    )

    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)

    return db_schedule


@router.get("/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(schedule_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_admin_user)):
    """Get a specific schedule."""
    
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    return schedule


@router.put("/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: int, 
    schedule_data: ScheduleUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_admin_user)
):
    """Update a schedule."""
    
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    update_data = schedule_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(schedule, field, value)

    db.commit()
    db.refresh(schedule)

    return schedule


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_admin_user)
):
    """Delete a schedule."""
    
    from app.db.models.booking import Booking
    
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    # Check for confirmed bookings
    booking_count = db.query(Booking).filter(
        Booking.schedule_id == schedule_id,
        Booking.status == "confirmed"
    ).count()
    
    if booking_count > 0:
        raise HTTPException(
            status_code=409, 
            detail=f"Cannot delete schedule with {booking_count} confirmed bookings"
        )

    db.delete(schedule)
    db.commit()
