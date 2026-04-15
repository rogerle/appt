# 👨‍🏫 Phase 5B: Admin Features - Atomic Task Breakdown

**Project**: Appt - Yoga Studio Booking System  
**Phase**: Phase 5B - Coach Management & Schedule Management  
**Status**: 📋 Planning Stage  
**Created**: 2026-04-15  
**Owner**: Rogers (AI Assistant)  

---

## 🎯 Phase Goals

实现完整的管理后台功能：
- **教练管理**：CRUD 操作（增删改查）、状态控制、搜索过滤
- **排课管理**：课程创建/编辑/删除、时间冲突检测、容量设置

---

## 📊 Task Overview (16 Atomic Tasks)

| Category | Subcategory | Task Count | Est. Time | Priority |
|----------|-------------|------------|-----------|----------|
| **Coach Management** | Backend API | 4 tasks | ~2h | P0:3, P1:1 |
| **Coach Management** | Frontend UI | 5 tasks | ~2.5h | P0:3, P1:2 |
| **Schedule Management** | Backend API | 4 tasks | ~2h | P0:3, P1:1 |
| **Schedule Management** | Frontend UI | 3 tasks | ~2h | P0:2, P1:1 |

**Total**: 16 tasks, ~8.5 hours development time

---

## 🗺️ Implementation Roadmap

```
Week 1 - Coach Management (4.5h):
├─ Backend: Tasks B5.1-B5.4 (~2h)
│   ├─ List/Get/Create/Delete APIs
│   └─ Validation + Business Logic
│
└─ Frontend: Tasks B5.5-B5.9 (~2.5h)
    ├─ Table View + Search Filters
    ├─ Create/Edit Modal Forms  
    └─ Delete Confirmation

Week 1 - Schedule Management (4h):
├─ Backend: Tasks B5.10-B5.13 (~2h)
│   ├─ CRUD APIs with Conflict Detection
│   └─ Capacity Validation
│
└─ Frontend: Tasks B5.14-B5.16 (~2h)
    ├─ Calendar View + List Toggle
    └─ Form Wizard (Multi-step)
```

---

## 🔨 PART 1: Coach Management (教练管理) - 9 Atomic Tasks

### **Backend Tasks (4 tasks)**

#### Task B5.1: Update Instructor API - GET All with Filters ⏱️ ~25 min
**Priority**: P0 - Critical Path  
**Dependencies**: None  
**Files to Modify**: `backend/app/api/v1/instructors.py`

**Acceptance Criteria**:
```python
# Current endpoint (returns all instructors):
@router.get("/")
async def get_instructors(db: Session = Depends(get_db)):
    # ... existing code ...

# AFTER - Add filtering and pagination:
from typing import Optional

@router.get("/", response_model=list[InstructorResponse])
async def get_instructors(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Page offset"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by name or bio"),
    is_active: Optional[bool] = Query(None, description="Filter by active status")
):
    """
    Get instructors with filtering and pagination.
    
    Query params:
      - skip: Page offset (default 0)
      - limit: Items per page (1-100, default 20)
      - search: Search term for name/bio matching  
      - is_active: Filter active/inactive instructors
    
    Returns paginated list with instructor details including schedule counts.
    """
    
    # Build base query
    query = db.query(Instructor).filter(Instructor.studio_id == 1)  # Single studio
    
    # Apply search filter (if provided)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Instructor.name.ilike(search_pattern)) | 
            (Instructor.bio.ilike(search_pattern))
        )
    
    # Apply status filter (if provided)
    if is_active is not None:
        query = query.filter(Instructor.is_active == is_active)
    
    # Count total for pagination metadata
    total = query.count()
    
    # Apply pagination and sort by creation date
    instructors = query.offset(skip).limit(limit).order_by(Instructor.created_at.desc()).all()
    
    # Build response with eager loading of schedules
    from sqlalchemy.orm import joinedload
    instructor_data = []
    
    for instructor in instructors:
        # Count available schedules
        schedule_count = db.query(Schedule).filter(
            Schedule.instructor_id == instructor.id,
            Schedule.is_active == True
        ).count()
        
        instructor_data.append(InstructorResponse(
            id=instructor.id,
            name=instructor.name,
            bio=instructor.bio or "",
            phone=instructor.phone or "",
            photo_url=instructor.photo_url or "",
            is_active=bool(instructor.is_active),
            total_schedules=schedule_count,
            created_at=instructor.created_at.isoformat(),
            updated_at=instructor.updated_at.isoformat()
        ))
    
    return instructor_data

# Response schema update needed (add pagination fields)
```

