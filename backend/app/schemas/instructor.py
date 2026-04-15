"""
Instructor Schemas - CRUD Operations and Available Time Slots

Provides Pydantic models for instructor management endpoints.
Includes response model with available class slots.
"""

from datetime import datetime, time
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class InstructorBase(BaseModel):
    """Base schema for instructor data (shared between create/update)."""
    
    name: str = Field(..., min_length=2, max_length=100, description="教练姓名")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")
    phone: Optional[str] = Field(None, pattern=r'^1[3-9]\d{9}$', description="手机号（可选）")
    photo_url: Optional[str] = Field(None, description="头像 URL（可选）")


class InstructorCreate(InstructorBase):
    """Request model for creating a new instructor.
    
    Example:
        {
            "name": "张伟",
            "bio": "资深瑜伽教练，8 年教学经验，擅长流瑜伽和阴瑜伽",
            "phone": "13800138000"
        }
    """
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "张伟",
                "bio": "资深瑜伽教练，8 年教学经验，擅长流瑜伽和阴瑜伽",
                "phone": "13800138000"
            }
        }


class InstructorUpdate(BaseModel):
    """Request model for updating an existing instructor (all fields optional).
    
    Only provided fields will be updated (partial update).
    """
    
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    phone: Optional[str] = Field(None, pattern=r'^1[3-9]\d{9}$')
    photo_url: Optional[str] = Field(None)
    is_active: Optional[bool] = Field(None)


class InstructorResponse(BaseModel):
    """Response model for instructor data (includes all fields)."""
    
    id: int = Field(..., description="教练 ID")
    name: str = Field(..., description="教练姓名")
    bio: str = Field(..., description="个人简介")
    phone: str = Field(..., description="手机号")
    photo_url: str = Field(..., description="头像 URL")
    is_active: bool = Field(..., description="是否活跃")
    total_schedules: int = Field(..., ge=0, description="课程总数")
    created_at: str = Field(..., description="创建时间 (ISO format)")
    updated_at: str = Field(..., description="更新时间 (ISO format)")
    
    class Config:
        from_attributes = True


class TimeSlot(BaseModel):
    """Time slot information for availability display."""
    
    start_time: str = Field(..., description="开始时间 (HH:MM)")
    end_time: str = Field(..., description="结束时间 (HH:MM)")
    available_spots: int = Field(..., ge=0, description="可用名额")


class InstructorWithSlotsResponse(InstructorResponse):
    """Extended instructor response with available class times."""
    
    available_slots: List[TimeSlot] = Field(
        default_factory=list, 
        description="List of available time slots for the selected date"
    )
