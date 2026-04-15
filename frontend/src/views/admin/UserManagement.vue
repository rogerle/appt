<template>
  <div class="user-management">
    <div class="header">
      <h1>👥 用户管理</h1>
    </div>

    <!-- Search & Filter -->
    <div class="filters">
      <input 
        v-model="searchQuery" 
        placeholder="搜索邮箱或用户名..." 
        class="search-input"
      />

      <select v-model="roleFilter" @change="fetchUsers">
        <option value="">全部角色</option>
        <option value="user">普通用户</option>
        <option value="admin">管理员</option>
      </select>

      <button @click="fetchUsers" class="btn-secondary">🔍 搜索</button>
    </div>

    <!-- Stats Summary -->
    <div class="stats-summary">
      <div class="stat-item">
        <span class="label">总用户数:</span>
        <span class="value">{{ users.length }}</span>
      </div>
      <div class="stat-item">
        <span class="label">管理员:</span>
        <span class="value admin-count">{{ adminCount }}</span>
      </div>
      <div class="stat-item">
        <span class="label">普通用户:</span>
        <span class="value user-count">{{ userCount }}</span>
      </div>
    </div>

    <!-- Loading & Empty States -->
    <div v-if="loading" class="loading-state">⏳ 加载中...</div>
    
    <div v-else-if="users.length === 0" class="empty-state">
      📭 暂无用户数据
    </div>

    <!-- Users Table -->
    <div v-else class="table-container">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>邮箱</th>
            <th>用户名</th>
            <th>角色</th>
            <th>状态</th>
            <th>注册日期</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in filteredUsers" :key="user.id">
            <td>#{{ user.id }}</td>
            <td>{{ user.email }}</td>
            <td>{{ user.username }}</td>
            <td>
              <span :class="['role-badge', user.role]">
                {{ user.role === 'admin' ? '管理员' : '普通用户' }}
              </span>
            </td>
            <td>
              <button 
                v-if="user.id !== currentUserId"
                @click="toggleUserStatus(user)" 
                :class="['status-toggle', user.is_active ? 'btn-warning' : 'btn-success']"
              >
                {{ user.is_active ? '停用' : '启用' }}
              </button>
              <span v-else class="text-muted">(当前用户)</span>
            </td>
            <td>{{ formatDate(user.created_at) }}</td>
            <td class="actions">
              <button 
                v-if="user.id !== currentUserId"
                @click="editUserRole(user)" 
                class="btn-sm btn-secondary"
              >修改角色</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Role Edit Modal -->
    <div v-if="showRoleModal" class="modal-overlay" @click.self="closeRoleModal">
      <div class="modal-content modal-sm">
        <h2>修改用户角色</h2>
        
        <div class="user-info-card">
          <p><strong>{{ editingUser?.username }}</strong></p>
          <p class="email">{{ editingUser?.email }}</p>
          <p class="current-role">当前角色：<span :class="'role-badge ' + (editingUser?.role || '')">
            {{ editingUser?.role === 'admin' ? '管理员' : '普通用户' }}
          </span></p>
        </div>

        <form @submit.prevent="saveUserRole">
          <div class="form-group">
            <label>新角色 *</label>
            <select v-model="newRole" required>
              <option value="">请选择角色</option>
              <option value="user">普通用户</option>
              <option value="admin">管理员 ⚠️</option>
            </select>
          </div>

          <div v-if="newRole === 'admin'" class="warning-box">
            ⚠️ 谨慎操作！赋予管理员权限将允许该用户访问所有管理功能。
          </div>

          <div class="modal-actions">
            <button type="button" @click="closeRoleModal" class="btn-secondary">取消</button>
            <button type="submit" :disabled="saving" class="btn-primary">
              {{ saving ? '保存中...' : '确认修改' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Status Toggle Modal -->
    <div v-if="showStatusModal" class="modal-overlay" @click.self="closeStatusModal">
      <div class="modal-content modal-sm">
        <h2>{{ statusAction === 'deactivate' ? '停用账户' : '启用账户' }}</h2>
        
        <p v-if="statusAction === 'deactivate'" class="confirmation-text">
          确定要停用用户 <strong>{{ editingUser?.username }}</strong> 吗？
          <br><br>
          停用后，该用户将无法登录系统。
        </p>

        <p v-else class="confirmation-text">
          确定要启用用户 <strong>{{ editingUser?.username }}</strong> 吗？
          <br><br>
          启用后，该用户可以重新登录系统。
        </p>

        <div class="modal-actions">
          <button type="button" @click="closeStatusModal" class="btn-secondary">取消</button>
          <button 
            @click="confirmStatusChange" 
            :disabled="saving" 
            :class="['btn-primary', statusAction === 'deactivate' ? 'btn-warning' : '']"
          >
            {{ saving ? '处理中...' : (statusAction === 'deactivate' ? '确认停用' : '确认启用') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import apiClient from '../../api/client'
import { useAuthStore } from '../../stores/auth'

interface User {
  id: number
  email: string
  username: string
  role: 'user' | 'admin'
  is_active: boolean
  created_at: string
}

// Auth store for current user info
const authStore = useAuthStore()
const currentUserId = ref(authStore.user?.id || 0)

// State
const users = ref<User[]>([])
const loading = ref(false)
const saving = ref(false)

// Filters
const searchQuery = ref('')
const roleFilter = ref('')

// Modals
const showRoleModal = ref(false)
const showStatusModal = ref(false)
const editingUser = ref<User | null>(null)
const newRole = ref('')
const statusAction = ref<'activate' | 'deactivate'>('deactivate')

// Computed - filtered users
const filteredUsers = computed(() => {
  return users.value.filter(user => {
    // Search filter
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      if (!user.email.toLowerCase().includes(query) && 
          !user.username.toLowerCase().includes(query)) {
        return false
      }
    }

    // Role filter
    if (roleFilter.value && user.role !== roleFilter.value) {
      return false
    }

    return true
  })
})

const adminCount = computed(() => users.value.filter(u => u.role === 'admin').length)
const userCount = computed(() => users.value.filter(u => u.role === 'user').length)

// Fetch users with filters
async function fetchUsers(): Promise<void> {
  loading.value = true
  
  try {
    const params: Record<string, any> = {}
    
    if (searchQuery.value) {
      params.search = searchQuery.value
    }
    
    if (roleFilter.value) {
      params.role_filter = roleFilter.value
    }

    const res = await apiClient.get('/admin/users', { params })
    users.value = res.data
  } catch (error) {
    console.error('Failed to fetch users:', error)
    alert('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

// Edit user role
function editUserRole(user: User): void {
  editingUser.value = user
  newRole.value = ''
  showRoleModal.value = true
}

// Close role modal
function closeRoleModal(): void {
  showRoleModal.value = false
  editingUser.value = null
  newRole.value = ''
}

// Save user role change
async function saveUserRole(): Promise<void> {
  if (!editingUser.value || !newRole.value) return
  
  saving.value = true
  
  try {
    await apiClient.patch(`/admin/users/${editingUser.value.id}/role`, { 
      role: newRole.value 
    })
    
    alert(`用户 "${editingUser.value.username}" 的角色已更新为：${newRole.value === 'admin' ? '管理员' : '普通用户'}`)
    
    closeRoleModal()
    fetchUsers()
  } catch (error: any) {
    console.error('Failed to update role:', error)
    const msg = error.response?.data?.detail || '更新失败'
    alert(typeof msg === 'string' ? msg : JSON.stringify(msg))
  } finally {
    saving.value = false
  }
}

// Toggle user status (activate/deactivate)
function toggleUserStatus(user: User): void {
  editingUser.value = user
  statusAction.value = user.is_active ? 'deactivate' : 'activate'
  showStatusModal.value = true
}

// Close status modal
function closeStatusModal(): void {
  showStatusModal.value = false
  editingUser.value = null
}

// Confirm status change
async function confirmStatusChange(): Promise<void> {
  if (!editingUser.value) return
  
  saving.value = true
  
  try {
    await apiClient.patch(`/admin/users/${editingUser.value.id}/status`, { 
      is_active: statusAction.value === 'activate' 
    })
    
    alert(`用户 "${editingUser.value.username}" 已${statusAction.value === 'activate' ? '启用' : '停用'}`)
    
    closeStatusModal()
    fetchUsers()
  } catch (error: any) {
    console.error('Failed to update status:', error)
    const msg = error.response?.data?.detail || '操作失败'
    alert(typeof msg === 'string' ? msg : JSON.stringify(msg))
  } finally {
    saving.value = false
  }
}

// Utility functions
function formatDate(dateStr: string): string {
  try {
    const date = new Date(dateStr)
    return `${date.getFullYear()}-${(date.getMonth()+1).toString().padStart(2,'0')}-${date.getDate().toString().padStart(2,'0')}`
  } catch {
    return '-'
  }
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.user-management {
  max-width: 1200px;
  margin: 0 auto;
}

.header h1 {
  font-size: 28px;
  color: #333;
  margin-bottom: 24px;
}

.filters {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  align-items: center;
}

.search-input, select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
}

.search-input {
  flex: 1;
  max-width: 400px;
}

.btn-secondary {
  padding: 8px 16px;
  background: #e5e7eb;
  color: #374151;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

/* Stats Summary */
.stats-summary {
  display: flex;
  gap: 24px;
  margin-bottom: 24px;
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stat-item .label {
  color: #6b7280;
}

.stat-item .value {
  font-weight: bold;
  font-size: 18px;
  color: #374151;
}

/* Table */
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

.role-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.role-badge.admin { background: #dbeafe; color: #1e40af; }
.role-badge.user { background: #f3f4f6; color: #374151; }

.status-toggle, .btn-sm {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
}

.btn-success { background: #d1fae5; color: #065f46; }
.btn-warning { background: #fef3c7; color: #92400e; }

.text-muted {
  color: #9ca3af;
  font-size: 13px;
}

.actions {
  display: flex;
  gap: 8px;
}

/* Loading & Empty States */
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

.modal-sm {
  max-width: 450px;
}

.modal-content h2 {
  margin-top: 0;
  margin-bottom: 24px;
}

.user-info-card {
  background: #f9fafb;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 24px;
}

.user-info-card .email {
  color: #6b7280;
  font-size: 14px;
}

.user-info-card .current-role {
  margin-top: 8px;
  font-size: 14px;
}

.confirmation-text {
  line-height: 1.6;
  color: #374151;
}

.warning-box {
  background: #fef3c7;
  border-left: 4px solid #f59e0b;
  padding: 12px;
  margin-bottom: 20px;
  border-radius: 4px;
  font-size: 14px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
}

.form-group select {
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

.btn-primary, .btn-secondary {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.btn-primary { background: #3b82f6; color: white; }
.btn-secondary { background: #e5e7eb; color: #374151; }

.btn-warning { background: #f59e0b; color: white; }
</style>
