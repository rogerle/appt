"""
Schedule Model - Yoga Class Time Slot Table

Represents scheduled yoga classes with instructor and capacity management.
Includes composite indexes for date/time range queries.
"""

from datetime import datetime, time
from typing import TYPE_CHECKING

from sqlalchemy import (
    Column, Integer, String, ForeignKey, DateTime, Boolean, JSON, 
    Date, Time, CheckConstraint, Index
)
from sqlalchemy.orm import relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.db.models.instructor import Instructor


class Schedule(Base):
    """Yoga class schedule table - represents teachable time slots."""
    
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    instructor_id = Column(
        Integer, 
        ForeignKey("instructors.id", ondelete="CASCADE"),
        nullable=False,
        comment="Reference to instructor who teaches this class"
    )
    
    # Date and time (stored as strings for flexibility)
    schedule_date = Column(Date, nullable=False, index=True, comment="Class date")
    start_time = Column(Time, nullable=False, comment="Start time of the class")
    end_time = Column(Time, nullable=False, comment="End time of the class")
    
    # Capacity management
    max_bookings = Column(Integer, default=1, nullable=False, 
                         check_constraint=True)  # Default: individual session
    
    # Recurring schedule support
    is_recurring = Column(Boolean, default=False, nullable=False)
    recurrence_pattern = Column(JSON, nullable=True, comment="Recurring pattern (e.g., weekdays)")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    instructor = relationship("Instructor", back_populates="schedules")
    bookings = relationship("Booking", back_populates="schedule", cascade="all, delete-orphan")
    
    # Check constraint: end time must be after start time
    __table_args__ = (
        CheckConstraint("end_time > start_time", name="check_time_validity"),
        
        # Composite indexes for performance optimization
        Index('idx_schedule_date_instructor', 'schedule_date', 'instructor_id'),  # Date + instructor queries
        Index('idx_schedule_time_range', 'start_time', 'end_time'),  # Time slot range queries
        
        # Unique constraint to prevent duplicate schedules (same instructor, date, time)
    )