**API Contract**:
- `GET /api/v1/instructors` → Returns list of instructors  
- `GET /api/v1/instructors?search=张&is_active=true&page=1&limit=20` → Filtered + paginated results
- Response: `{data: [...], total: 45, page: 1, limit: 20}`

**Testing**:
- [ ] Search by name returns matching instructors (case-insensitive)
- [ ] Pagination works correctly (skip=0,limit=5 returns first 5 items)
- [ ] is_active filter shows only active/inactive as requested
- [ ] Total count accurate for pagination UI

---

#### Task B5.2: Update Instructor API - GET by ID ⏱️ ~15 min  
**Priority**: P0 - Critical Path  
**Dependencies**: None (can run in parallel with B5.1)  
**Files to Modify**: `backend/app/api/v1/instructors.py`

**Acceptance Criteria**:
```python
# Current endpoint:
@router.get("/{instructor_id}")
async def get_instructor(instructor_id: int, db: Session = Depends(get_db)):
    instructor = db.query(Instructor).filter(
        Instructor.id == instructor_id, 
        Instructor.studio_id == 1
    ).first()
    
    if not instructor:
        raise HTTPException(status_code=404, detail="Instructor not found")
    
    return {
        "id": instructor.id,
        "name": instructor.name,
        "description": instructor.bio or ""
    }

# AFTER - Enhanced response with full details:
@router.get("/{instructor_id}", response_model=InstructorDetailResponse)
async def get_instructor(instructor_id: int, db: Session = Depends(get_db)):
    """Get single instructor with complete details including all schedules."""
    
    from sqlalchemy.orm import joinedload
    
    instructor = db.query(Instructor).options(
        joinedload(Instructor.schedules)
    ).filter(
        Instructor.id == instructor_id, 
        Instructor.studio_id == 1
    ).first()
    
    if not instructor:
        raise HTTPException(status_code=404, detail="教练不存在")
    
    # Build detailed response
    return InstructorDetailResponse(
        id=instructor.id,
        name=instructor.name,
        bio=instructor.bio or "",
        phone=instructor.phone or "",
        photo_url=instructor.photo_url or "",
        is_active=bool(instructor.is_active),
        schedules=[  # Include all schedules for this instructor
            ScheduleResponse(
                id=s.id,
                date=s.date.isoformat(),
                start_time=s.start_time.strftime("%H:%M"),
                end_time=s.end_time.strftime("%H:%M"),
                capacity=s.capacity,
                available_spots=s.available_spots,
                is_active=bool(s.is_active)
            ) for s in instructor.schedules if s.is_active
        ],
        created_at=instructor.created_at.isoformat(),
        updated_at=instructor.updated_at.isoformat()
    )

# Add new response schema to schemas/instructor.py:
class InstructorDetailResponse(InstructorResponse):
    schedules: list[ScheduleResponse] = []
```

**API Contract**:
- `GET /api/v1/instructors/{id}` → Returns full instructor details with nested schedules
- Returns HTTP 404 if not found

**Testing**:
- [ ] Valid ID returns complete instructor data including all active schedules
- [ ] Invalid ID returns 404 error with clear message
- [ ] Schedules are properly formatted (date, time, capacity)

---

#### Task B5.3: Create Instructor API - POST ⏱️ ~35 min  
**Priority**: P0 - Critical Path  
**Dependencies**: None  
**Files to Modify**: `backend/app/api/v1/instructors.py`, `backend/app/schemas/instructor.py`

