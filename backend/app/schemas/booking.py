"""
Booking Schemas - Customer Reservation and Conflict Management

Provides Pydantic models for booking CRUD with conflict detection.
Supports phone-based customer identification.
"""

from datetime import datetime, date, time
from typing import Optional, List
from pydantic import BaseModel, Field


class BookingBase(BaseModel):
    """Base schema for booking data (shared between create/update)."""
    
    schedule_id: int = Field(..., gt=0, description="Schedule slot ID to book")
    customer_name: str = Field(..., min_length=2, max_length=50, description="Customer full name")
    customer_phone: str = Field(..., pattern=r'^\d{11}$', description="Phone number (11 digits)")


class BookingCreate(BookingBase):
    """Request model for creating a new booking."""
    
    notes: Optional[str] = Field(None, max_length=500, description="Optional notes/requirements")


class BookingUpdate(BaseModel):
    """Request model for updating an existing booking (status only)."""
    
    status: str = Field(..., pattern=r'^(confirmed|cancelled)$', 
                       description="New status (confirmed/cancelled)")


class BookingResponse(BaseModel):
    """Response model for booking data (customer view)."""
    
    id: int = Field(..., description="Booking unique identifier")
    customer_name: str = Field(..., description="Customer name")
    instructor_name: str = Field(..., description="Instructor who teaches this class")
    schedule_date: date = Field(..., description="Class date (YYYY-MM-DD)")
    start_time: time = Field(..., description="Start time (HH:MM)")
    end_time: time = Field(..., description="End time (HH:MM)")
    status: str = Field(..., description="Booking status")


class BookingListResponse(BaseModel):
    """Extended booking response for admin dashboard."""
    
    id: int = Field(..., description="Booking ID")
    customer_name: str = Field(..., description="Customer name")
    customer_phone_masked: str = Field(..., description="Masked phone number (e.g., 138****8000)")
    instructor_name: str = Field(..., description="Instructor name")
    schedule_date: date = Field(..., description="Class date")
    start_time: time = Field(..., description="Start time")
    end_time: time = Field(..., description="End time")
    status: str = Field(..., description="Booking status")


class ConflictErrorSchema(BaseModel):
    """Response model for booking conflict errors."""
    
    error: str = Field("booking_conflict", description="Error type")
    message: str = Field(
        ..., 
        description="Human-readable explanation of the conflict"
    )
    conflicting_schedule_id: Optional[int] = Field(None, description="ID of conflicting booking")


class BookingConfirmationResponse(BaseModel):
    """Success response after successful booking."""
    
    success: bool = True
    message: str = Field(..., description="Confirmation message")
    booking_id: int = Field(..., description="Created booking ID")
