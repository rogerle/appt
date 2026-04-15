# Phase 6B - Admin Dashboard & Management Features
## 🎯 阶段目标

为管理员提供完整的后台管理系统，包括：
- **仪表盘** - 关键指标概览（预约数、教练状态、收入统计）
- **教练管理** - CRUD 操作、状态控制、信息编辑
- **排课管理** - 创建/编辑课程安排、批量导入
- **用户管理** - 查看注册用户、角色分配

---

## 📋 原子级任务分解

### Task 1: Dashboard Backend API (30 mins)
**文件**: `backend/app/api/v1/admin/dashboard.py`

#### Subtasks:
1.1 Create FastAPI router with `/admin/dashboard` prefix
```python
router = APIRouter(prefix="/dashboard", tags=["Admin - Dashboard"])
```

1.2 Implement GET /stats endpoint
- Query: Total bookings (today/this week/month)
- Query: Active instructors count
- Query: Available schedule slots
- Return: `DashboardStats` Pydantic model

1.3 Implement GET /recent-bookings endpoint  
- Query: Latest 10 bookings with customer info
- Include: Booking status, instructor name, date/time
- Parameters: limit (default=10), offset (for pagination)

1.4 Create DashboardStats schema in `app/schemas/admin.py`
```python
class DashboardStats(BaseModel):
    total_bookings_today: int
    total_bookings_week: int
    active_instructors: int
    available_slots: int
    revenue_this_month: float  # Optional, for future payment integration
```

1.5 Add route to `app/api/v1/admin/__init__.py`

---

### Task 2: Dashboard Frontend Component (45 mins)
**文件**: `frontend/src/views/admin/Dashboard.vue`

#### Subtasks:
2.1 Create dashboard layout with grid cards
- Stats Cards Grid (4 columns): Today's Bookings, Weekly Bookings, Active Instructors, Available Slots

2.2 Implement stats card component (`src/components/admin/StatsCard.vue`)
```vue
<template>
  <div class="stats-card">
    <div class="icon">{{ props.icon }}</div>
    <div class="content">
      <h3>{{ props.title }}</h3>
      <p class="value">{{ props.value }}</p>
    </div>
  </div>
</template>
```

2.3 Add recent bookings table section
- Columns: Time, Customer Name, Phone (masked), Instructor, Class Type, Status, Actions
- Status badges with color coding (confirmed=green, cancelled=red)
- "View Details" button on each row

2.4 Implement data fetching in setup()
```typescript
const { stats, recentBookings } = storeToRefs(useAdminStore())
onMounted(() => fetchDashboardData())
```

2.5 Add refresh button with auto-refresh every 30 seconds (optional)

---

### Task 3: Instructor CRUD Backend API (45 mins)
**文件**: `backend/app/api/v1/admin/instructors.py`

#### Subtasks:
3.1 Create FastAPI router with `/admin/instructors` prefix

3.2 Implement GET /instructors (list all)
- Query parameters: search (name), status (active/inactive), studio_id
- Return: List of `InstructorResponse` with pagination metadata

3.3 Implement POST /instructors (create new)
- Request body: `InstructorCreate` schema
- Fields: name, phone, studio_name, bio, experience_years, specialties[]
- Validation: Unique phone number per studio
- Return: Created instructor with ID

3.4 Implement GET /instructors/{id} (get single)
- Return: Full instructor details including schedules count

3.5 Implement PUT /instructors/{id} (update)
- Request body: `InstructorUpdate` schema (all fields optional)
- Support partial updates (PATCH behavior)
- Special handling for status toggle (activate/deactivate)

3.6 Implement DELETE /instructors/{id} (soft delete)
- Set `is_active = False` instead of physical deletion
- Check: Cannot delete if has active schedules or confirmed bookings

