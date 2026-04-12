"""
Pydantic schemas for Instructor model validation and serialization
"""

from typing import Optional
from pydantic import BaseModel, Field


class InstructorBase(BaseModel):
    """Base instructor schema with common fields"""
    name: str = Field(..., min_length=1, max_length=100, description="Instructor name")
    avatar_url: Optional[str] = Field(None, description="Profile image URL")
    bio: Optional[str] = Field(None, max_length=500, description="Brief biography")


class InstructorCreate(InstructorBase):
    """Schema for creating a new instructor"""
    pass


class InstructorUpdate(BaseModel):
    """Schema for updating an existing instructor"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    avatar_url: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None


class InstructorResponse(InstructorBase):
    """Schema for instructor response with ID and metadata"""
    id: int
    is_active: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
