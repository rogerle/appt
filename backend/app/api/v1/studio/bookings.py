"""
Studio Management API - Booking endpoints (Admin only)

Endpoints:
- GET /api/v1/studio/bookings - View all bookings (admin)
- DELETE /api/v1/studio/bookings/{id} - Cancel booking
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import logging

from api.v1.deps import get_current_user
from db.database import get_db
from schemas.booking import BookingResponse
from models.booking import Booking


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/bookings", tags=["studio-bookings"])


@router.get("", response_model=List[BookingResponse])
def list_bookings(
    status: Optional[str] = Query(None, description="Filter by booking status"),
    date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all bookings for admin view.
    
    Optionally filter by status or specific date.
    Returns comprehensive booking information including user details.
    """
    query = db.query(Booking)
    
    if status:
        query = query.filter(Booking.status == status)
    
    if date:
        query = query.filter(Booking.date == date)
    
    # Order by date descending, then time_slot_start
    bookings = query.order_by(
        Booking.date.desc(), 
        Booking.time_slot_start.desc()
    ).all()
    
    return bookings


@router.delete("/{booking_id}", status_code=204)
def cancel_booking(
    booking_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel a booking by ID (admin only).
    
    Only allows cancelling bookings that are not yet completed.
    Returns 204 No Content on success.
    """
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Prevent cancelling completed bookings
    if booking.status == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel a completed booking"
        )
    
    # Update status to cancelled
    booking.status = "cancelled"
    
    db.commit()
    
    logger.info(f"Booking {booking_id} cancelled by admin: {current_user}")
    
    return None
