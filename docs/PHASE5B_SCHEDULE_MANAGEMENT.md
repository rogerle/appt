# 📅 Phase 5B Part 2: Schedule Management - Atomic Task Breakdown

**Continuation of PHASE5B_ADMIN_FEATURES_TASKS.md**  
**Focus**: Complete CRUD operations for yoga class schedules  

---

## 🔨 PART 2: Schedule Management (排课管理) - 7 Atomic Tasks

### **Backend Tasks (4 tasks)**

#### Task B5.10: Create Schedule API - GET All with Filters ⏱️ ~30 min
**Priority**: P0 - Critical Path  
**Dependencies**: None  
**Files to Modify**: `backend/app/api/v1/schedules.py`

**Acceptance Criteria**:
```python
# Enhanced list endpoint for admin use:
@router.get("/", response_model=list[ScheduleAdminResponse])
async def get_schedules(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    date_from: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    instructor_id: Optional[int] = Query(None, description="Filter by instructor"),
    is_active: Optional[bool] = Query(None, description="Filter by active status")
):
    """
    Get schedules with advanced filtering for admin management.
    
    Query params:
      - date_from/date_to: Date range filter
      - instructor_id: Filter specific instructor's classes  
      - is_active: Show only active/inactive schedules
    
    Returns paginated list with instructor details included.
    """
    
    from sqlalchemy.orm import joinedload
    
    query = db.query(Schedule).options(
        joinedload(Schedule.instructor)  # Eager load instructor data
    ).filter(
        Schedule.studio_id == 1,
        Schedule.date >= date_from if date_from else True,
        Schedule.date <= date_to if date_to else True
    )
    
    if instructor_id:
        query = query.filter(Schedule.instructor_id == instructor_id)
    
    if is_active is not None:
        query = query.filter(Schedule.is_active == is_active)
    
    total = query.count()
    schedules = query.offset(skip).limit(limit).order_by(
        Schedule.date.desc(), 
        Schedule.start_time.asc()
    ).all()
    
    # Build response with nested instructor data
    result = []
    for schedule in schedules:
        result.append(ScheduleAdminResponse(
            id=schedule.id,
            date=schedule.date.isoformat(),
            start_time=schedule.start_time.strftime("%H:%M"),
            end_time=schedule.end_time.strftime("%H:%M"),
            capacity=schedule.capacity,
            available_spots=schedule.available_spots,
            is_active=bool(schedule.is_active),
            instructor_id=schedule.instructor.id,
            instructor_name=schedule.instructor.name,  # Denormalized for display
            booking_count=db.query(Booking).filter(
                Booking.schedule_id == schedule.id,
                Booking.status == "confirmed"
            ).count(),
            created_at=schedule.created_at.isoformat()
        ))
    
    return result

# New response schema in schemas/schedule.py:
class ScheduleAdminResponse(BaseModel):
    id: int
    date: str  # ISO format YYYY-MM-DD
    start_time: str  # HH:MM format
    end_time: str
    capacity: int
    available_spots: int
    is_active: bool
    
    # Admin-only fields (includes instructor details)
    instructor_id: int
    instructor_name: str
    booking_count: int = 0
    
    created_at: str
    
    class Config:
        from_attributes = True
```

**API Contract**:
- `GET /api/v1/schedules?date_from=2026-04-15&date_to=2026-04-30` → Date range filter
- Returns schedules with instructor name denormalized for display

---

#### Task B5.11: Create Schedule API - POST ⏱️ ~40 min  
**Priority**: P0 - Critical Path  
**Dependencies**: None  
**Files to Modify**: `backend/app/api/v1/schedules.py`, `backend/app/schemas/schedule.py`

