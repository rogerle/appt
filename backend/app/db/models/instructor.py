"""
Instructor Model - Yoga Instructor Information Table

Represents yoga instructors with activity status and studio association.
Includes composite indexes for performance optimization.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.db.models.schedule import Schedule


class Instructor(Base):
    """Yoga instructor information table."""
    
    __tablename__ = "instructors"
    
    id = Column(Integer, primary_key=True, index=True)
    studio_id = Column(
        Integer, 
        ForeignKey("studios.id", ondelete="CASCADE"),
        nullable=False,
        comment="Reference to parent studio"
    )
    name = Column(String(50), nullable=False, comment="Instructor full name")
    avatar_url = Column(Text, nullable=True, comment="Profile picture URL")
    description = Column(Text, nullable=True, comment="Instructor bio/introduction")
    
    # Activity status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    schedules = relationship("Schedule", back_populates="instructor", cascade="all, delete-orphan")
    
    # Composite indexes for performance optimization
    __table_args__ = (
        Index('idx_instructor_composite', 'studio_id', 'is_active'),  # Studio + active status queries
    )
