"""
Admin Schemas - Pydantic models for admin-specific endpoints and responses.
"""

from datetime import date as dt_date, time as dt_time, datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field


# ============================================================================
# Enums
# ============================================================================

class UserRole(str, Enum):
    user = "user"
    admin = "admin"


# ============================================================================
# Dashboard Schemas
# ============================================================================

class DashboardStats(BaseModel):
    """Dashboard statistics response model."""
    total_bookings_today: int = Field(..., description="Confirmed bookings today")
    total_bookings_week: int = Field(..., description="Confirmed bookings this week")
    total_bookings_month: int = Field(..., description="Confirmed bookings this month")
    active_instructors: int = Field(..., description="Number of active instructors")
    available_slots: int = Field(..., description="Available booking slots in future schedules")
    revenue_this_month: float = Field(0.0, description="Revenue (placeholder)")

    class Config:
        from_attributes = True


class RecentBookingResponse(BaseModel):
    """Simplified booking response for recent bookings list."""
    id: int = Field(..., description="Booking ID")
    customer_name: str = Field(..., min_length=1)
    customer_phone: str = Field(..., pattern=r'^1[3-9]\d{9}$')
    
    # Schedule details - use different field names to avoid conflicts
    booking_date: dt_date  # Avoid 'date' name conflict with datetime.date
    start_time: dt_time
    end_time: dt_time
    class_type: str = Field(..., min_length=1)
    instructor_name: str
    
    status: str  # pending, confirmed, cancelled, completed
    created_at: datetime
    notes: Optional[str] = ""

    class Config:
        from_attributes = True


# ============================================================================
# Instructor Schemas (Admin CRUD)
# ============================================================================

class InstructorCreate(BaseModel):
    """Schema for creating a new instructor - matches actual DB model."""
    name: str = Field(..., min_length=2, max_length=50)  # Model has String(50)
    studio_id: int  # FK to studios table
    avatar_url: Optional[str] = None
    description: Optional[str] = Field(None, max_length=1000)


class InstructorUpdate(BaseModel):
    """Schema for updating an instructor (all fields optional)."""
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    studio_id: Optional[int] = None
    avatar_url: Optional[str] = None
    description: Optional[str] = Field(None, max_length=1000)


class InstructorResponse(BaseModel):
    """Complete instructor response matching DB model."""
    id: int
    studio_id: int
    name: str
    avatar_url: Optional[str] = None
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Schedule Schemas (Admin CRUD)
# ============================================================================

class ScheduleCreate(BaseModel):
    """Schema for creating a new schedule."""
    instructor_id: int
    schedule_date: dt_date  # Use 'schedule_date' to avoid conflict with datetime.date
    start_time: dt_time  
    end_time: dt_time
    max_bookings: int = Field(10, ge=1, le=50)  # Changed from max_participants


class ScheduleUpdate(BaseModel):
    """Schema for updating a schedule (all fields optional)."""
    start_time: Optional[dt_time] = None
    end_time: Optional[dt_time] = None
    max_bookings: Optional[int] = Field(None, ge=1, le=50)  # Changed from max_participants


class ScheduleResponse(BaseModel):
    """Complete schedule response with all fields."""
    id: int
    instructor_id: int
    schedule_date: dt_date  # Use 'schedule_date' to match DB field name
    start_time: dt_time  
    end_time: dt_time
    max_bookings: int  # Changed from max_participants
    is_recurring: bool = False  # From model
    
    # Denormalized data from related entities (computed at response time)
    instructor_name: Optional[str] = None
    
    # Current booking status (will be set in API layer)
    confirmed_bookings_count: int = 0
    pending_bookings_count: int = 0
    is_active: bool = True  # Default to active unless explicitly set

    class Config:
        from_attributes = True


# ============================================================================
# User Schemas (Admin Management)  
# ============================================================================

class UserResponse(BaseModel):
    """User response for admin user management."""
    id: int
    email: str
    username: str
    role: UserRole
    is_active: bool
    
    # Metadata
    created_at: datetime
    last_login_at: Optional[datetime] = None
    
    # Denormalized stats
    booking_count: int = 0

    class Config:
        from_attributes = True


class RoleUpdate(BaseModel):
    """Schema for updating user role."""
    role: UserRole


class StatusUpdate(BaseModel):
    """Schema for updating user account status."""
    is_active: bool