3.7 Create schemas in `app/schemas/admin.py`:
```python
class InstructorCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., pattern=r'^1[3-9]\d{9}$')
    studio_name: str = Field(..., min_length=2, max_length=200)
    bio: Optional[str] = Field(None, max_length=1000)
    experience_years: int = Field(0, ge=0, le=50)
    specialties: List[str] = []

class InstructorUpdate(BaseModel):
    # All optional fields from InstructorCreate + status toggle
```

3.8 Add route to `app/api/v1/admin/__init__.py`

---

### Task 4: Instructor Management Frontend (60 mins)
**文件**: `frontend/src/views/admin/InstructorManagement.vue`

#### Subtasks:
4.1 Create page layout with tabs or sections:
- Tab 1: All Instructors (table view)
- Tab 2: Add New Instructor (form)

4.2 Implement instructors table component (`src/components/admin/InstructorTable.vue`)
```vue
<template>
  <div class="table-container">
    <!-- Search & Filter Toolbar -->
    <div class="toolbar">
      <input v-model="searchQuery" placeholder="搜索教练..." />
      <select v-model="statusFilter">...</select>
      <button @click="$emit('refresh')">刷新</button>
    </div>

    <!-- Table -->
    <table>
      <thead>
        <tr><th>姓名</th><th>电话</th><th>擅长领域</th><th>状态</th><th>操作</th></tr>
      </thead>
      <tbody>...</tbody>
    </table>

    <!-- Pagination -->
  </div>
</template>
```

4.3 Implement instructor form component (`src/components/admin/InstructorForm.vue`)
- Fields: Name (text), Phone (tel with validation), Studio (text)
- Optional: Bio (textarea), Experience (number input), Specialties (multi-select/tags input)
- Form validation with Vuelidate or vee-validate
- Submit button with loading state

4.4 Create instructor store (`src/stores/admin.ts`)
```typescript
export const useAdminStore = defineStore('admin', {
  state: () => ({
    instructors: [],
    dashboardStats: null,
    // ... other admin data
  }),
  actions: {
    async fetchInstructors(filters) { /* ... */ },
    async createInstructor(data) { /* ... */ },
    async updateInstructor(id, data) { /* ... */ },
    async deleteInstructor(id) { /* ... */ }
  }
})
```

4.5 Add "Edit" modal dialog (reuse InstructorForm with pre-filled data)

4.6 Implement status toggle button (active/inactive switch with confirmation)

---

### Task 5: Schedule CRUD Backend API (45 mins)
**文件**: `backend/app/api/v1/admin/schedules.py`

#### Subtasks:
5.1 Create FastAPI router with `/admin/schedules` prefix

5.2 Implement GET /schedules (list all)
- Query parameters: instructor_id, date_from, date_to, status (available/occupied)
- Return: Paginated list of schedules with booking count

5.3 Implement POST /schedules (create single)
- Request body: `ScheduleCreate` schema
- Fields: instructor_id, date, start_time, end_time, class_type, max_participants
- Validation: Time range check (end > start), no overlapping schedules for same instructor

5.4 Implement POST /schedules/bulk (bulk create)
- Request body: Array of `ScheduleCreate` objects
- Use database transaction for atomicity
- Return: Count of created/failed with error details per item

5.5 Implement GET /schedules/{id} (get single)
- Include related instructor and bookings info

5.6 Implement PUT /schedules/{id} (update)
- Request body: `ScheduleUpdate` schema (all fields optional except ID)
- Validation: Cannot modify if has confirmed bookings (or require migration prompt)

5.7 Implement DELETE /schedules/{id} (delete)
- Check: Cannot delete if has confirmed bookings
- Cascade: Cancel pending bookings with notification (future feature)

5.8 Create schemas in `app/schemas/admin.py`:
```python
class ScheduleCreate(BaseModel):
    instructor_id: int
    date: date = Field(..., description="YYYY-MM-DD")
    start_time: time = Field(...)
    end_time: time = Field(...)
    class_type: str = Field(..., min_length=1, max_length=50)  # e.g., "哈他瑜伽", "流瑜伽"
    max_participants: int = Field(10, ge=1, le=50)

class ScheduleUpdate(BaseModel):
    start_time: Optional[time]
    end_time: Optional[time]
    class_type: Optional[str]
    max_participants: Optional[int]
```