**Acceptance Criteria**:
```python
# Add create schema (if not exists):
class InstructorCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="教练姓名")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")
    phone: Optional[str] = Field(None, pattern=r'^1[3-9]\d{9}$', description="手机号（可选）")
    photo_url: Optional[str] = Field(None, description="头像 URL（可选）")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "张伟",
                "bio": "资深瑜伽教练，8 年教学经验，擅长流瑜伽和阴瑜伽",
                "phone": "13800138000"
            }
        }

# Add create endpoint:
@router.post("/", response_model=InstructorResponse, status_code=status.HTTP_201_CREATED)
async def create_instructor(
    instructor_data: InstructorCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # Admin only!
):
    """
    Create new instructor (admin only).
    
    Validates:
      - Name uniqueness within studio
      - Phone number format (if provided)
      - Bio length constraints
    
    Returns created instructor with generated ID.
    """
    
    # Check for duplicate name
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
        bio=instructor_data.bio,
        phone=instructor_data.phone,
        photo_url=instructor_data.photo_url,
        is_active=True,  # Default to active
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(db_instructor)
    db.commit()
    db.refresh(db_instructor)
    
    # Build response
    return InstructorResponse(
        id=db_instructor.id,
        name=db_instructor.name,
        bio=db_instructor.bio or "",
        phone=db_instructor.phone or "",
        photo_url=db_instructor.photo_url or "",
        is_active=True,
        total_schedules=0,  # New instructor has no schedules yet
        created_at=db_instructor.created_at.isoformat(),
        updated_at=db_instructor.updated_at.isoformat()
    )
```

**API Contract**:
- `POST /api/v1/instructors` → Create new instructor (requires admin JWT token)
- Request body: `{name, bio?, phone?, photo_url?}`
- Response: HTTP 201 + created instructor object with ID
- Errors: 
  - 409 Conflict if name already exists
  - 422 Validation error for invalid data format

**Testing**:
- [ ] Valid request creates instructor and returns 201 status
- [ ] Duplicate name rejected with clear error message
- [ ] Invalid phone number format rejected (must be 11 digits starting with 1)
- [ ] Bio field accepts null/empty string
- [ ] New instructor has is_active=true by default

---

#### Task B5.4: Update Instructor API - PUT/PATCH and DELETE ⏱️ ~30 min  
**Priority**: P1 - Important  
**Dependencies**: Task B5.2 Complete (need GET logic)  
**Files to Modify**: `backend/app/api/v1/instructors.py`, `backend/app/schemas/instructor.py`

**Acceptance Criteria**:
```python
# Add update schema:
class InstructorUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    phone: Optional[str] = Field(None, pattern=r'^1[3-9]\d{9}$')
    photo_url: Optional[str] = Field(None)
    is_active: Optional[bool] = Field(None)  # Toggle active status

# Update endpoint (PATCH - partial update):
@router.patch("/{instructor_id}", response_model=InstructorResponse)
async def update_instructor(
    instructor_id: int, 
    updates: InstructorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # Admin only!
):
    """
    Update instructor information (partial update - only provided fields changed).
    
    Validates updates and checks for duplicate names.
    Returns updated instructor object.
    """
    
    # Find instructor
    instructor = db.query(Instructor).filter(
        Instructor.id == instructor_id, 
        Instructor.studio_id == 1
    ).first()
    
    if not instructor:
        raise HTTPException(status_code=404, detail="教练不存在")
    
    # Check for name conflict (if name is being updated)
    if updates.name and updates.name != instructor.name:
        existing = db.query(Instructor).filter(
            Instructor.name == updates.name,
            Instructor.id != instructor_id,  # Exclude current record
            Instructor.studio_id == 1
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail="新姓名已被其他教练使用"
            )
    
    # Update provided fields only (partial update)
    update_data = updates.dict(exclude_unset=True)  # Only include changed fields
    
    for field, value in update_data.items():
        setattr(instructor, field, value)
    
    instructor.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(instructor)
    
    # Build response with schedule count
    schedule_count = db.query(Schedule).filter(
        Schedule.instructor_id == instructor.id,
        Schedule.is_active == True
    ).count()
    
    return InstructorResponse(
        id=instructor.id,
        name=instructor.name,
        bio=instructor.bio or "",
        phone=instructor.phone or "",
        photo_url=instructor.photo_url or "",
        is_active=bool(instructor.is_active),
        total_schedules=schedule_count,
        created_at=instructor.created_at.isoformat(),
        updated_at=instructor.updated_at.isoformat()
    )

# Delete endpoint (soft delete - set is_active=false):
@router.delete("/{instructor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_instructor(
    instructor_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # Admin only!
):
    """
    Soft delete instructor (set is_active=false).
    
    Does not physically delete record to preserve booking history.
    Returns 204 No Content on success.
    """
    
    # Find instructor
    instructor = db.query(Instructor).filter(
        Instructor.id == instructor_id, 
        Instructor.studio_id == 1
    ).first()
    
    if not instructor:
        raise HTTPException(status_code=404, detail="教练不存在")
    
    # Check if has active schedules (prevent deletion with existing classes)
    active_schedule_count = db.query(Schedule).filter(
        Schedule.instructor_id == instructor.id,
        Schedule.is_active == True
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

# Hard delete endpoint (admin override - optional):
@router.delete("/{instructor_id}/hard", status_code=status.HTTP_204_NO_CONTENT)
async def hard_delete_instructor(
    instructor_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Permanently delete instructor (admin override).
    
    WARNING: This will also delete all associated schedules and bookings!
    Use with extreme caution. Requires explicit confirmation token.
    """
    
    # Find instructor
    instructor = db.query(Instructor).filter(
        Instructor.id == instructor_id, 
        Instructor.studio_id == 1
    ).first()
    
    if not instructor:
        raise HTTPException(status_code=404, detail="教练不存在")
    
    # Delete associated schedules first (cascade)
    db.query(Schedule).filter(Schedule.instructor_id == instructor.id).delete()
    
    # Delete instructor record
    db.delete(instructor)
    db.commit()
    
    return None  # 204 No Content
```

