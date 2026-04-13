"""
Instructor Schemas - CRUD Operations and Available Time Slots

Provides Pydantic models for instructor management endpoints.
Includes response model with available class slots.
"""

from datetime import datetime, time
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class InstructorBase(BaseModel):
    """Base schema for instructor data (shared between create/update)."""
    
    name: str = Field(..., min_length=2, max_length=50, description="Instructor full name")
    description: Optional[str] = Field(None, max_length=1000, description="Bio/introduction text")


class InstructorCreate(InstructorBase):
    """Request model for creating a new instructor."""
    
    pass  # Inherits all fields from InstructorBase


class InstructorUpdate(BaseModel):
    """Request model for updating an existing instructor (all fields optional)."""
    
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = Field(None, max_length=1000)
    is_active: Optional[bool] = Field(None, description="Toggle instructor activity status")


class InstructorResponse(InstructorBase):
    """Response model for instructor data (public-facing)."""
    
    id: int = Field(..., description="Instructor unique identifier")
    avatar_url: Optional[str] = Field(None, description="Profile picture URL")
    is_active: bool = Field(..., description="Whether instructor is currently active")
    created_at: datetime = Field(..., description="Creation timestamp")


class TimeSlot(BaseModel):
    """Time slot information for availability display."""
    
    start_time: time = Field(..., description="Start time (HH:MM)")
    end_time: time = Field(..., description="End time (HH:MM)")
    available_spots: int = Field(..., description="Number of available slots")


class InstructorWithSlotsResponse(InstructorResponse):
    """Extended instructor response with available class times."""
    
    available_slots: List[TimeSlot] = Field(
        default_factory=list, 
        description="List of available time slots for the selected date"
    )
