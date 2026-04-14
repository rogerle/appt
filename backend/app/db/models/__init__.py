"""
Database Models Package

Exports all SQLAlchemy ORM models for use in the application.
Base must be imported and initialized before importing individual model files!
"""

# Import Base first to ensure it's properly initialized
from app.db.database import Base  # noqa: F401

from app.db.models.studio import Studio
from app.db.models.instructor import Instructor
from app.db.models.schedule import Schedule
from app.db.models.booking import Booking

__all__ = [
    "Studio",
    "Instructor", 
    "Schedule",
    "Booking"
]
