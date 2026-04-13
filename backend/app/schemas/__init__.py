"""
Pydantic Schemas Package

Provides request/response validation models for all API endpoints.
All schemas are type-validated and automatically documented in Swagger UI.
"""

from app.schemas.auth import (
    LoginRequest, 
    RegisterRequest, 
    TokenResponse,
    UserResponse
)
from app.schemas.instructor import (
    InstructorCreate,
    InstructorUpdate, 
    InstructorResponse,
    InstructorWithSlotsResponse
)
from app.schemas.schedule import (
    ScheduleCreate,
    ScheduleResponse,
    ScheduleBatchCreateRequest,
    ScheduleSlotResponse
)
from app.schemas.booking import (
    BookingCreate,
    BookingResponse,
    ConflictErrorSchema
)

__all__ = [
    # Auth schemas
    "LoginRequest",
    "RegisterRequest", 
    "TokenResponse",
    "UserResponse",
    
    # Instructor schemas
    "InstructorCreate",
    "InstructorUpdate",
    "InstructorResponse", 
    "InstructorWithSlotsResponse",
    
    # Schedule schemas
    "ScheduleCreate",
    "ScheduleResponse",
    "ScheduleBatchCreateRequest",
    "ScheduleSlotResponse",
    
    # Booking schemas
    "BookingCreate",
    "BookingResponse",
    "ConflictErrorSchema"
]
