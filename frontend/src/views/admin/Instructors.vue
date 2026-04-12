<template>
  <div class="space-y-6">
    <!-- 页面标题 -->
    <div class="flex justify-between items-center">
      <h1 class="text-3xl font-bold text-gray-900">教练管理</h1>
      <button
        @click="showAddModal = true"
        class="px-4 py-2 bg-teal-600 text-white rounded-md hover:bg-teal-700 transition-colors"
      >
        ➕ 添加新教练
      </button>
    </div>

    <!-- 教练列表 -->
    <div class="bg-white rounded-lg shadow p-6">
      <div v-if="loading" class="text-center py-8 text-gray-500">
        加载中...
      </div>

      <div v-else-if="instructors.length === 0" class="text-center py-8 text-gray-500">
        暂无教练数据
      </div>

      <div v-else class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="instructor in instructors"
          :key="instructor.id"
          class="border rounded-lg p-4 hover:shadow-md transition-shadow"
        >
          <div class="flex items-start justify-between">
            <div class="flex items-center space-x-3">
              <img
                :src="instructor.avatar_url || '/default-avatar.png'"
                :alt="instructor.name"
                class="w-12 h-12 rounded-full object-cover"
              />
              <div>
                <h3 class="font-semibold text-gray-900">{{ instructor.name }}</h3>
                <p class="text-sm text-gray-600">{{ instructor.title || '瑜伽教练' }}</p>
              </div>
            </div>
            <button
              @click="toggleStatus(instructor)"
              :class="{
                'bg-green-100 text-green-700': instructor.is_active,
                'bg-gray-100 text-gray-600': !instructor.is_active
              }"
              class="px-3 py-1 rounded-full text-xs font-medium"
            >
              {{ instructor.is_active ? '✓ 启用' : '✕ 禁用' }}
            </button>
          </div>

          <p class="mt-3 text-sm text-gray-600 line-clamp-2">
            {{ instructor.bio || '暂无简介' }}
          </p>

          <div class="mt-4 flex space-x-2">
            <button
              @click="editInstructor(instructor)"
              class="flex-1 px-3 py-2 text-sm bg-blue-50 text-blue-600 rounded hover:bg-blue-100 transition-colors"
            >
              编辑
            </button>
            <button
              @click="deleteInstructor(instructor)"
              class="flex-1 px-3 py-2 text-sm bg-red-50 text-red-600 rounded hover:bg-red-100 transition-colors"
            >
              删除
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加/编辑教练弹窗 -->
    <div v-if="showAddModal || showEditModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md mx-4">
        <h2 class="text-xl font-bold mb-4">{{ isEditing ? '编辑教练' : '添加新教练' }}</h2>

        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div>
            <label for="name" class="block text-sm font-medium text-gray-700 mb-1">姓名 *</label>
            <input
              id="name"
              v-model="formData.name"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-teal-500 focus:border-teal-500"
            />
          </div>

          <div>
            <label for="title" class="block text-sm font-medium text-gray-700 mb-1">头衔</label>
            <input
              id="title"
              v-model="formData.title"
              type="text"
              placeholder="例如：资深瑜伽导师"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-teal-500 focus:border-teal-500"
            />
          </div>

          <div>
            <label for="avatar_url" class="block text-sm font-medium text-gray-700 mb-1">头像 URL</label>
            <input
              id="avatar_url"
              v-model="formData.avatar_url"
              type="url"
              placeholder="https://example.com/avatar.jpg"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-teal-500 focus:border-teal-500"
            />
          </div>

          <div>
            <label for="bio" class="block text-sm font-medium text-gray-700 mb-1">简介</label>
            <textarea
              id="bio"
              v-model="formData.bio"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-teal-500 focus:border-teal-500"
              placeholder="简短介绍教练的背景和专长..."
            ></textarea>
          </div>

          <div class="flex space-x-3 pt-4">
            <button
              type="submit"
              :disabled="loading"
              class="flex-1 px-4 py-2 bg-teal-600 text-white rounded-md hover:bg-teal-700 disabled:opacity-50 transition-colors"
            >
              {{ loading ? '保存中...' : (isEditing ? '更新' : '添加') }}
            </button>
            <button
              type="button"
              @click="closeModal"
              class="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
            >
              取消
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 成功/错误提示 -->
    <div v-if="successMessage" class="fixed bottom-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg">
      {{ successMessage }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const instructors = ref([])
const loading = ref(false)
const showAddModal = ref(false)
const showEditModal = ref(false)
const isEditing = ref(false)
const successMessage = ref('')

const formData = ref({
  name: '',
  title: '',
  avatar_url: '',
  bio: ''
})

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

onMounted(() => {
  loadInstructors()
})

const loadInstructors = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('admin_token')
    const response = await fetch(`${API_BASE_URL}/api/v1/studio/instructors`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (response.ok) {
      const data = await response.json()
      instructors.value = data.instructors || []
    } else {
      console.error('Failed to load instructors:', response.statusText)
    }
  } catch (err) {
    console.error('Error loading instructors:', err)
  } finally {
    loading.value = false
  }
}