**API Contract**:
- `PATCH /api/v1/instructors/{id}` → Partial update (only change provided fields)
- `DELETE /api/v1/instructors/{id}` → Soft delete (set is_active=false, prevents deletion if has active schedules)
- `DELETE /api/v1/instructors/{id}/hard` → Hard delete (removes record and all associated data - use cautiously!)

**Testing**:
- [ ] PATCH with partial fields only updates those fields, leaves others unchanged
- [ ] Name update validates uniqueness across other instructors
- [ ] Soft delete prevents deletion if instructor has active schedules (409 error)
- [ ] Soft delete sets is_active=false but preserves record in database
- [ ] Hard delete removes instructor AND all associated schedules/bookings

---

### **Frontend Tasks (5 tasks)**

#### Task B5.5: Create Coach Management Page - Table View ⏱️ ~40 min  
**Priority**: P0 - Critical Path  
**Dependencies**: Tasks B5.1, B5.2 Complete (API ready)  
**Files to Modify**: `frontend/src/views/admin/InstructorManagement.vue`

**Acceptance Criteria**:
```vue
<template>
  <div class="admin-page min-h-screen bg-gray-50">
    <!-- Page Header -->
    <div class="bg-white shadow-sm border-b px-6 py-4">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-800">👨‍🏫 教练管理</h1>
          <p class="text-sm text-gray-500 mt-1">管理系统中的所有瑜伽教练</p>
        </div>
        <button 
          @click="openCreateModal"
          class="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition flex items-center gap-2"
        >
          <span>➕</span> 添加教练
        </button>
      </div>
    </div>

    <!-- Search & Filters -->
    <div class="bg-white border-b px-6 py-4">
      <div class="flex items-center gap-4">
        <!-- Search Box -->
        <div class="flex-1 max-w-md">
          <input 
            v-model="filters.search"
            @keyup.enter="loadInstructors"
            type="text" 
            placeholder="🔍 搜索教练（姓名/简介）..."
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 outline-none"
          />
        </div>

        <!-- Status Filter -->
        <select 
          v-model="filters.is_active"
          @change="loadInstructors"
          class="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 outline-none"
        >
          <option value="">全部状态</option>
          <option value="true">仅显示活跃</option>
          <option value="false">仅显示停用</option>
        </select>

        <!-- Refresh Button -->
        <button 
          @click="loadInstructors"
          class="px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200 transition"
        >
          🔄 刷新
        </button>
      </div>
    </div>

    <!-- Data Table -->
    <div class="container mx-auto px-6 py-6">
      
      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-3"></div>
        <p class="text-gray-500">加载中...</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="instructors.length === 0" class="text-center py-12">
        <p class="text-gray-400 text-lg mb-2">暂无教练数据</p>
        <button @click="openCreateModal" class="text-green-600 hover:text-green-700 font-medium">
          添加第一个教练 →
        </button>
      </div>

      <!-- Table Content -->
      <div v-else class="bg-white rounded-lg shadow-sm border overflow-hidden">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">教练信息</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">联系方式</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">课程数</th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
            </tr>
          </thead>
          
          <tbody class="bg-white divide-y divide-gray-200">
            <tr 
              v-for="instructor in instructors" 
              :key="instructor.id"
              class="hover:bg-gray-50 transition"
            >
              <!-- Coach Info -->
              <td class="px-6 py-4">
                <div class="flex items-center">
                  <div class="flex-shrink-0 h-10 w-10">
                    <img 
                      v-if="instructor.photo_url"
                      :src="instructor.photo_url" 
                      :alt="instructor.name"
                      class="h-10 w-10 rounded-full object-cover"
                    />
                    <div 
                      v-else 
                      class="h-10 w-10 rounded-full bg-green-100 flex items-center justify-center text-green-600 font-bold"
                    >
                      {{ instructor.name.charAt(0) }}
                    </div>
                  </div>
                  <div class="ml-4">
                    <p class="text-sm font-medium text-gray-900">{{ instructor.name }}</p>
                    <p class="text-xs text-gray-500 truncate max-w-xs">{{ instructor.bio || '暂无简介' }}</p>
                  </div>
                </div>
              </td>

              <!-- Contact Info -->
              <td class="px-6 py-4">
                <p class="text-sm text-gray-900">{{ instructor.phone || '-' }}</p>
              </td>

              <!-- Schedule Count -->
              <td class="px-6 py-4">
                <span class="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">
                  {{ instructor.total_schedules }} 个课程
                </span>
              </td>

              <!-- Status Badge -->
              <td class="px-6 py-4 text-center">
                <span 
                  :class="{
                    'bg-green-100 text-green-800': instructor.is_active,
                    'bg-red-100 text-red-800': !instructor.is_active
                  }"
                  class="px-3 py-1 rounded-full text-xs font-medium"
                >
                  {{ instructor.is_active ? '活跃' : '已停用' }}
                </span>
              </td>

              <!-- Actions -->
              <td class="px-6 py-4 text-right">
                <button 
                  @click="openEditModal(instructor)"
                  class="text-green-600 hover:text-green-900 mr-3 text-sm font-medium"
                >
                  编辑
                </button>
                <button 
                  v-if="instructor.total_schedules === 0"
                  @click="confirmDelete(instructor)"
                  class="text-red-600 hover:text-red-900 text-sm font-medium"
                >
                  删除
                </button>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Pagination -->
        <div v-if="pagination.total > pagination.limit" class="bg-gray-50 px-6 py-3 border-t flex items-center justify-between">
          <p class="text-sm text-gray-700">
            显示 {{ pagination.from }} - {{ pagination.to }} 条，共 {{ pagination.total }} 条
          </p>
          <div class="flex gap-2">
            <button 
              @click="changePage(currentPage - 1)"
              :disabled="currentPage === 1"
              class="px-3 py-1 border rounded disabled:opacity-50 hover:bg-gray-100"
            >
              ← 上一页
            </button>
            <button 
              @click="changePage(currentPage + 1)"
              :disabled="currentPage >= totalPages"
              class="px-3 py-1 border rounded disabled:opacity-50 hover:bg-gray-100"
            >
              下一页 →
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Modal (implemented in separate task) -->
    <InstructorModal 
      v-if="showModal"
      :instructor="selectedInstructor"
      @close="closeModal"
      @save="handleSave"
    />

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
// ... TypeScript implementation with API calls, state management, modal handling
</script>
```

