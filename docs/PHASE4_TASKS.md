# Phase 4: API Integration Task Breakdown

**目标**: 将前端 UI 组件与后端 API 完全连接，实现完整的预约流程

---

## 🎯 Phase 4 任务清单 (原子级)

### **P4-01**: 创建示例数据种子脚本 (~15min)
**文件**: `backend/scripts/seed_data.py`  
**功能**: 
- 插入示例教练数据 (张伟，李娜，王强)
- 插入示例排课数据 (未来 7 天的课程时段)
- 为测试提供真实数据

---

### **P4-02**: 执行数据库种子数据 (~5min)  
**命令**: `python scripts/seed_data.py`  
**验证**: 
```sql
SELECT * FROM instructor; -- Should show 3 coaches
SELECT * FROM schedule WHERE date >= CURRENT_DATE; -- Should show upcoming slots
```

---

### **P4-03**: 更新 Instructors API - GET all with filters (~20min)
**文件**: `backend/app/api/v1/instructors.py`  
**修改**: 
- Add query parameters: `date`, `studio_id`, `is_active`
- Filter schedules by date to show only available instructors
- Calculate available slot count for each instructor

---

### **P4-04**: 更新 Schedules API - GET available slots (~25min)  
**文件**: `backend/app/api/v1/schedules.py`  
**新增端点**: 
```python
GET /api/v1/schedules/available?date=YYYY-MM-DD&instructor_id=X
# Returns: List of time slots with availability status
```

---

### **P4-05**: 更新 Bookings API - POST create booking (~30min)  
**文件**: `backend/app/api/v1/bookings.py`  
**修改**: 
- Add conflict detection logic (check if slot is already booked)
- Validate customer phone format
- Return detailed error messages for conflicts

---

### **P4-06**: 更新 Frontend API Client - Add new methods (~20min)  
**文件**: `frontend/src/api/client.ts`  
**新增方法**: 
```typescript
export const bookingApi = {
  createBooking(data: BookingData): Promise<BookingResponse>
  getMyBookings(phone: string): Promise<Booking[]>
  cancelBooking(bookingId: number): Promise<void>
}

export const instructorApi = {
  getAll(date?: string): Promise<Instructor[]>
  getAvailableSlots(instructorId: number, date: string): Promise<TimeSlot[]>
}
```

---

### **P4-07**: 连接 BookingPage - Load Instructors (~30min)  
**文件**: `frontend/src/views/BookingPage.vue`  
**修改**: 
- Replace placeholder instructor data with API call
- Add loading state while fetching
- Handle empty state (no instructors available)

---

### **P4-08**: 连接 BookingPage - Load Time Slots (~30min)  
**文件**: `frontend/src/views/BookingPage.vue`  
**修改**: 
- Call `/schedules/available` when instructor selected
- Display real-time availability status
- Show booked count for each slot

---

### **P4-09**: 连接 BookingForm - Submit to API (~35min)  
**文件**: `frontend/src/components/BookingForm.vue` + `BookingPage.vue`  
**修改**: 
- POST booking data to `/bookings/` endpoint
- Handle success (show confirmation, redirect to /my-bookings)
- Handle errors (conflict, validation, network issues)

---

### **P4-10**: 更新 MyBookings Page - Display user bookings (~25min)  
**文件**: `frontend/src/views/MyBookings.vue`  
**修改**: 
- Fetch user's bookings by phone number
- Display booking cards with status badges
- Add cancel button for upcoming bookings

---

### **P4-11**: 添加 Loading States & Error Boundaries (~20min)  
**文件**: Multiple Vue components  
**功能**: 
- Skeleton loaders for async data
- Error message toast notifications
- Retry mechanism for failed requests

---

### **P4-12**: E2E Test - Complete Booking Flow (~30min)  
**步骤**: 
1. 访问首页 → 点击 "立即预约"
2. 选择日期 → 加载教练列表
3. 选择教练 → 加载可用时段
4. 选择时段 → 填写表单
5. 提交 → 验证成功消息
6. 查看 /my-bookings → 确认记录存在

---

### **P4-13**: Update Documentation (~15min)  
**文件**: `docs/PHASE4_REPORT.md`  
**内容**: 
- Integration architecture diagram
- API endpoint usage examples
- Known limitations and future improvements

---

## 📊 Phase 4 预估总耗时

| Category | Tasks | Estimated Time |
|----------|-------|----------------|
| **Backend API Enhancements** | P4-03 ~ P4-05 | ~75 min (1.25h) |
| **Frontend Integration** | P4-06 ~ P4-10 | ~140 min (2.3h) |
| **UX Improvements** | P4-11 | ~20 min |
| **Testing & Docs** | P4-12, P4-13 | ~45 min |
| **Seed Data Setup** | P4-01, P4-02 | ~20 min |

**总计**: ~3.7 小时 (约 4 小时含缓冲时间)

---

## 🚀 Execution Strategy

### Phase A: Backend Preparation (~90min)
1. ✅ **P4-01**: Create seed script
2. ✅ **P4-02**: Execute and verify data  
3. ⏳ **P4-03**: Enhance Instructors API
4. ⏳ **P4-04**: Add Available Slots endpoint
5. ⏳ **P4-05**: Improve Bookings conflict detection

### Phase B: Frontend Integration (~160min)  
6. ⏳ **P4-06**: Update API client methods
7. ⏳ **P4-07**: Connect instructor loading
8. ⏳ **P4-08**: Connect time slot loading
9. ⏳ **P4-09**: Implement booking submission
10. ⏳ **P4-10**: Display user bookings

### Phase C: Polish & Test (~65min)  
11. ⏳ **P4-11**: Add loading/error states
12. ⏳ **P4-12**: Complete E2E flow test
13. ⏳ **P4-13**: Update documentation

---

## 📝 Success Criteria

### Functional Requirements:
- [ ] User can see real instructors (not placeholders)
- [ ] Time slots show actual availability from database  
- [ ] Booking submission creates record in PostgreSQL
- [ ] Conflict detection prevents double-booking
- [ ] My Bookings page shows user's reservations

### Non-Functional Requirements:
- [ ] All API calls have loading indicators
- [ ] Error messages are clear and actionable
- [ ] Average response time < 300ms
- [ ] No console errors in browser dev tools

---

*Created: 2026-04-13 21:25 GMT+8*  
*Next Action: Begin executing P4-01 ~ P4-05 (Backend Preparation)*
