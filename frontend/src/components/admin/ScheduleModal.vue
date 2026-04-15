<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <!-- Backdrop -->
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0" @click.self="closeModal">
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

        <!-- Modal Panel -->
        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl w-full">
          <!-- Header -->
          <div class="bg-gray-50 px-6 py-4 border-b flex items-center justify-between">
            <h3 class="text-lg font-semibold text-gray-900" id="modal-title">
              {{ isEditMode ? '✏️ 编辑课程' : '➕ 添加新课程' }}
            </h3>
            <button @click="closeModal" 
                    class="text-gray-400 hover:text-gray-600 transition text-2xl leading-none">
              ✕
            </button>
          </div>

          <!-- Form Body -->
          <form @submit.prevent="handleSubmit" 
                class="px-6 py-5 space-y-5 max-h-[calc(100vh-200px)] overflow-auto">
            
            <!-- Instructor Selection (Required) -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                教练选择 <span class="text-red-500">*</span>
              </label>
              <select v-model="formData.instructor_id" 
                      :disabled="isEditMode"
                      required
                      @change="validateInstructorId"
                      class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 outline-none transition disabled:bg-gray-100">
                <option value="">请选择教练...</option>
                <option v-for="coach in coaches" :key="coach.id" :value="coach.id">
                  {{ coach.name }} - {{ coach.bio || '暂无简介' }} ({{ coach.total_schedules || 0 }} 个课程)
                </option>
              </select>
              
              <!-- Error Message -->
              <p v-if="errors.instructor_id" class="mt-1 text-sm text-red-600 flex items-center gap-1">
                <span>⚠️</span> {{ errors.instructor_id }}
              </p>

              <!-- Helper Text (Edit mode only) -->
              <p v-if="isEditMode && formData.instructor_name" class="mt-2 text-sm text-gray-500">
                当前教练：{{ formData.instructor_name }}（编辑时不可更改）
              </p>
            </div>

            <!-- Date Selection (Required) -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                课程日期 <span class="text-red-500">*</span>
              </label>
              <input type="date" v-model="formData.schedule_date" 
                     required
                     @change="validateDate"
                     class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 outline-none transition">
              
              <!-- Error Message -->
              <p v-if="errors.schedule_date" class="mt-1 text-sm text-red-600 flex items-center gap-1">
                <span>⚠️</span> {{ errors.schedule_date }}
              </p>

              <!-- Day of Week Display -->
              <p v-if="formData.schedule_date && getDayOfWeek(formData.schedule_date)" 
                 class="mt-2 text-sm text-gray-500">
                📅 日期：{{ formatDate(formData.schedule_date) }} ({{ getDayOfWeek(formData.schedule_date) }})
              </p>
            </div>

            <!-- Time Range (Required) -->
            <div class="grid grid-cols-2 gap-4">
              <!-- Start Time -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  开始时间 <span class="text-red-500">*</span>
                </label>
                <input type="time" v-model="formData.start_time" 
                       required
                       @change="validateTimeRange"
                       class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 outline-none transition">
                
                <!-- Error Message -->
                <p v-if="errors.start_time" class="mt-1 text-sm text-red-600 flex items-center gap-1">
                  <span>⚠️</span> {{ errors.start_time }}
                </p>
              </div>

              <!-- End Time -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  结束时间 <span class="text-red-500">*</span>
                </label>
                <input type="time" v-model="formData.end_time" 
                       required
                       @change="validateTimeRange"
                       class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 outline-none transition">
                
                <!-- Error Message -->
                <p v-if="errors.end_time" class="mt-1 text-sm text-red-600 flex items-center gap-1">
                  <span>⚠️</span> {{ errors.end_time }}
                </p>
              </div>
            </div>

            <!-- Time Range Summary -->
            <div v-if="formData.start_time && formData.end_time" 
                 :class="{ 'bg-red-50 border-red-200': hasTimeError, 'bg-blue-50 border-blue-200': !hasTimeError }"
                 class="border rounded-lg p-3">
              <p class="text-sm">
                <span :class="{ 'text-red-700': hasTimeError, 'text-blue-700': !hasTimeError }">
                  {{ hasTimeError ? '⚠️' : 'ℹ️' }} 课程时长：{{ calculateDuration() }}
                </span>
              </p>
            </div>

            <!-- Max Bookings (Required, Min: 1) -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                容纳人数 <span class="text-red-500">*</span>
              </label>
              <input type="number" v-model.number="formData.max_bookings" 
                     min="1" max="50" required
                     @change="validateCapacity"
                     class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 outline-none transition">
              
              <!-- Error Message -->
              <p v-if="errors.max_bookings" class="mt-1 text-sm text-red-600 flex items-center gap-1">
                <span>⚠️</span> {{ errors.max_bookings }}
              </p>

              <!-- Helper Text (Edit mode) -->
              <p v-if="isEditMode && existingBookingCount > 0" 
                 class="mt-2 text-sm text-orange-600 flex items-center gap-1">
                ⚠️ 该课程已有 {{ existingBookingCount }} 个预约，容纳人数不能低于此数量
              </p>

              <p v-if="!isEditMode && !formData.max_bookings" 
                 class="mt-2 text-sm text-gray-500">
                💡 建议设置为 8-12 人（根据瑜伽类型调整）
              </p>
            </div>

            <!-- Conflict Warning (Edit mode only) -->
            <div v-if="isEditMode && showConflictWarning" 
                 class="bg-yellow-50 border border-yellow-200 rounded-lg p-3 flex items-start gap-2">
              <span class="text-yellow-600 text-xl">⚠️</span>
              <p class="text-sm text-yellow-800">
                修改时间段可能会与其他课程产生冲突。系统将自动检测并提示您。
              </p>
            </div>

          </form>

          <!-- Footer -->
          <div class="bg-gray-50 px-6 py-4 border-t flex items-center justify-end gap-3">
            <button @click="closeModal" 
                    :disabled="loading"
                    class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition disabled:opacity-50 disabled:cursor-not-allowed">
              取消
            </button>

            <button @click="handleSubmit" 
                    :disabled="loading || !isFormValid"
                    class="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 transition flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed">
              <span v-if="loading" class="inline-block animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full"></span>
              {{ loading ? '保存中...' : (isEditMode ? '更新课程' : '创建课程') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import axios from 'axios'

// Props
const props = defineProps({
  scheduleData: Object, // Can be null for create mode or object with id for edit mode
  coaches: Array,
  isEditMode: Boolean
})

// Emit events
const emit = defineEmits(['close', 'save'])

// Form state
const formData = ref({
  instructor_id: '',
  schedule_date: '',
  start_time: '',
  end_time: '',
  max_bookings: 1,
  
  // Denormalized field (read-only in edit mode)
  instructor_name: '' 
})

// Validation errors
const errors = ref({
  instructor_id: null,
  schedule_date: null,
  start_time: null,
  end_time: null,
  max_bookings: null
})

// State
const loading = ref(false)
const existingBookingCount = ref(0)
const showConflictWarning = ref(false)

// Watch for prop changes (populate form when editing)
watch(() => props.scheduleData, (newVal) => {
  if (newVal && newVal.id) {
    // Edit mode: Populate with existing data
    formData.value = {
      instructor_id: newVal.instructor_id,
      schedule_date: newVal.schedule_date,
      start_time: newVal.start_time,
      end_time: newVal.end_time,
      max_bookings: newVal.max_bookings,
      instructor_name: newVal.instructor_name
    }

    existingBookingCount.value = newVal.booking_count || 0
    showConflictWarning.value = true
    
    // Pre-validate time range and capacity
    validateTimeRange()
    validateCapacity()
  } else {
    // Create mode: Reset to defaults
    resetForm()
  }
}, { immediate: true })

// Computed properties
const isFormValid = computed(() => {
  return !Object.values(errors.value).some(err => err !== null) && 
         formData.value.instructor_id && 
         formData.value.schedule_date &&
         formData.value.start_time && 
         formData.value.end_time &&
         formData.value.max_bookings > 0
})

const hasTimeError = computed(() => {
  return errors.value.start_time || errors.value.end_time
})

// Reset form to defaults
function resetForm() {
  formData.value = {
    instructor_id: '',
    schedule_date: '',
    start_time: '',
    end_time: '',
    max_bookings: 1,
    instructor_name: ''
  }

  errors.value = {
    instructor_id: null,
    schedule_date: null,
    start_time: null,
    end_time: null,
    max_bookings: null
  }

  existingBookingCount.value = 0
  showConflictWarning.value = false
}

// Validation functions
function validateInstructorId() {
  errors.value.instructor_id = !formData.value.instructor_id ? '请选择教练' : null
}

function validateDate() {
  if (!formData.value.schedule_date) {
    errors.value.schedule_date = '请选择日期'
    return false
  }

  const selectedDate = new Date(formData.value.schedule_date)
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  if (selectedDate < today) {
    errors.value.schedule_date = '日期不能早于今天'
    return false
  }

  errors.value.schedule_date = null
  return true
}

function validateTimeRange() {
  // Clear previous errors first
  errors.value.start_time = null
  errors.value.end_time = null
  
  if (!formData.value.start_time) {
    errors.value.start_time = '请输入开始时间'
    return false
  }

  if (!formData.value.end_time) {
    errors.value.end_time = '请输入结束时间'
    return false
  }

  // Compare times (convert to minutes for comparison)
  const [startHour, startMin] = formData.value.start_time.split(':').map(Number)
  const [endHour, endMin] = formData.value.end_time.split(':').map(Number)

  const startMinutes = startHour * 60 + startMin
  const endMinutes = endHour * 60 + endMin

  if (endMinutes <= startMinutes) {
    errors.value.start_time = '结束时间必须晚于开始时间'
    return false
  }

  // Suggest minimum duration (30 minutes for yoga classes)
  if (endMinutes - startMinutes < 30) {
    errors.value.end_time = '课程时长建议至少为 30 分钟'
    return false
  }

  return true
}

function validateCapacity() {
  if (!formData.value.max_bookings || formData.value.max_bookings < 1) {
    errors.value.max_bookings = '容纳人数必须大于等于 1'
    return false
  }

  if (formData.value.max_bookings > 50) {
    errors.value.max_bookings = '容纳人数不能超过 50 人（安全限制）'
    return false
  }

  // In edit mode, cannot reduce below existing bookings
  if (props.isEditMode && formData.value.max_bookings < existingBookingCount.value) {
    errors.value.max_bookings = `容纳人数不能低于现有预约数 (${existingBookingCount.value})`
    return false
  }

  errors.value.max_bookings = null
  return true
}

// Helper functions
function formatDate(dateStr) {
  if (!dateStr) return ''
  
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

function getDayOfWeek(dateStr) {
  if (!dateStr) return ''
  
  const days = ['日', '一', '二', '三', '四', '五', '六']
  const date = new Date(dateStr)
  return `周${days[date.getDay()]}`
}

function calculateDuration() {
  if (!formData.value.start_time || !formData.value.end_time) return ''

  const [startHour, startMin] = formData.value.start_time.split(':').map(Number)
  const [endHour, endMin] = formData.value.end_time.split(':').map(Number)

  const startMinutes = startHour * 60 + startMin
  const endMinutes = endHour * 60 + endMin
  const duration = endMinutes - startMinutes

  if (duration < 60) {
    return `${duration}分钟`
  } else {
    const hours = Math.floor(duration / 60)
    const minutes = duration % 60
    return `${hours}小时${minutes > 0 ? minutes + '分钟' : ''}`
  }
}

// Close modal handler
function closeModal() {
  emit('close')
}

// Form submit handler
async function handleSubmit() {
  // Run all validations first
  validateInstructorId()
  const dateValid = validateDate()
  const timeValid = validateTimeRange()
  const capacityValid = validateCapacity()

  if (!isFormValid.value) return

  loading.value = true
  
  try {
    // Prepare payload for API (exclude denormalized instructor_name field)
    const payload = {
      instructor_id: formData.value.instructor_id,
      schedule_date: formData.value.schedule_date,
      start_time: `${formData.value.start_time}:00`, // Add seconds for backend compatibility
      end_time: `${formData.value.end_time}:00`,     // Add seconds for backend compatibility
      max_bookings: formData.value.max_bookings
    }

    if (props.isEditMode) {
      // Update existing schedule
      await axios.patch(`/api/v1/schedules/${formData.value.id}`, payload)
    } else {
      // Create new schedule
      await axios.post('/api/v1/schedules/', payload)
    }

    emit('save', props.isEditMode ? formData.value : null)
    
  } catch (err) {
    const errorData = err.response?.data || {}
    const errorMessage = errorData.detail || '保存失败'
    
    // Handle specific validation errors from backend
    if (errorData.type === 'conflict') {
      alert('⚠️ 时间冲突：该教练在此时间段已有其他课程安排')
    } else {
      alert(errorMessage)
    }

    console.error('Failed to save schedule:', err)
    
  } finally {
    loading.value = false
  }
}

// Expose resetForm for parent component access if needed
defineExpose({ resetForm })
</script>

<style scoped>
/* Smooth scrollbar */
.overflow-auto::-webkit-scrollbar {
  width: 8px;
}

.overflow-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.overflow-auto::-webkit-scrollbar-thumb {
  background: #cbd5e0;
  border-radius: 4px;
}

.overflow-auto::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
