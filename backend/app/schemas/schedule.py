"""
Pydantic schemas for Schedule model validation and serialization
"""

from typing import Optional
from pydantic import BaseModel, Field


class ScheduleBase(BaseModel):
    """Base schedule schema with common fields"""
    instructor_id: int = Field(..., description="Instructor ID")
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Schedule date (YYYY-MM-DD)")
    start_time: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="Start time (HH:MM)")
    end_time: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="End time (HH:MM)")


class ScheduleCreate(ScheduleBase):
    """Schema for creating a new schedule"""
    max_capacity: int = Field(default=10, ge=1, le=50, description="Maximum class capacity")


class ScheduleResponse(BaseModel):
    """Schema for schedule response with ID and metadata"""
    id: int
    instructor_id: int
    date: str
    start_time: str
    end_time: str
    max_capacity: int
    is_active: bool
    
    class Config:
        from_attributes = True