**Acceptance Criteria**:
```python
class ScheduleCreate(BaseModel):
    instructor_id: int = Field(..., gt=0, description="教练 ID")
    date: date = Field(..., description="课程日期")
    start_time: time = Field(..., description="开始时间")
    end_time: time = Field(..., description="结束时间")
    capacity: int = Field(..., ge=1, le=50, description="容纳人数 (1-50)")

@router.post("/", response_model=ScheduleAdminResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    schedule_data: ScheduleCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Create new class schedule with conflict detection.
    
    Validates:
      - Instructor exists and is active
      - End time > start time  
      - Capacity within range (1-50)
      - No overlapping schedules for same instructor on same date
    
    Returns created schedule or 409 Conflict if time overlaps exist.
    """
    
    # Verify instructor exists and is active
    instructor = db.query(Instructor).filter(
        Instructor.id == schedule_data.instructor_id,
        Instructor.is_active == True,
        Instructor.studio_id == 1
    ).first()
    
    if not instructor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="教练不存在或已停用"
        )
    
    # Validate time range
    if schedule_data.end_time <= schedule_data.start_time:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="结束时间必须晚于开始时间"
        )
    
    # Check for overlapping schedules (conflict detection)
    conflicts = db.query(Schedule).filter(
        Schedule.instructor_id == schedule_data.instructor_id,
        Schedule.date == schedule_data.date,
        Schedule.is_active == True,
        
        # Overlap condition: new start < existing end AND new end > existing start
        (Schedule.start_time < schedule_data.end_time),
        (Schedule.end_time > schedule_data.start_time)
    ).first()
    
    if conflicts:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"时间冲突：该教练在 {schedule_data.date.strftime('%Y-%m-%d')} 已有其他课程安排在此时间段"
        )
    
    # Calculate available spots (initially equals capacity)
    available_spots = schedule_data.capacity
    
    # Create new schedule
    db_schedule = Schedule(
        studio_id=1,
        instructor_id=schedule_data.instructor_id,
        date=schedule_data.date,
        start_time=schedule_data.start_time,
        end_time=schedule_data.end_time,
        capacity=schedule_data.capacity,
        available_spots=available_spots,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    
    # Build response with instructor details
    return ScheduleAdminResponse(
        id=db_schedule.id,
        date=db_schedule.date.isoformat(),
        start_time=db_schedule.start_time.strftime("%H:%M"),
        end_time=db_schedule.end_time.strftime("%H:%M"),
        capacity=db_schedule.capacity,
        available_spots=db_schedule.available_spots,
        is_active=True,
        instructor_id=instructor.id,
        instructor_name=instructor.name,
        booking_count=0,  # New schedule has no bookings yet
        created_at=db_schedule.created_at.isoformat()
    )
```

**API Contract**:
- `POST /api/v1/schedules` → Create new class (admin only)
- Request: `{instructor_id, date, start_time, end_time, capacity}`
- Response: HTTP 201 + created schedule with instructor name
- Errors: 
  - 404 if instructor doesn't exist or inactive
  - 409 if time conflicts detected
  - 422 for invalid data (end <= start, capacity out of range)

---

#### Task B5.12: Update Schedule API - PATCH ⏱️ ~35 min  
**Priority**: P1 - Important  
**Dependencies**: Task B5.10 Complete  
**Files to Modify**: `backend/app/api/v1/schedules.py`, `backend/app/schemas/schedule.py`

