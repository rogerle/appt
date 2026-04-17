<template>
  <div class="instructor-management">
    <div class="header">
      <h1>🧘 教练管理</h1>
      <button @click="openAddModal" class="btn-primary">➕ 添加新教练</button>
    </div>

    <!-- Search & Filter -->
    <div class="filters">
      <input v-model="searchQuery" placeholder="搜索教练姓名..." class="search-input" />
      <select v-model="activeFilter" class="filter-select">
        <option value="">全部状态</option>
        <option value="active">仅活跃</option>
        <option value="inactive">仅停用</option>
      </select>
    </div>

    <!-- Instructor Table -->
    <div v-if="loading" class="loading">⏳ 加载中...</div>
    
    <div v-else-if="instructors.length === 0" class="empty-state">
      📭 暂无教练数据，点击上方按钮添加
    </div>

    <table v-else class="data-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>姓名</th>
          <th>门店 ID</th>
          <th>简介</th>
          <th>状态</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="instructor in filteredInstructors" :key="instructor.id">
          <td>#{{ instructor.id }}</td>
          <td>{{ instructor.name }}</td>
          <td>#{{ instructor.studio_id }}</td>
          <td class="description-cell">{{ instructor.description || '-' }}</td>
          <td>
            <span :class="['status-badge', instructor.is_active ? 'active' : 'inactive']">
              {{ instructor.is_active ? '活跃' : '停用' }}
            </span>
          </td>
          <td class="actions">
            <button @click="editInstructor(instructor)" class="btn-sm">编辑</button>
            <button 
              @click="toggleStatus(instructor)" 
              :class="['btn-sm', instructor.is_active ? 'btn-warning' : 'btn-success']"
            >
              {{ instructor.is_active ? '停用' : '启用' }}
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Add/Edit Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <h2>{{ isEditing ? '编辑教练' : '添加新教练' }}</h2>
        
        <form @submit.prevent="saveInstructor">
          <div class="form-group">
            <label>姓名 *</label>
            <input v-model="formData.name" required maxlength="50" placeholder="请输入教练姓名" />
          </div>

          <div class="form-group">
            <label>门店 ID *</label>
            <input v-model.number="formData.studio_id" type="number" required placeholder="请输入门店 ID" />
          </div>

          <div class="form-group">
            <label>头像 URL</label>
            <input v-model="formData.avatar_url" placeholder="https://example.com/avatar.jpg" />
          </div>

          <div class="form-group">
            <label>简介</label>
            <textarea v-model="formData.description" rows="3" maxlength="1000" 
              placeholder="请输入教练简介"></textarea>
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
import { ref, computed, onMounted } from 'vue'
import apiClient from '../../api/client'

interface Instructor {
  id: number
  studio_id: number
  name: string
  avatar_url: string | null
  description: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

// State
const instructors = ref<Instructor[]>([])
const loading = ref(false)
const saving = ref(false)
const showModal = ref(false)
const isEditing = ref(false)

// Filters
const searchQuery = ref('')
const activeFilter = ref('')

// Form data
const formData = ref({
  id: null as number | null,
  name: '',
  studio_id: 1,
  avatar_url: '',
  description: ''
})

// Computed - filtered instructors
const filteredInstructors = computed(() => {
  return instructors.value.filter(instr => {
    // Search filter
    if (searchQuery.value && !instr.name.toLowerCase().includes(searchQuery.value.toLowerCase())) {
      return false
    }
    
    // Status filter
    if (activeFilter.value === 'active' && !instr.is_active) return false
    if (activeFilter.value === 'inactive' && instr.is_active) return false
    
    return true
  })
})

// Fetch instructors
async function fetchInstructors(): Promise<void> {
  loading.value = true
  
  try {
    const res = await apiClient.get('/admin/instructors')
    instructors.value = res.data
  } catch (error) {
    console.error('Failed to fetch instructors:', error)
    alert('加载教练列表失败')
  } finally {
    loading.value = false
  }
}

// Open add modal
function openAddModal(): void {
  isEditing.value = false
  formData.value = { id: null, name: '', studio_id: 1, avatar_url: '', description: '' }
  showModal.value = true
}

// Edit instructor
function editInstructor(instructor: Instructor): void {
  isEditing.value = true
  formData.value = {
    id: instructor.id,
    name: instructor.name,
    studio_id: instructor.studio_id,
    avatar_url: instructor.avatar_url || '',
    description: instructor.description || ''
  }
  showModal.value = true
}

// Close modal
function closeModal(): void {
  showModal.value = false
}

// Save instructor (create or update)
async function saveInstructor(): Promise<void> {
  saving.value = true
  
  try {
    if (isEditing.value && formData.value.id !== null) {
      // Update existing
      await apiClient.put(`/admin/instructors/${formData.value.id}`, formData.value)
      alert('教练信息更新成功')
    } else {
      // Create new
      const createData = { ...formData.value, id: undefined }
      await apiClient.post('/admin/instructors', createData)
      alert('新教练添加成功')
    }
    
    closeModal()
    fetchInstructors()
  } catch (error: any) {
    console.error('Failed to save instructor:', error)
    const msg = error.response?.data?.detail || '保存失败'
    alert(typeof msg === 'string' ? msg : JSON.stringify(msg))
  } finally {
    saving.value = false
  }
}

// Toggle instructor status
async function toggleStatus(instructor: Instructor): Promise<void> {
  if (!confirm(`确定要${instructor.is_active ? '停用' : '启用'}教练 "${instructor.name}" 吗？`)) {
    return
  }
  
  try {
    await apiClient.patch(`/admin/instructors/${instructor.id}/toggle-status`)
    fetchInstructors()
  } catch (error) {
    console.error('Failed to toggle status:', error)
    alert('操作失败')
  }
}

onMounted(() => {
  fetchInstructors()
})
</script>

<style scoped>
.instructor-management {
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
}

.search-input, .filter-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
}

.search-input {
  flex: 1;
  max-width: 300px;
}

.data-table {
  width: 100%;
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

.description-cell {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
}

.status-badge.active { background: #d1fae5; color: #065f46; }
.status-badge.inactive { background: #fee2e2; color: #991b1b; }

.actions {
  display: flex;
  gap: 8px;
}

.btn-primary, .btn-secondary, .btn-sm {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-primary { background: #3b82f6; color: white; }
.btn-secondary { background: #e5e7eb; color: #374151; }
.btn-sm { font-size: 13px; }
.btn-warning { background: #fef3c7; color: #92400e; }
.btn-success { background: #d1fae5; color: #065f46; }

.loading, .empty-state {
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

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
}

.form-group input, .form-group textarea {
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
</style>
