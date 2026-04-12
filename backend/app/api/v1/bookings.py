"""
Booking API endpoints - User-facing booking management

Endpoints:
- POST /api/v1/bookings - Create new booking (with conflict detection)
- GET /api/v1/bookings?phone=xxx - Get user's bookings by phone number
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func
import logging

from db.database import get_db
from schemas.booking import BookingCreate, BookingResponse
from models.booking import Booking


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("", response_model=BookingResponse, status_code=201)
def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new booking with conflict detection.
    
    Checks for overlapping time slots and existing bookings before creating.
    """
    # Check if instructor has conflicting schedules at this time (optimized with index)
    from models.schedule import Schedule
    
    # Use composite query for faster execution with indexes on (instructor_id, date, start_time, end_time)
    conflicting_schedule = db.query(Schedule).filter(
        Schedule.instructor_id == booking_data.instructor_id,
        Schedule.date == booking_data.date,
        Schedule.start_time <= booking_data.time_slot_start,
        Schedule.end_time >= booking_data.time_slot_end
    ).first()
    
    if conflicting_schedule:
        raise HTTPException(
            status_code=409,
            detail="Instructor already has a class scheduled at this time"
        )
    
    # Check for existing booking by same user
    existing_booking = db.query(Booking).filter(
        and_(
            Booking.phone == booking_data.phone,
            Booking.date == booking_data.date,
            Booking.instructor_id == booking_data.instructor_id,
            Booking.status != "cancelled"
        )
    ).first()
    
    if existing_booking:
        raise HTTPException(
            status_code=409,
            detail="You already have a booking with this instructor on the same date"
        )
    
    # Create new booking
    db_booking = Booking(
        phone=booking_data.phone,
        name=booking_data.name,
        instructor_id=booking_data.instructor_id,
        studio_id=booking_data.studio_id,
        date=booking_data.date,
        time_slot_start=booking_data.time_slot_start,
        time_slot_end=booking_data.time_slot_end,
        status="confirmed"
    )
    
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    
    logger.info(f"Booking created: {db_booking.id} for {db_booking.phone}")
    
    return db_booking


@router.get("", response_model=List[BookingResponse])
def get_user_bookings(
    phone: str = Query(..., description="User's phone number"),
    status: Optional[str] = Query(None, description="Filter by booking status"),
    db: Session = Depends(get_db)
):
    """
    Get all bookings for a specific phone number with eager loading.
    
    Optionally filter by booking status (confirmed/pending/completed/cancelled).
    Uses joinedload to avoid N+1 queries when accessing schedule/instructor data.
    """
    query = db.query(Booking).filter(Booking.customer_phone == phone)
    
    if status:
        query = query.filter(Booking.status == status)
    
    # Use joinedload for eager loading to avoid N+1 queries
    query = query.options(joinedload(Booking.schedule), joinedload(Booking.instructor))
    
    # Order by date descending, then time_slot_start
    bookings = query.order_by(
        Booking.created_at.desc(),
        Booking.time_slot_start.desc()
    ).all()
    
    return bookings
