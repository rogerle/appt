"""
Booking API Endpoints - Customer Reservations with Conflict Detection

Provides booking creation, listing, and cancellation.
Includes automatic conflict detection to prevent double-booking.
"""

from datetime import datetime, date, time
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.schemas.booking import (
    BookingCreate,
    BookingResponse,
    BookingListResponse,
    ConflictErrorSchema,
    BookingConfirmationResponse
)


router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"],
)


def check_booking_conflict(db: Session, schedule_id: int, 
                           customer_phone: str) -> Optional[int]:
    """Check if customer already has a confirmed booking for this slot."""
    
    from app.db.models.booking import Booking
    
    # Check for existing confirmed booking for the same schedule and phone
    existing = db.query(Booking).filter(
        Booking.schedule_id == schedule_id,
        Booking.customer_phone == customer_phone,
        Booking.status == 'confirmed'
    ).first()
    
    return existing.id if existing else None


def check_slot_capacity(db: Session, schedule_id: int) -> bool:
    """Check if the time slot has reached maximum capacity."""
    
    from app.db.models.schedule import Schedule
    from app.db.models.booking import Booking
    
    # Get schedule info
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        return False  # Schedule doesn't exist - let other validation handle this
    
    # Count confirmed bookings for this slot
    booked_count = db.query(Booking).filter(
        Booking.schedule_id == schedule_id,
        Booking.status == 'confirmed'
    ).count()
    
    return booked_count >= schedule.max_bookings


@router.post("/", response_model=BookingConfirmationResponse, 
             status_code=status.HTTP_201_CREATED, summary="Create new booking")
async def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db)
    # No authentication required - public endpoint
):
    """Submit a yoga class reservation for a customer."""
    
    from app.db.models.booking import Booking
    from app.db.models.schedule import Schedule
    
    # Check if schedule exists and is valid
    schedule = db.query(Schedule).filter(
        Schedule.id == booking_data.schedule_id,
        ~Schedule.is_recurring  # Only allow booking non-recurring schedules
    ).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time slot not found or unavailable"
        )
    
    # Check for double-booking by same customer
    existing_booking_id = check_booking_conflict(db, booking_data.schedule_id, 
                                                  booking_data.customer_phone)
    if existing_booking_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You already have a confirmed booking for this time slot",
            headers={"X-Conflict-Type": "double-booking"}
        )
    
    # Check slot capacity
    if check_slot_capacity(db, booking_data.schedule_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This time slot is fully booked",
            headers={"X-Conflict-Type": "capacity-exceeded"}
        )
    
    # Create and save new booking
    db_booking = Booking(
        schedule_id=booking_data.schedule_id,
        customer_name=booking_data.customer_name,
        customer_phone=booking_data.customer_phone,
        notes=booking_data.notes,
        status='confirmed'
    )
    
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    
    return BookingConfirmationResponse(
        success=True,
        message=f"预约成功！您已预订 {schedule.start_time}-{schedule.end_time} 的课程",
        booking_id=db_booking.id
    )


@router.get("/", response_model=List[BookingListResponse], 
             summary="Get bookings list (customer view)")
async def list_bookings(
    phone: str = Query(..., description="Customer phone number for lookup"),
    db: Session = Depends(get_db)
):
    """Retrieve booking history for a customer by phone number."""
    
    from app.db.models.booking import Booking
    
    # Mask phone number in response (privacy protection)
    masked_phone = f"{phone[:3]}****{phone[-4:]}" if len(phone) == 11 else "***-***-{phone[-4:]}"
    
    # Get bookings with schedule details via JOIN for proper ordering
    from app.db.models.schedule import Schedule
    
    bookings = db.query(Booking).join(
        Schedule, Booking.schedule_id == Schedule.id
    ).filter(
        Booking.customer_phone == phone,
        Booking.status != 'cancelled'  # Only show active bookings by default
    ).order_by(Schedule.schedule_date.desc()).all()
    
    response = []
    for booking in bookings:
        # Get schedule and instructor details (JOIN simulation)
        from app.db.models.schedule import Schedule
        from app.db.models.instructor import Instructor
        
        schedule = db.query(Schedule).filter(Schedule.id == booking.schedule_id).first()
        
        if schedule:
            instructor = db.query(Instructor).filter(
                Instructor.id == schedule.instructor_id
            ).first()
            
            response.append(BookingListResponse(
                id=booking.id,
                customer_name=booking.customer_name,
                customer_phone_masked=masked_phone,
                instructor_name=instructor.name if instructor else "Unknown",
                schedule_date=schedule.schedule_date,
                start_time=schedule.start_time,
                end_time=schedule.end_time,
                status=booking.status
            ))
    
    return response


@router.get("/admin/", response_model=List[BookingResponse], 
             summary="Get all bookings (admin view)")
async def admin_list_bookings(
    date_param: Optional[date] = Query(None, description="Filter by date"),
    instructor_id: Optional[int] = Query(None, description="Filter by instructor ID"),
    db: Session = Depends(get_db),
    token: str = Depends(lambda token: settings.ADMIN_USERNAME)  # TODO: JWT validation
):
    """Retrieve all bookings with admin-level details (for dashboard)."""
    
    from app.db.models.booking import Booking
    from app.db.models.schedule import Schedule
    from app.db.models.instructor import Instructor
    
    query = db.query(Booking).join(Schedule, Booking.schedule_id == Schedule.id) \
                          .join(Instructor, Schedule.instructor_id == Instructor.id)
    
    if date_param:
        query = query.filter(Schedule.schedule_date == date_param)
    
    if instructor_id:
        query = query.filter(Schedule.instructor_id == instructor_id)
    
    bookings = query.all()
    
    response = []
    for booking in bookings:
        schedule = db.query(Schedule).filter(
            Schedule.id == booking.schedule_id,
            ~Schedule.is_recurring
        ).first()
        
        if not schedule:
            continue
        
        instructor = db.query(Instructor).filter(
            Instructor.id == schedule.instructor_id
        ).first()
        
        response.append(BookingResponse(
            id=booking.id,
            customer_name=booking.customer_name,
            instructor_name=instructor.name if instructor else "Unknown",
            schedule_date=schedule.schedule_date,
            start_time=schedule.start_time,
            end_time=schedule.end_time,
            status=booking.status
        ))
    
    return response


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT, 
               summary="Cancel booking")
async def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(lambda token: settings.ADMIN_USERNAME)  # TODO: JWT validation (or phone check for customers)
):
    """Cancel an existing booking."""
    
    from app.db.models.booking import Booking
    
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Only allow cancellation of confirmed bookings
    if booking.status != 'confirmed':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel booking with status: {booking.status}"
        )
    
    # Soft delete (mark as cancelled instead of removing)
    booking.status = 'cancelled'
    db.commit()
    
    return None  # No content response