5.9 Add route to `app/api/v1/admin/__init__.py`

---

### Task 6: Schedule Management Frontend (60 mins)
**文件**: `frontend/src/views/admin/ScheduleManagement.vue`

#### Subtasks:
6.1 Create page layout with calendar + list views toggle

6.2 Implement schedule calendar component (`src/components/admin/ScheduleCalendar.vue`)
- Month view with time slots grid
- Color coding by class type or status (available=green, full=red)
- Click on slot to create/edit schedule

6.3 Implement schedule list view (`src/components/admin/ScheduleList.vue`)
- Table columns: Date, Time Range, Instructor, Class Type, Capacity, Bookings/Max, Status, Actions
- Sortable columns (click header to sort)
- Filters: Date range picker, instructor dropdown, status filter

6.4 Create schedule form modal (`src/components/admin/ScheduleModal.vue`)
- Form fields: Instructor (dropdown), Date (date picker), Start Time, End Time
- Advanced: Class Type (text/select), Max Participants (number)
- Validation: Time range logic, overlap detection with visual feedback

6.5 Implement bulk import feature
- Upload CSV file with columns: instructor_name,date,start_time,end_time,class_type,max_participants
- Preview before committing
- Show import results (success count, error details per row)

6.6 Add "Quick Actions" toolbar:
- Generate weekly schedule template (button → creates 7 days of slots for all active instructors)
- Clear old schedules (>30 days in past with no bookings)

---

### Task 7: User Management Backend API (30 mins)
**文件**: `backend/app/api/v1/admin/users.py`

#### Subtasks:
7.1 Create FastAPI router with `/admin/users` prefix (requires admin role)

7.2 Implement GET /users (list all registered users)
- Query parameters: search (email/username), role filter, is_active filter
- Return: Paginated list of `UserResponse` (exclude password hash!)

7.3 Implement GET /users/{id} (get single user)
- Include: User info + booking count + last login timestamp

7.4 Implement PUT /users/{id}/role (change role)
- Request body: `{ "role": "user" | "admin" }`
- Only admins can change roles
- Audit log entry (future feature)

7.5 Implement PUT /users/{id}/status (activate/deactivate)
- Request body: `{ "is_active": true/false }`
- Prevent self-deactivation (cannot disable your own account)

7.6 Create schemas in `app/schemas/admin.py`:
```python
class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    role: UserRole
    is_active: bool
    created_at: datetime
    last_login_at: Optional[datetime]
    booking_count: int  # Denormalized for performance

class RoleUpdate(BaseModel):
    role: UserRole

class StatusUpdate(BaseModel):
    is_active: bool
```

7.7 Add route to `app/api/v1/admin/__init__.py`

---

### Task 8: User Management Frontend (45 mins)
**文件**: `frontend/src/views/admin/UserManagement.vue`

#### Subtasks:
8.1 Create user table component (`src/components/admin/UserTable.vue`)
- Columns: ID, Email, Username, Role, Status, Last Login, Bookings, Actions
- Role badges (admin=blue, user=gray)
- Status toggles with confirmation

8.2 Implement role change modal
- Dropdown to select new role
- Warning message when promoting to admin ("Only give admin access to trusted users")

8.3 Add search and filter controls:
- Search by email/username (debounced input)
- Filter by role (checkbox group)
- Filter by status (active/inactive tabs)

8.4 Implement user detail view (modal or separate route)
- Show full user profile
- Display recent bookings list
- Action buttons: Change Role, Deactivate, Reset Password (future)

---

### Task 9: Integration & Testing (60 mins)

