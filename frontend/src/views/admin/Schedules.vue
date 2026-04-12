<template>
  <div class="space-y-6">
    <!-- 页面标题和操作按钮 -->
    <div class="flex justify-between items-center">
      <h1 class="text-3xl font-bold text-gray-900">排课管理</h1>
      <div class="flex space-x-3">
        <button
          @click="showSingleModal = true"
          class="px-4 py-2 bg-teal-600 text-white rounded-md hover:bg-teal-700 transition-colors"
        >
          ➕ 单次排课
        </button>
        <button
          @click="showBatchModal = true"
          class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        >
          📅 批量周排课
        </button>
      </div>
    </div>

    <!-- 日期筛选 -->
    <div class="bg-white rounded-lg shadow p-4">
      <label class="text-sm font-medium text-gray-700 mr-2">选择日期:</label>
      <input
        v-model="selectedDate"
        type="date"
        @change="loadSchedules"
        class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-teal-500 focus:border-teal-500"
      />
    </div>

    <!-- 排课列表 -->
    <div class="bg-white rounded-lg shadow p-6">
      <div v-if="loading" class="text-center py-8 text-gray-500">
        加载中...
      </div>

      <div v-else-if="schedules.length === 0" class="text-center py-8 text-gray-500">
        {{ selectedDate ? '该日期暂无排课' : '请选择日期查看排课' }}
      </div>

      <div v-else class="space-y-4">
        <div
          v-for="schedule in schedules"
          :key="schedule.id"
          class="border rounded-lg p-4 hover:shadow-md transition-shadow"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-4">
              <!-- 教练头像 -->
              <img
                :src="schedule.instructor?.avatar_url || '/default-avatar.png'"
                :alt="schedule.instructor?.name"
                class="w-12 h-12 rounded-full object-cover"
              />

              <div>
                <h3 class="font-semibold text-gray-900">
                  {{ schedule.instructor?.name }}
                </h3>
                <p class="text-sm text-gray-600">
                  📅 {{ formatDate(schedule.date) }} | ⏰ {{ formatTime(schedule.start_time, schedule.end_time) }}
                </p>
                <p v-if="schedule.title" class="text-xs text-teal-600 mt-1">
                  {{ schedule.title }}
                </p>
              </div>
            </div>

            <button
              @click="deleteSchedule(schedule)"
              class="px-3 py-1 text-sm bg-red-50 text-red-600 rounded hover:bg-red-100 transition-colors"
            >
              删除
            </button>
          </div>

          <!-- 预约人数统计 -->
          <div v-if="schedule.booking_count > 0" class="mt-3 text-sm text-gray-500">
            📊 {{ schedule.booking_count }}人已预约
          </div>
        </div>
      </div>
    </div>

    <!-- 单次排课弹窗 -->
    <div v-if="showSingleModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md mx-4">
        <h2 class="text-xl font-bold mb-4">单次排课</h2>

        <form @submit.prevent="handleSingleSubmit" class="space-y-4">
          <div>
            <label for="instructor_id" class="block text-sm font-medium text-gray-700 mb-1">选择教练 *</label>
            <select
              id="instructor_id"
              v-model="singleForm.instructor_id"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-teal-500 focus:border-teal-500"
            >
              <option value="">请选择教练</option>
              <option v-for="instructor in instructors" :key="instructor.id" :value="instructor.id">
                {{ instructor.name }}
              </option>
            </select>
          </div>

          <div>
            <label for="date" class="block text-sm font-medium text-gray-700 mb-1">日期 *</label>
            <input
              id="date"
              v-model="singleForm.date"
              type="date"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-teal-500 focus:border-teal-500"
            />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label for="start_time" class="block text-sm font-medium text-gray-700 mb-1">开始时间 *</label>
              <input
                id="start_time"
                v-model="singleForm.start_time"
                type="time"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-teal-500 focus:border-teal-500"
              />
            </div>

            <div>
              <label for="end_time" class="block text-sm font-medium text-gray-700 mb-1">结束时间 *</label>
              <input
                id="end_time"
                v-model="singleForm.end_time"
                type="time"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-teal-500 focus:border-teal-500"
              />
            </div>
          </div>

          <div>
            <label for="title" class="block text-sm font-medium text-gray-700 mb-1">课程标题</label>
            <input
              id="title"
              v-model="singleForm.title"
              type="text"
              placeholder="例如：晨间瑜伽"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-teal-500 focus:border-teal-500"
            />
          </div>

          <div class="flex space-x-3 pt-4">
            <button
              type="submit"
              :disabled="loading || singleForm.instructor_id === ''"
              class="flex-1 px-4 py-2 bg-teal-600 text-white rounded-md hover:bg-teal-700 disabled:opacity-50 transition-colors"
            >
              {{ loading ? '创建中...' : '创建排课' }}
            </button>
            <button
              type="button"
              @click="showSingleModal = false"
              class="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
            >
              取消
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 批量周排课弹窗 -->
    <div v-if="showBatchModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md mx-4 max-h-[90vh] overflow-y-auto">
        <h2 class="text-xl font-bold mb-4">批量周排课</h2>

        <form @submit.prevent="handleBatchSubmit" class="space-y-4">
          <div>
            <label for="batch_instructor_id" class="block text-sm font-medium text-gray-700 mb-1">选择教练 *</label>
            <select
              id="batch_instructor_id"
              v-model="batchForm.instructor_id"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-teal-500 focus:border-teal-500"
            >
              <option value="">请选择教练</option>
              <option v-for="instructor in instructors" :key="instructor.id" :value="instructor.id">
                {{ instructor.name }}
              </option>
            </select>
          </div>

          <div class="border-t pt-4">
            <h3 class="font-semibold mb-3">重复规则</h3>

            <div class="space-y-3">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">选择星期几:</label>
                <div class="flex flex-wrap gap-2">
                  <label v-for="(dayName, dayIndex) in weekDays" :key="dayIndex" class="inline-flex items-center">
                    <input
                      type="checkbox"
                      :value="dayIndex"
                      v-model="batchForm.daysOfWeek"
                      class="rounded border-gray-300 text-teal-600 focus:ring-teal-500"
                    />
                    <span class="ml-2 text-sm">{{ dayName }}</span>
                  </label>
                </div>
              </div>

              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label for="batch_start_time" class="block text-sm font-medium text-gray-700 mb-1">开始时间 *</label>
                  <input
                    id="batch_start_time"
                    v-model="batchForm.start_time"
                    type="time"
                    required
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                  />
                </div>

                <div>
                  <label for="batch_end_time" class="block text-sm font-medium text-gray-700 mb-1">结束时间 *</label>
                  <input
                    id="batch_end_time"
                    v-model="batchForm.end_time"
                    type="time"
                    required
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                  />
                </div>
              </div>

              <div>
                <label for="batch_title" class="block text-sm font-medium text-gray-700 mb-1">课程标题</label>
                <input
                  id="batch_title"
                  v-model="batchForm.title"
                  type="text"
                  placeholder="例如：每周瑜伽课"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                />
              </div>

              <div>
                <label for="start_date" class="block text-sm font-medium text-gray-700 mb-1">开始日期 *</label>
                <input
                  id="start_date"
                  v-model="batchForm.start_date"
                  type="date"
                  required
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                />
              </div>

              <div>
                <label for="end_date" class="block text-sm font-medium text-gray-700 mb-1">结束日期 *</label>
                <input
                  id="end_date"
                  v-model="batchForm.end_date"
                  type="date"
                  required
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-teal-500 focus:border-teal-500"
                />
              </div>
            </div>
          </div>

          <div class="flex space-x-3 pt-4">
            <button
              type="submit"
              :disabled="loading || batchForm.instructor_id === '' || batchForm.daysOfWeek.length === 0"
              class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {{ loading ? '创建中...' : '批量创建' }}
            </button>
            <button
              type="button"
              @click="showBatchModal = false"
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

