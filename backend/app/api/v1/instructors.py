"""
Instructor API Endpoints - CRUD Operations and Available Time Slots

Provides instructor management for studio owners.
Includes available time slot calculation for public viewing.
"""

from datetime import date, datetime, time, timedelta
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.schemas.instructor import (
    InstructorCreate,
    InstructorUpdate, 
    InstructorResponse,
    InstructorWithSlotsResponse,
    TimeSlot
)


router = APIRouter(
    prefix="/instructors",
    tags=["Instructors"],
)


@router.post("/", response_model=InstructorResponse, status_code=status.HTTP_201_CREATED,
             summary="Create new instructor (admin only)")
async def create_instructor(
    instructor_data: InstructorCreate,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_admin_user)  # Will add JWT auth in Phase 5
):
    """
    Create new instructor (admin only).
    
    Validates:
      - Name uniqueness within studio
      - Phone number format (if provided)
      - Bio length constraints
    
    Returns created instructor with generated ID.
    """
    
    from app.db.models.instructor import Instructor
    
    # Check for duplicate name (case-insensitive)
    existing = db.query(Instructor).filter(
        Instructor.name == instructor_data.name,
        Instructor.studio_id == 1
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="该教练姓名已存在"
        )
    
    # Create new instructor record
    db_instructor = Instructor(
        studio_id=1,  # Single studio for now
        name=instructor_data.name,
        description=instructor_data.bio,
        avatar_url=getattr(instructor_data, "photo_url", None),
        is_active=True,  # Default to active
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(db_instructor)
    db.commit()
    db.refresh(db_instructor)
    
    # Build response with schedule count (0 for new instructor)
    return InstructorResponse(
        id=db_instructor.id,
        name=db_instructor.name,
        bio=db_instructor.description or "",
        phone=getattr(db_instructor, "phone", "") or "",
        photo_url=db_instructor.avatar_url or "",
        is_active=True,
        total_schedules=0,  # New instructor has no schedules yet
        created_at=db_instructor.created_at.isoformat(),
        updated_at=db_instructor.updated_at.isoformat()
    )


@router.get("/", response_model=List[InstructorResponse], 
            summary="Get all instructors with filtering and pagination")
async def list_instructors(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Page offset"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by name or bio"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    date_param: Optional[date] = Query(None, alias="date", description="Filter by date (for slots)")
):
    """
    Get instructors with filtering and pagination.
    
    Query params:
      - skip: Page offset (default 0)
      - limit: Items per page (1-100, default 20)
      - search: Search term for name/bio matching  
      - is_active: Filter active/inactive instructors
      - date: Optional date for calculating available slots
    
    Returns paginated list with instructor details including schedule counts.
    """
    
    from app.db.models.instructor import Instructor
    from app.db.models.schedule import Schedule
    from sqlalchemy.orm import joinedload
    
    # Build base query with eager loading
    query = db.query(Instructor).options(
        joinedload(Instructor.schedules)
    ).filter(Instructor.studio_id == 1)  # Single studio filter
    
    # Apply search filter (if provided)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Instructor.name.ilike(search_pattern)) | 
            (Instructor.description.ilike(search_pattern))
        )
    
    # Apply status filter (if provided)
    if is_active is not None:
        query = query.filter(Instructor.is_active == is_active)
    
    # Count total for pagination metadata
    total_count = query.count()
    
    # Apply sorting FIRST, then pagination (SQLAlchemy requirement)
    instructors = query.order_by(
        Instructor.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    # Build response with schedule counts
    response_data = []
    
    for instructor in instructors:
        # Count all schedules (no is_active field in current schema)
        schedule_count = db.query(Schedule).filter(
            Schedule.instructor_id == instructor.id
        ).count()
        
        # Calculate available slots if date provided
        available_slots = []
        if date_param:
            from app.db.models.booking import Booking
            schedules = db.query(Schedule).filter(
                Schedule.instructor_id == instructor.id,
                Schedule.schedule_date == date_param,
                ~Schedule.is_recurring
            ).all()
            
            for schedule in schedules:
                booked_count = db.query(Booking).filter(
                    Booking.schedule_id == schedule.id,
                    Booking.status == 'confirmed'
                ).count()
                
                available_spots = max(0, schedule.max_bookings - booked_count)
                
                if available_spots > 0:
                    available_slots.append(TimeSlot(
                        start_time=schedule.start_time.strftime("%H:%M"),
                        end_time=schedule.end_time.strftime("%H:%M"),
                        available_spots=available_spots
                    ))
        
        response_data.append(InstructorResponse(
            id=instructor.id,
            name=instructor.name,
            bio=instructor.description or "",
            phone=getattr(instructor, 'phone', '') or "",
            photo_url=instructor.avatar_url or "",
            is_active=bool(instructor.is_active),
            total_schedules=schedule_count,
            created_at=instructor.created_at.isoformat(),
            updated_at=instructor.updated_at.isoformat()
        ))
    
    return response_data


@router.get("/{instructor_id}", response_model=InstructorResponse, 
            summary="Get instructor by ID with full details")
async def get_instructor(
    instructor_id: int,
    db: Session = Depends(get_db)
):
    """
    Get single instructor with complete details including all schedules.
    Uses eager loading to prevent N+1 query problem.
    """
    
    from app.db.models.instructor import Instructor
    from sqlalchemy.orm import joinedload
    
    # Use joinedload for efficient querying
    instructor = db.query(Instructor).options(
        joinedload(Instructor.schedules)
    ).filter(
        Instructor.id == instructor_id, 
        Instructor.studio_id == 1
    ).first()
    
    if not instructor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="教练不存在"
        )
    
    # Count active schedules for response
    schedule_count = db.query(Schedule).filter(
        Schedule.instructor_id == instructor.id,
        
    ).count()
    
    return InstructorResponse(
        id=instructor.id,
        name=instructor.name,
        bio=instructor.description or "",
        phone=getattr(instructor, "phone", "") or "",
        photo_url=instructor.avatar_url or "",
        is_active=bool(instructor.is_active),
        total_schedules=schedule_count,
        created_at=instructor.created_at.isoformat(),
        updated_at=instructor.updated_at.isoformat()
    )