const toggleStatus = async (instructor) => {
  try {
    const token = localStorage.getItem('admin_token')
    const response = await fetch(`${API_BASE_URL}/api/v1/studio/instructors/${instructor.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ is_active: !instructor.is_active })
    })

    if (response.ok) {
      const index = instructors.value.findIndex(i => i.id === instructor.id)
      if (index !== -1) {
        instructors.value[index].is_active = !instructor.is_active
      }
      showSuccess('状态已更新')
    } else {
      console.error('Failed to toggle status:', response.statusText)
    }
  } catch (err) {
    console.error('Error toggling status:', err)
  }
}

const editInstructor = (instructor) => {
  formData.value = { ...instructor }
  isEditing.value = true
  showEditModal.value = true
}

const deleteInstructor = async (instructor) => {
  if (!confirm(`确定要禁用教练 "${instructor.name}" 吗？`)) return

  try {
    const token = localStorage.getItem('admin_token')
    const response = await fetch(`${API_BASE_URL}/api/v1/studio/instructors/${instructor.id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (response.ok) {
      instructors.value = instructors.value.filter(i => i.id !== instructor.id)
      showSuccess('教练已禁用')
    } else {
      console.error('Failed to delete instructor:', response.statusText)
    }
  } catch (err) {
    console.error('Error deleting instructor:', err)
  }
}

const handleSubmit = async () => {
  const token = localStorage.getItem('admin_token')
  
  try {
    if (isEditing.value) {
      // 更新操作
      const response = await fetch(`${API_BASE_URL}/api/v1/studio/instructors/${formData.value.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData.value)
      })

      if (response.ok) {
        const index = instructors.value.findIndex(i => i.id === formData.value.id)
        if (index !== -1) {
          instructors.value[index] = { ...instructors.value[index], ...formData.value }
        }
        showSuccess('教练信息已更新')
      } else {
        console.error('Failed to update instructor:', response.statusText)
      }
    } else {
      // 添加操作
      const response = await fetch(`${API_BASE_URL}/api/v1/studio/instructors`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData.value)
      })

      if (response.ok) {
        const newInstructor = await response.json()
        instructors.value.push(newInstructor.instructor || newInstructor)
        showSuccess('教练已添加')
      } else {
        console.error('Failed to add instructor:', response.statusText)
      }
    }

    closeModal()
  } catch (err) {
    console.error('Error saving instructor:', err)
  }
}

const closeModal = () => {
  showAddModal.value = false
  showEditModal.value = false
  isEditing.value = false
  formData.value = { name: '', title: '', avatar_url: '', bio: '' }
}

const showSuccess = (message) => {
  successMessage.value = message
  setTimeout(() => {
    successMessage.value = ''
  }, 3000)
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
