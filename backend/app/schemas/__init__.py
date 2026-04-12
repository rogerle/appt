from app.schemas.instructor import InstructorCreate, InstructorUpdate, InstructorResponse
from app.schemas.schedule import ScheduleCreate, ScheduleResponse, ScheduleAvailableSlots
from app.schemas.booking import BookingCreate, BookingResponse

__all__ = [
    "InstructorCreate", "InstructorUpdate", "InstructorResponse",
    "ScheduleCreate", "ScheduleResponse", "ScheduleAvailableSlots",
    "BookingCreate", "BookingResponse"
]