#### Subtasks:
9.1 Verify all admin routes are protected with `@router.get()` + dependency injection
```python
@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(user: User = Depends(get_current_admin_user)):
    # Only admins can access!
```

9.2 Test frontend router guards prevent non-admin users from accessing /admin/* routes

9.3 E2E test scenarios (manual or automated):
- Scenario 1: Admin login → view dashboard → add instructor → create schedule → see stats update
- Scenario 2: Regular user tries to access /admin/dashboard → redirected to homepage with alert
- Scenario 3: Create instructor via form → appears in table immediately (no refresh needed)

9.4 Performance testing:
- Load test GET /instructors with 1000+ records (pagination works?)
- Test bulk schedule import with 500 rows CSV file

9.5 Fix any bugs found during testing and update documentation

---

### Task 10: Polish & Documentation (30 mins)

#### Subtasks:
10.1 Add loading states to all async operations (spinners, skeleton screens)

10.2 Implement error handling UI:
- Global error toast notifications (use Vue Toastification or similar)
- Form field-level errors with inline validation messages
- 403 Forbidden page for unauthorized access attempts

10.3 Add confirmation dialogs for destructive actions:
```typescript
async function deleteInstructor(id: number): Promise<void> {
  if (!confirm('确定要停用此教练吗？这将隐藏其所有课程安排。')) return
  await adminStore.deleteInstructor(id)
}
```

10.4 Update `docs/ADMIN_GUIDE.md` with usage instructions for each feature

10.5 Create `docs/API_ADMIN.md` documenting all admin endpoints (Swagger should auto-generate)

---

## 📊 Estimated Timeline

| Task | Duration | Dependencies |
|------|----------|--------------|
| Task 1: Dashboard Backend API | 30 mins | None |
| Task 2: Dashboard Frontend | 45 mins | Task 1 |
| Task 3: Instructor CRUD Backend | 45 mins | None (parallel with Task 2) |
| Task 4: Instructor Management Frontend | 60 mins | Task 3 |
| Task 5: Schedule CRUD Backend | 45 mins | Task 3 complete (reuse patterns) |
| Task 6: Schedule Management Frontend | 60 mins | Task 5 |
| Task 7: User Management Backend | 30 mins | None (parallel with earlier tasks) |
| Task 8: User Management Frontend | 45 mins | Task 7 |
| Task 9: Integration & Testing | 60 mins | All above complete |
| Task 10: Polish & Documentation | 30 mins | Task 9 complete |

**Total Estimated Time**: ~6.25 hours (can be parallelized to ~4 hours)

---

## 🎯 Success Criteria

Phase 6B is considered **complete** when all of the following are true:
- [ ] Dashboard shows accurate real-time stats from database queries
- [ ] Admin can create, view, edit, and deactivate instructors via UI
- [ ] Admin can create single or bulk schedules with conflict detection  
- [ ] Admin can view all users, change roles, and manage account status
- [ ] All admin routes are protected (non-admin users get 403 redirect)
- [ ] Forms have proper validation with user-friendly error messages
- [ ] UI provides visual feedback for loading states and async operations
- [ ] Documentation covers all new features with screenshots/examples

---

## 📝 Notes & Decisions

### Technical Decisions Made:
1. **Soft Delete Pattern**: Instructors/users marked as `is_active=False` instead of physical deletion to preserve audit trail
2. **Role-Based Access Control (RBAC)**: Simple two-tier system (user/admin), easily extensible to more roles later
3. **API Response Standardization**: All list endpoints return paginated results with metadata `{ items, total, page, pageSize }`
4. **Frontend State Management**: Centralized admin store in Pinia for consistent data fetching and caching

### Future Enhancements (Not in Phase 6B):
- Advanced analytics (charts/graphs for booking trends)
- Email notifications to customers when schedules change
- Export reports to PDF/Excel
- Multi-studio support (filter by studio_id across all features)
- Audit logging for all admin actions

---

*Created: 2026-04-15 | Author: Rogers (AI Product Manager)*
