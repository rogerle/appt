"""
Schedule API endpoints - User-facing schedule listing

Endpoints:
- GET /api/v1/schedules?date=xxx&instructor_id=xxx 查询可用时段
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from db.database import get_db
from models.schedule import Schedule


router = APIRouter(prefix="/schedules", tags=["schedules"])


@router.get("")
def list_schedules(
    date: Optional[str] = Query(None, description="Filter schedules by date (YYYY-MM-DD)"),
    instructor_id: Optional[int] = Query(None, description="Filter by instructor ID"),
    db: Session = Depends(get_db)
):
    """
    Get available class schedules.
    
    Filter by date and/or instructor to find available time slots.
    """
    query = db.query(Schedule).filter(
        Schedule.date == date if date else True,
        Schedule.instructor_id == instructor_id if instructor_id else True,
        Schedule.is_active == True
    )
    
    schedules = query.all()
    
    return [
        {
            "id": s.id,
            "instructor_id": s.instructor_id,
            "date": s.date,
            "start_time": s.start_time,
            "end_time": s.end_time,
            "max_capacity": s.max_capacity
        }
        for s in schedules
    ]