**UI Features**:
- ✅ Responsive table layout (horizontal scroll on mobile)
- ✅ Search box with enter key support
- ✅ Status filter dropdown (all/active/inactive)
- ✅ Empty state with call-to-action button  
- ✅ Loading spinner during API calls
- ✅ Pagination controls with page info display
- ✅ Avatar display (photo or initial letter in colored circle)
- ✅ Status badges (green=active, red=inactive)

**Testing**:
- [ ] Table displays all instructors from API correctly
- [ ] Search filters results by name/bio (case-insensitive)
- [ ] Pagination navigates through pages smoothly
- [ ] "添加教练" button opens create modal
- [ ] Edit/Delete buttons work for each row
- [ ] Status badges show correct colors

---

#### Task B5.6: Create Instructor Form Modal Component ⏱️ ~45 min  
**Priority**: P0 - Critical Path  
**Dependencies**: Task B5.3, B5.4 Complete (API ready)  
**Files to Create**: `frontend/src/components/admin/InstructorModal.vue`

**Acceptance Criteria**:
```vue
<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div 
      class="bg-white rounded-xl shadow-2xl w-full max-w-lg mx-4"
      @click.stop
    >
      
      <!-- Modal Header -->
      <div class="px-6 py-4 border-b flex items-center justify-between">
        <h3 class="text-xl font-bold text-gray-800">
          {{ isEdit ? '✏️ 编辑教练' : '➕ 添加新教练' }}
        </h3>
        <button 
          @click="$emit('close')"
          class="text-gray-400 hover:text-gray-600 transition"
        >
          ✕
        </button>
      </div>

      <!-- Modal Body (Form) -->
      <form @submit.prevent="handleSubmit" class="px-6 py-5">
        
        <!-- Name Field (Required) -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            教练姓名 <span class="text-red-500">*</span>
          </label>
          <input 
            v-model="form.name"
            type="text" 
            required
            minlength="2"
            maxlength="100"
            placeholder="请输入教练姓名"
            :class="{ 'border-red-500': errors.name }"
            class="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-green-500 outline-none transition"
          />
          <p v-if="errors.name" class="mt-1 text-sm text-red-600">{{ errors.name }}</p>
        </div>

        <!-- Bio Field (Optional) -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">个人简介</label>
          <textarea 
            v-model="form.bio"
            rows="3"
            maxlength="500"
            placeholder="介绍一下教练的专业背景和教学经验..."
            :class="{ 'border-red-500': errors.bio }"
            class="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-green-500 outline-none transition resize-y"
          ></textarea>
          <p v-if="errors.bio" class="mt-1 text-sm text-red-600">{{ errors.bio }}</p>
          <p class="text-xs text-gray-500 text-right">{{ form.bio.length }}/500</p>
        </div>

        <!-- Phone Field (Optional) -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">手机号码</label>
          <input 
            v-model="form.phone"
            type="tel" 
            pattern="^1[3-9]\d{9}$"
            placeholder="11 位手机号（可选）"
            :class="{ 'border-red-500': errors.phone }"
            class="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-green-500 outline-none transition"
          />
          <p v-if="errors.phone" class="mt-1 text-sm text-red-600">{{ errors.phone }}</p>
        </div>

        <!-- Photo URL Field (Optional) -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">头像图片 URL</label>
          <input 
            v-model="form.photo_url"
            type="url" 
            placeholder="https://example.com/avatar.jpg（可选）"
            :class="{ 'border-red-500': errors.photo_url }"
            class="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-green-500 outline-none transition"
          />
          <p v-if="errors.photo_url" class="mt-1 text-sm text-red-600">{{ errors.photo_url }}</p>
          
          <!-- Preview Image -->
          <div v-if="form.photo_url" class="mt-3">
            <img 
              :src="form.photo_url" 
              alt="头像预览"
              class="h-20 w-20 rounded-full object-cover border-2 border-gray-200"
            />
          </div>
        </div>

        <!-- Active Status Toggle (Edit mode only) -->
        <div v-if="isEdit" class="mb-4">
          <label class="flex items-center cursor-pointer">
            <input 
              type="checkbox" 
              v-model="form.is_active"
              class="w-5 h-5 text-green-600 rounded focus:ring-green-500"
            />
            <span class="ml-3 text-sm font-medium text-gray-700">启用该教练</span>
          </label>
        </div>

        <!-- Error Alert -->
        <div v-if="generalError" class="mb-4 bg-red-50 border border-red-200 rounded-lg p-3">
          <p class="text-sm text-red-700">{{ generalError }}</p>
        </div>

      </form>

      <!-- Modal Footer (Actions) -->
      <div class="px-6 py-4 bg-gray-50 border-t flex items-center justify-end gap-3 rounded-b-xl">
        <button 
          type="button"
          @click="$emit('close')"
          :disabled="isSubmitting"
          class="px-5 py-2.5 border border-gray-300 rounded-lg hover:bg-gray-100 disabled:opacity-50 transition"
        >
          取消
        </button>
        <button 
          type="submit"
          @click="handleSubmit"
          :disabled="isSubmitting || !!generalError"
          class="px-5 py-2.5 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition transform hover:-translate-y-0.5"
        >
          {{ isSubmitting ? '保存中...' : (isEdit ? '保存修改' : '创建教练') }}
        </button>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
// ... Form validation logic, API calls for create/update, error handling
</script