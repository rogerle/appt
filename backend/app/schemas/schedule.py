"""
Schedule Schemas - Class Slot Management and Batch Operations

Provides Pydantic models for schedule CRUD and batch creation endpoints.
Supports weekly recurring pattern configuration.
"""

from datetime import date, time
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class ScheduleBase(BaseModel):
    """Base schema for schedule data (shared between create/update)."""
    
    instructor_id: int = Field(..., gt=0, description="Instructor ID")
    schedule_date: date = Field(..., description="Class date (YYYY-MM-DD)")
    start_time: time = Field(..., description="Start time (HH:MM)")
    end_time: time = Field(..., description="End time (HH:MM)")
    max_bookings: int = Field(default=1, gt=0, description="Maximum bookings for this slot")


class ScheduleCreate(ScheduleBase):
    """Request model for creating a single class schedule."""
    
    pass  # Inherits all fields from ScheduleBase


class ScheduleUpdate(BaseModel):
    """Request model for updating an existing schedule (all fields optional)."""
    
    instructor_id: Optional[int] = Field(None, gt=0)
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    max_bookings: Optional[int] = Field(None, ge=0)
    is_recurring: Optional[bool] = None


class ScheduleResponse(BaseModel):
    """Response model for schedule data (includes admin details)."""
    
    id: int = Field(..., description="课程 ID")
    instructor_id: int = Field(..., description="教练 ID")
    instructor_name: str = Field(..., description="教练姓名")  # Denormalized for display
    schedule_date: str = Field(..., description="日期 (ISO format YYYY-MM-DD)")
    start_time: str = Field(..., description="开始时间 (HH:MM)")
    end_time: str = Field(..., description="结束时间 (HH:MM)")
    max_bookings: int = Field(..., ge=0, description="容纳人数")
    available_spots: int = Field(..., ge=0, description="可用名额")
    booking_count: int = Field(default=0, ge=0, description="已预约数")


class ScheduleSlotResponse(BaseModel):
    """Simplified slot response for frontend display."""
    
    id: int = Field(..., description="Schedule ID")
    start_time: time = Field(..., description="Start time (HH:MM)")
    end_time: time = Field(..., description="End time (HH:MM)")
    available_spots: int = Field(..., description="Available spots count")


class ScheduleBatchCreateRequest(BaseModel):
    """Request model for batch creating weekly schedules."""
    
    instructor_id: int = Field(..., gt=0, description="Instructor ID")
    start_date: date = Field(..., description="Start date of the week (YYYY-MM-DD)")
    end_date: date = Field(..., description="End date of the week (YYYY-MM-DD)")
    weekdays: List[int] = Field(
        ..., 
        min_length=1, 
        max_length=7,
        description="Weekdays to schedule [1=Monday, 7=Sunday]"
    )
    start_time: time = Field(..., description="Start time (HH:MM)")
    end_time: time = Field(..., description="End time (HH:MM)")


class ScheduleBatchCreateResponse(BaseModel):
    """Response model for batch schedule creation."""
    
    created_count: int = Field(..., description="Number of schedules created")
    schedule_ids: List[int] = Field(default_factory=list, description="IDs of created schedules")