**Acceptance Criteria**:
```python
class ScheduleUpdate(BaseModel):
    instructor_id: Optional[int] = Field(None, gt=0)
    date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    capacity: Optional[int] = Field(None, ge=1, le=50)
    is_active: Optional[bool] = None

@router.patch("/{schedule_id}", response_model=ScheduleAdminResponse)
async def update_schedule(
    schedule_id: int, 
    updates: ScheduleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Update schedule with conflict detection for time changes.
    
    Partially updates provided fields and re-checks for overlapping schedules.
    Prevents capacity reduction below existing booking count.
    """
    
    # Find schedule
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id, 
        Schedule.studio_id == 1
    ).first()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="课程不存在")
    
    update_data = updates.dict(exclude_unset=True)
    
    # Special handling for time/date changes - need conflict detection
    if any(field in update_data for field in ['date', 'start_time', 'end_time', 'instructor_id']):
        # Build temporary schedule object with proposed changes
        proposed_date = update_data.get('date', schedule.date)
        proposed_start = update_data.get('start_time', schedule.start_time)
        proposed_end = update_data.get('end_time', schedule.end_time)
        proposed_instructor = update_data.get('instructor_id', schedule.instructor_id)
        
        # Check for conflicts (excluding current record)
        conflicts = db.query(Schedule).filter(
            Schedule.id != schedule_id,  # Exclude self
            Schedule.instructor_id == proposed_instructor,
            Schedule.date == proposed_date,
            Schedule.is_active == True,
            (Schedule.start_time < proposed_end),
            (Schedule.end_time > proposed_start)
        ).first()
        
        if conflicts:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="时间冲突：修改后的时间段与其他课程重叠"
            )
    
    # Special handling for capacity changes - cannot reduce below existing bookings
    if 'capacity' in update_data:
        new_capacity = update_data['capacity']
        
        # Count confirmed bookings
        booking_count = db.query(Booking).filter(
            Booking.schedule_id == schedule.id,
            Booking.status == "confirmed"
        ).count()
        
        if new_capacity < booking_count:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"无法减少容量：该课程已有 {booking_count} 个预约，容量至少需要设置为 {booking_count}"
            )
    
    # Apply all updates
    for field, value in update_data.items():
        setattr(schedule, field, value)
    
    schedule.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(schedule)
    
    # Recalculate available spots after capacity change or new bookings
    booking_count = db.query(Booking).filter(
        Booking.schedule_id == schedule.id,
        Booking.status == "confirmed"
    ).count()
    schedule.available_spots = max(0, schedule.capacity - booking_count)
    
    # Get instructor for response
    instructor = db.query(Instructor).get(schedule.instructor_id)
    
    return ScheduleAdminResponse(
        id=schedule.id,
        date=schedule.date.isoformat(),
        start_time=schedule.start_time.strftime("%H:%M"),
        end_time=schedule.end_time.strftime("%H:%M"),
        capacity=schedule.capacity,
        available_spots=schedule.available_spots,
        is_active=bool(schedule.is_active),
        instructor_id=instructor.id,
        instructor_name=instructor.name,
        booking_count=booking_count,
        created_at=schedule.created_at.isoformat()
    )
```

**API Contract**:
- `PATCH /api/v1/schedules/{id}` → Partial update with validation
- Time/date changes re-check for conflicts (409 if overlap)
- Capacity cannot be reduced below existing booking count (422 error)

---

#### Task B5.13: Delete Schedule API - DELETE ⏱️ ~25 min  
**Priority**: P1 - Important  
**Dependencies**: None  
**Files to Modify**: `backend/app/api/v1/schedules.py`

**Acceptance Criteria**:
```python
@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(
    schedule_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Soft delete schedule (set is_active=false).
    
    If schedule has confirmed bookings, requires force=true query parameter.
    When forced, all associated bookings are cancelled automatically.
    
    Query params:
      - force: Cancel existing bookings and delete anyway (default false)
    """
    
    # Find schedule  
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id, 
        Schedule.studio_id == 1
    ).first()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="课程不存在")
    
    # Check for existing bookings
    booking_count = db.query(Booking).filter(
        Booking.schedule_id == schedule.id,
        Booking.status == "confirmed"
    ).count()
    
    if booking_count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"该课程有 {booking_count} 个预约，请先取消所有预约或使用 force=true 强制删除",
            headers={"X-Booking-Count": str(booking_count)}
        )
    
    # Soft delete (mark as inactive)
    schedule.is_active = False
    schedule.updated_at = datetime.utcnow()
    
    db.commit()
    
    return None  # 204 No Content

# Alternative: Hard delete with force parameter (optional):
@router.delete("/{schedule_id}/force", status_code=status.HTTP_204_NO_CONTENT)  
async def force_delete_schedule(
    schedule_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Force delete schedule and cancel all associated bookings.
    
    WARNING: This will automatically cancel all confirmed bookings for this class!
    Bookings are cancelled (status='cancelled') rather than deleted to preserve history.
    """
    
    # Find schedule
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id, 
        Schedule.studio_id == 1
    ).first()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="课程不存在")
    
    # Cancel all confirmed bookings for this schedule
    cancelled_count = db.query(Booking).filter(
        Booking.schedule_id == schedule.id,
        Booking.status == "confirmed"
    ).update({"status": "cancelled"})
    
    # Soft delete the schedule itself
    schedule.is_active = False
    schedule.updated_at = datetime.utcnow()
    
    db.commit()
    
    return None  # 204 No Content
```