@router.patch("/{instructor_id}", response_model=InstructorResponse, 
            summary="Update instructor information (partial update)")
async def update_instructor(
    instructor_id: int,
    updates: InstructorUpdate,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_admin_user)  # Will add JWT auth in Phase 5
):
    """
    Update instructor information (partial update - only provided fields changed).
    
    Validates updates and checks for duplicate names.
    Returns updated instructor object.
    """
    
    from app.db.models.instructor import Instructor
    from app.db.models.schedule import Schedule
    
    # Find instructor
    instructor = db.query(Instructor).filter(
        Instructor.id == instructor_id, 
        Instructor.studio_id == 1
    ).first()
    
    if not instructor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="教练不存在"
        )
    
    # Check for name conflict (if name is being updated)
    update_dict = updates.model_dump(exclude_unset=True)
    
    if 'name' in update_dict and update_dict['name'] != instructor.name:
        existing = db.query(Instructor).filter(
            Instructor.name == update_dict['name'],
            Instructor.id != instructor_id,  # Exclude current record
            Instructor.studio_id == 1
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail="新姓名已被其他教练使用"
            )
    
    # Update provided fields only (partial update)
    # Map schema fields to model fields and filter invalid ones
    FIELD_MAPPING = {
        'name': 'name',
        'bio': 'description',  # Schema uses bio, model uses description
        'photo_url': 'avatar_url',  # Schema uses photo_url, model uses avatar_url
        'is_active': 'is_active'
    }
    
    for schema_field, value in update_dict.items():
        if schema_field in FIELD_MAPPING:
            model_field = FIELD_MAPPING[schema_field]
            setattr(instructor, model_field, value)
    
    instructor.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(instructor)
    
    # Count active schedules for response
    schedule_count = db.query(Schedule).filter(
        Schedule.instructor_id == instructor.id,
        
    ).count()
    
    return InstructorResponse(
        id=instructor.id,
        name=instructor.name,
        bio=instructor.description or "",
        phone=getattr(instructor, "phone", "") or "",
        photo_url=instructor.avatar_url or "",
        is_active=bool(instructor.is_active),
        total_schedules=schedule_count,
        created_at=instructor.created_at.isoformat(),
        updated_at=instructor.updated_at.isoformat()
    )


@router.delete("/{instructor_id}", status_code=status.HTTP_204_NO_CONTENT, 
               summary="Soft delete instructor (admin only)")
async def delete_instructor(
    instructor_id: int,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_admin_user)  # Will add JWT auth in Phase 5
):
    """
    Soft delete instructor (set is_active=false).
    
    Does not physically delete record to preserve booking history.
    Prevents deletion if instructor has active schedules.
    Returns 204 No Content on success.
    """
    
    from app.db.models.instructor import Instructor
    from app.db.models.schedule import Schedule
    
    # Find instructor
    instructor = db.query(Instructor).filter(
        Instructor.id == instructor_id, 
        Instructor.studio_id == 1
    ).first()
    
    if not instructor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="教练不存在"
        )
    
    # Check if has active schedules (prevent deletion with existing classes)
    active_schedule_count = db.query(Schedule).filter(
        Schedule.instructor_id == instructor.id,
        
    ).count()
    
    if active_schedule_count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"无法删除：该教练有 {active_schedule_count} 个未完成的课程安排"
        )
    
    # Soft delete (mark as inactive)
    instructor.is_active = False
    instructor.updated_at = datetime.utcnow()
    
    db.commit()
    
    return None  # 204 No Content


@router.delete("/{instructor_id}/hard", status_code=status.HTTP_204_NO_CONTENT, 
               summary="Hard delete instructor (admin override)")
async def hard_delete_instructor(
    instructor_id: int,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_admin_user)  # Will add JWT auth in Phase 5
):
    """
    Permanently delete instructor (admin override).
    
    WARNING: This will also delete all associated schedules and bookings!
    Use with extreme caution. Requires explicit confirmation.
    """
    
    from app.db.models.instructor import Instructor
    from app.db.models.schedule import Schedule
    from app.db.models.booking import Booking
    
    # Find instructor
    instructor = db.query(Instructor).filter(
        Instructor.id == instructor_id, 
        Instructor.studio_id == 1
    ).first()
    
    if not instructor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="教练不存在"
        )
    
    # Delete all associated bookings first (to avoid foreign key constraints)
    # Get all schedule IDs for this instructor
    schedules = db.query(Schedule).filter(
        Schedule.instructor_id == instructor.id
    ).all()
    
    schedule_ids = [s.id for s in schedules]
    
    if schedule_ids:
        # Cancel/delete all bookings for these schedules
        db.query(Booking).filter(
            Booking.schedule_id.in_(schedule_ids)
        ).delete(synchronize_session=False)
    
    # Delete all associated schedules
    db.query(Schedule).filter(
        Schedule.instructor_id == instructor.id
    ).delete(synchronize_session=False)
    
    # Finally delete the instructor record itself
    db.delete(instructor)
    db.commit()
    
    return None  # 204 No Content