const schedules = ref([])
const instructors = ref([])
const loading = ref(false)
const selectedDate = ref('')
const showSingleModal = ref(false)
const showBatchModal = ref(false)
const successMessage = ref('')

const singleForm = ref({
  instructor_id: '',
  date: new Date().toISOString().split('T')[0],
  start_time: '09:00',
  end_time: '10:00',
  title: ''
})

const batchForm = ref({
  instructor_id: '',
  daysOfWeek: [],
  start_time: '09:00',
  end_time: '10:00',
  title: '',
  start_date: new Date().toISOString().split('T')[0],
  end_date: ''
})

const weekDays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

onMounted(() => {
  loadInstructors()
  selectedDate.value = new Date().toISOString().split('T')[0]
})

const loadInstructors = async () => {
  try {
    const token = localStorage.getItem('admin_token')
    const response = await fetch(`${API_BASE_URL}/api/v1/studio/instructors`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })

    if (response.ok) {
      const data = await response.json()
      instructors.value = data.instructors || []
    }
  } catch (err) {
    console.error('Failed to load instructors:', err)
  }
}

const loadSchedules = async () => {
  if (!selectedDate.value) return

  loading.value = true
  try {
    const token = localStorage.getItem('admin_token')
    const response = await fetch(
      `${API_BASE_URL}/api/v1/studio/schedules?date=${selectedDate.value}`,
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    )

    if (response.ok) {
      const data = await response.json()
      schedules.value = data.schedules || []
    } else {
      console.error('Failed to load schedules:', response.statusText)
    }
  } catch (err) {
    console.error('Error loading schedules:', err)
  } finally {
    loading.value = false
  }
}

const handleSingleSubmit = async () => {
  const token = localStorage.getItem('admin_token')

  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/studio/schedules`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(singleForm.value)
    })

    if (response.ok) {
      showSuccess('排课已创建')
      loadSchedules()
      showSingleModal.value = false
      singleForm.value.title = ''
    } else {
      const data = await response.json()
      alert(data.detail || '创建失败')
    }
  } catch (err) {
    console.error('Error creating schedule:', err)
  }
}

const handleBatchSubmit = async () => {
  const token = localStorage.getItem('admin_token')

  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/studio/schedules/batch`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(batchForm.value)
    })

    if (response.ok) {
      showSuccess(`成功创建${batchForm.value.daysOfWeek.length}天的排课`)
      loadSchedules()
      showBatchModal.value = false
    } else {
      const data = await response.json()
      alert(data.detail || '批量创建失败')
    }
  } catch (err) {
    console.error('Error creating batch schedules:', err)
  }
}

const deleteSchedule = async (schedule) => {
  if (!confirm(`确定要删除 "${schedule.instructor?.name}" 的排课吗？`)) return

  const token = localStorage.getItem('admin_token')

  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/studio/schedules/${schedule.id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
    })

    if (response.ok) {
      schedules.value = schedules.value.filter(s => s.id !== schedule.id)
      showSuccess('排课已删除')
    } else {
      console.error('Failed to delete schedule:', response.statusText)
    }
  } catch (err) {
    console.error('Error deleting schedule:', err)
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

const formatTime = (start, end) => {
  if (!start || !end) return ''
  return `${start} - ${end}`
}

const showSuccess = (message) => {
  successMessage.value = message
  setTimeout(() => {
    successMessage.value = ''
  }, 3000)
}
</script>

<style scoped>
/* 使用 Tailwind CSS 类，无需额外样式 */
</style>