**API Contract**:
- `DELETE /api/v1/schedules/{id}` → Soft delete (fails if has bookings, returns 409)
- `DELETE /api/v1/schedules/{id}/force` → Force delete + auto-cancel all bookings

---

### **Frontend Tasks (3 tasks)**

#### Task B5.14: Create Schedule Management Page - Calendar/List Views ⏱️ ~60 min  
**Priority**: P0 - Critical Path  
**Dependencies**: Tasks B5.10-B5.13 Complete  
**Files to Modify**: `frontend/src/views/admin/ScheduleManagement.vue`

**Key Features**:
- Dual view: Calendar (month/week) + List toggle
- Date range filter with date picker
- Instructor dropdown filter  
- Color-coded schedule cards showing capacity and booking count
- Quick actions: Edit/Delete buttons on each card

---

#### Task B5.15: Create Schedule Form Wizard (Multi-step) ⏱️ ~70 min  
**Priority**: P0 - Critical Path  
**Dependencies**: Tasks B5.11, B5.12 Complete  
**Files to Create**: `frontend/src/components/admin/ScheduleWizard.vue`

**Wizard Steps**:
1. **Select Instructor** → Dropdown with search filter
2. **Set Date & Time** → Date picker + time range inputs with conflict check
3. **Configure Capacity** → Number input (1-50) with validation
4. **Review & Confirm** → Summary of all selections before submission

---

#### Task B5.16: Add Schedule Conflict Visualization ⏱️ ~30 min  
**Priority**: P1 - Important  
**Dependencies**: Task B5.14 Complete  
**Files to Modify**: `frontend/src/views/admin/ScheduleManagement.vue`

**Features**:
- Visual overlap highlighting in calendar view (red background for conflicts)
- Warning tooltips when selecting conflicting time ranges
- Real-time conflict detection during form wizard step 2

---

## 📊 Complete Task Summary

| Phase | Component | Tasks | Est. Time | Status |
|-------|-----------|-------|-----------|--------|
| **5B** | Coach Management Backend | B5.1-B5.4 | ~2h | 📋 Planned |
| **5B** | Coach Management Frontend | B5.5-B5.9 | ~3h | 📋 Planned (partial) |
| **5B** | Schedule Management Backend | B5.10-B5.13 | ~2h | 📋 Planned |  
| **5B** | Schedule Management Frontend | B5.14-B5.16 | ~2h | 📋 Planned |

**Total**: 16 atomic tasks, ~9 hours development time

---

## ✅ Acceptance Criteria (Definition of Done)

### Coach Management:
- [ ] Admin can list all coaches with search/filter/pagination  
- [ ] Admin can create new coach with name/bio/phone/photo
- [ ] Admin can edit any coach's information
- [ ] Admin can soft-delete coaches (prevents deletion if has active schedules)
- [ ] Form validation prevents invalid data submission

### Schedule Management:
- [ ] Admin can view all schedules in calendar or list format
- [ ] Admin can filter by date range and instructor  
- [ ] Admin can create new class with conflict detection
- [ ] Admin can edit schedule times (re-checks for conflicts)
- [ ] Admin cannot reduce capacity below existing booking count
- [ ] Schedule deletion requires explicit confirmation if has bookings

---

*Document maintained by: Rogers (AI Assistant)*  
*Last Updated: 2026-04-15 10:40 GMT+8*  
*Next Action: Begin implementation of Task B5.1 or await user approval*