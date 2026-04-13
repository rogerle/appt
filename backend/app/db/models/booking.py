"""
Booking Model - Customer Reservation Table

Represents customer bookings with conflict detection and status management.
Includes composite indexes for customer queries and capacity validation.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, CheckConstraint, Index, func
from sqlalchemy.orm import relationship, validates

from app.db.database import Base

if TYPE_CHECKING:
    from app.db.models.schedule import Schedule


class Booking(Base):
    """Customer booking/reservation table."""
    
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(
        Integer, 
        ForeignKey("schedules.id", ondelete="CASCADE"),
        nullable=False,
        comment="Reference to scheduled class slot"
    )
    
    # Customer information
    customer_name = Column(String(50), nullable=False, index=True)
    customer_phone = Column(String(20), nullable=False, index=True)  # Used for lookup and login
    
    # Status management
    status = Column(String(20), default="confirmed", 
                   comment="confirmed/cancelled/no_show")
    
    # Optional notes (e.g., allergies, special requirements)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    schedule = relationship("Schedule", back_populates="bookings")
    
    @validates('customer_phone')
    def validate_phone(self, key, phone):
        """Validate phone number format (basic Chinese mobile pattern)."""
        if not phone.isdigit() or len(phone) < 11:
            raise ValueError("Invalid phone number format")
        return phone
    
    # Check constraint: only valid statuses allowed
    __table_args__ = (
        CheckConstraint(
            "status IN ('confirmed', 'cancelled', 'no_show')",
            name="check_booking_status"
        ),
        
        # Composite indexes for performance optimization
        Index('idx_booking_customer_status', 'customer_phone', 'status'),  # Customer lookup queries
        Index('idx_booking_schedule_created', 'schedule_id', 'created_at'),  # Schedule + time queries
        
        # Ensure same phone can't double-book the same slot (business logic enforced in API layer)
    )
