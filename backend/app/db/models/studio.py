"""
Studio Model - Yoga Studio Information Table

Represents the yoga studio/business owner information.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Index

from app.db.database import Base


class Studio(Base):
    """Yoga studio business information table."""
    
    __tablename__ = "studios"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="Studio name")
    phone = Column(String(20), nullable=True, comment="Contact phone number")
    address = Column(Text, nullable=True, comment="Physical address")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_studio_name', 'name'),
    )
