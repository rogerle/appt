"""
Pydantic schemas for Booking model validation and serialization
"""

from typing import Optional
from pydantic import BaseModel, Field, validator


class BookingBase(BaseModel):
    """Base booking schema with common fields"""
    phone: str = Field(..., min_length=11, max_length=11, description="User's 11-digit phone number")
    name: str = Field(..., min_length=1, max_length=50, description="User's full name")


class BookingCreate(BookingBase):
    """Schema for creating a new booking"""
    instructor_id: int = Field(..., description="Instructor ID")
    studio_id: int = Field(..., description="Studio ID")
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Booking date (YYYY-MM-DD)")
    time_slot_start: str = Field(..., description="Start time of the slot (HH:MM)")
    time_slot_end: str = Field(..., description="End time of the slot (HH:MM)")


class BookingUpdate(BaseModel):
    """Schema for updating an existing booking"""
    status: Optional[str] = Field(None, pattern=r"^(confirmed|pending|completed|cancelled)$")


class BookingResponse(BookingBase):
    """Schema for booking response with all fields"""
    id: int
    instructor_id: int
    studio_id: int
    date: str
    time_slot_start: str
    time_slot_end: str
    status: str
    created_at: str
    
    class Config:
        from_attributes = True
