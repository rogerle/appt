<template>
  <div class="schedule-management">
    <div class="header">
      <h1>📅 排课管理</h1>
      <button @click="openAddModal" class="btn-primary">➕ 添加课程安排</button>
    </div>

    <!-- Filters -->
    <div class="filters">
      <select v-model="selectedInstructor" @change="fetchSchedules">
        <option value="">全部教练</option>
        <option v-for="inst in instructors" :key="inst.id" :value="inst.id">
          {{ inst.name }} (ID: {{ inst.id }})
        </option>
      </select>

      <input 
        type="date" 
        v-model="startDate" 
        @change="fetchSchedules"
        class="filter-input"
      />
    </div>

    <!-- Loading & Empty States -->
    <div v-if="loading" class="loading-state">⏳ 加载中...</div>
    
    <div v-else-if="schedules.length === 0" class="empty-state">
      📭 暂无课程安排，点击上方按钮添加
    </div>

    <!-- Schedule Table -->
    <div v-else class="table-container">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>教练</th>
            <th>日期</th>
            <th>时间</th>
            <th>最大人数</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="schedule in schedules" :key="schedule.id">
            <td>#{{ schedule.id }}</td>
            <td>{{ getInstructorName(schedule.instructor_id) }}</td>
            <td>{{ formatDate(schedule.date) }}</td>
            <td>{{ formatTimeRange(schedule.start_time, schedule.end_time) }}</td>
            <td>{{ schedule.max_bookings }}人</td>
            <td>
              <span :class="['status-badge', getAvailabilityClass(schedule)]">
                {{ getAvailabilityText(schedule) }}
              </span>
            </td>
            <td class="actions">
              <button @click="editSchedule(schedule)" class="btn-sm">编辑</button>
              <button 
                v-if="canDelete(schedule)" 
                @click="deleteSchedule(schedule)" 
                class="btn-sm btn-danger"
              >删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Add/Edit Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <h2>{{ isEditing ? '编辑课程安排' : '添加新课程安排' }}</h2>
        
        <form @submit.prevent="saveSchedule">
          <div class="form-row">
            <div class="form-group">
              <label>教练 *</label>
              <select v-model.number="formData.instructor_id" required>
                <option value="">请选择教练</option>
                <option v-for="inst in instructors" :key="inst.id" :value="inst.id">
                  {{ inst.name }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label>日期 *</label>
              <input type="date" v-model="formData.schedule_date" required />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>开始时间 *</label>
              <input type="time" v-model="formData.start_time" required />
            </div>

            <div class="form-group">
              <label>结束时间 *</label>
              <input type="time" v-model="formData.end_time" required />
            </div>
          </div>

          <div class="form-group">
            <label>最大预约人数 *</label>
            <input 
              type="number" 
              v-model.number="formData.max_bookings" 
              min="1" 
              max="50" 
              required 
              placeholder="例如：10"
            />
          </div>

          <div class="modal-actions">
            <button type="button" @click="closeModal" class="btn-secondary">取消</button>
            <button type="submit" :disabled="saving" class="btn-primary">
              {{ saving ? '保存中...' : '保存' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import apiClient from '../../api/client'

interface Instructor {
  id: number
  name: string
}

interface Schedule {
  id: number
  instructor_id: number
  date: Date | string
  start_time: any
  end_time: any
  max_bookings: number
  confirmed_bookings_count?: number
}

// State
const schedules = ref<Schedule[]>([])
const instructors = ref<Instructor[]>([])
const loading = ref(false)
const saving = ref(false)
const showModal = ref(false)
const isEditing = ref(false)

// Filters
const selectedInstructor = ref('')
const startDate = ref('')

// Form data
const formData = ref({
  id: null as number | null,
  instructor_id: null as number | null,
  schedule_date: '',
  start_time: '',
  end_time: '',
  max_bookings: 10
})

// Fetch instructors for dropdown
async function fetchInstructors(): Promise<void> {
  try {
    const res = await apiClient.get('/admin/instructors?active_only=true')
    instructors.value = res.data
  } catch (error) {
    console.error('Failed to fetch instructors:', error)
  }
}

// Fetch schedules with filters
async function fetchSchedules(): Promise<void> {
  loading.value = true
  
  try {
    const params: Record<string, any> = {}
    if (selectedInstructor.value) {
      params.instructor_id = selectedInstructor.value
    }
    
    const res = await apiClient.get('/admin/schedules', { params })
    schedules.value = res.data
    
    // Apply date filter client-side
    if (startDate.value) {
      schedules.value = schedules.value.filter(s => 
        s.date >= startDate.value
      )
    }
  } catch (error) {
    console.error('Failed to fetch schedules:', error)
    alert('加载课程安排失败')
  } finally {
    loading.value = false
  }
}

// Open add modal
function openAddModal(): void {
  isEditing.value = false
  formData.value = {
    id: null,
    instructor_id: instructors.value[0]?.id || null,
    schedule_date: new Date().toISOString().split('T')[0],
    start_time: '19:00',
    end_time: '20:00',
    max_bookings: 10
  }
  showModal.value = true
}

// Edit schedule
function editSchedule(schedule: Schedule): void {
  isEditing.value = true
  
  // Convert time objects to strings for form input
  const startTimeStr = typeof schedule.start_time === 'object' 
    ? `${schedule.start_time.getHours().toString().padStart(2, '0')}:${schedule.start_time.getMinutes().toString().padStart(2, '0')}`
    : schedule.start_time
    
  const endTimeStr = typeof schedule.end_time === 'object'
    ? `${schedule.end_time.getHours().toString().padStart(2, '0')}:${schedule.end_time.getMinutes().toString().padStart(2, '0')}`
    : schedule.end_time

  formData.value = {
    id: schedule.id,
    instructor_id: schedule.instructor_id,
    schedule_date: typeof schedule.date === 'object' 
      ? schedule.date.toISOString().split('T')[0] 
      : schedule.date,
    start_time: startTimeStr,
    end_time: endTimeStr,
    max_bookings: schedule.max_bookings
  }
  
  showModal.value = true
}

// Close modal
function closeModal(): void {
  showModal.value = false
}

// Save schedule (create or update)
async function saveSchedule(): Promise<void> {
  saving.value = true
  
  try {
    if (isEditing.value && formData.value.id !== null) {
      // Update existing
      const updateData = { 
        start_time: formData.value.start_time,
        end_time: formData.value.end_time,
        max_bookings: formData.value.max_bookings 
      }
      await apiClient.put(`/admin/schedules/${formData.value.id}`, updateData)
      alert('课程安排更新成功')
    } else {
      // Create new
      const createData = { ...formData.value, id: undefined }
      await apiClient.post('/admin/schedules', createData)
      alert('新课程安排添加成功')
    }
    
    closeModal()
    fetchSchedules()
  } catch (error: any) {
    console.error('Failed to save schedule:', error)
    const msg = error.response?.data?.detail || '保存失败'
    alert(typeof msg === 'string' ? msg : JSON.stringify(msg))
  } finally {
    saving.value = false
  }
}

// Delete schedule with confirmation
async function deleteSchedule(schedule: Schedule): Promise<void> {
  if (!confirm(`确定要删除课程安排 #${schedule.id} 吗？\n\n教练：${getInstructorName(schedule.instructor_id)}\n日期：${formatDate(schedule.date)}`)) {
    return
  }
  
  try {
    await apiClient.delete(`/admin/schedules/${schedule.id}`)
    alert('课程安排已删除')
    fetchSchedules()
  } catch (error: any) {
    console.error('Failed to delete schedule:', error)
    const msg = error.response?.data?.detail || '删除失败'
    alert(typeof msg === 'string' ? msg : JSON.stringify(msg))
  }
}

// Utility functions
function getInstructorName(id: number): string {
  const inst = instructors.value.find(i => i.id === id)
  return inst?.name || `教练 #${id}`
}

function formatDate(date: Date | string): string {
  if (!date) return '-'
  const d = new Date(date)
  return `${d.getFullYear()}-${(d.getMonth()+1).toString().padStart(2,'0')}-${d.getDate().toString().padStart(2,'0')}`
}

function formatTimeRange(startTime: any, endTime: any): string {
  if (!startTime || !endTime) return '-'
  
  const start = typeof startTime === 'object' 
    ? `${startTime.getHours().toString().padStart(2, '0')}:${startTime.getMinutes().toString().padStart(2, '0')}`
    : startTime
    
  const end = typeof endTime === 'object'
    ? `${endTime.getHours().toString().padStart(2, '0')}:${endTime.getMinutes().toString().padStart(2, '0')}`
    : endTime
  
  return `${start} - ${end}`
}

function getAvailabilityText(schedule: Schedule): string {
  const booked = schedule.confirmed_bookings_count || 0
  if (booked >= schedule.max_bookings) return '已满'
  return `剩余 ${schedule.max_bookings - booked} 位`
}

function getAvailabilityClass(schedule: Schedule): string {
  const booked = schedule.confirmed_bookings_count || 0
  return booked >= schedule.max_bookings ? 'full' : 'available'
}

function canDelete(schedule: Schedule): boolean {
  // Cannot delete if has confirmed bookings
  return (schedule.confirmed_bookings_count || 0) === 0
}

onMounted(() => {
  fetchInstructors()
  fetchSchedules()
})
</script>

<style scoped>
.schedule-management {
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header h1 {
  font-size: 28px;
  color: #333;
}

.filters {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  align-items: center;
}

select, .filter-input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
}

.table-container {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

th {
  background: #f9fafb;
  font-weight: 600;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
}

.status-badge.available { background: #d1fae5; color: #065f46; }
.status-badge.full { background: #fee2e2; color: #991b1b; }

.actions {
  display: flex;
  gap: 8px;
}

.btn-primary, .btn-secondary, .btn-sm, .btn-danger {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-primary { background: #3b82f6; color: white; }
.btn-secondary { background: #e5e7eb; color: #374151; }
.btn-sm { font-size: 13px; }
.btn-danger { background: #ef4444; color: white; }

.loading-state, .empty-state {
  text-align: center;
  padding: 48px;
  color: #999;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 24px;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
}

.modal-content h2 {
  margin-top: 0;
  margin-bottom: 24px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
}

.form-group input, .form-group select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

@media (max-width: 768px) {
  .form-row { grid-template-columns: 1fr; }
}
</style>
