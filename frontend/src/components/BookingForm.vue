<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  instructor: { type: Object, required: true },
  date: { type: String, required: true },
  timeSlot: { type: Object, required: true }
})

const emit = defineEmits(['submit', 'cancel'])

// Form state
const formData = ref({ name: '', phone: '' })
const errors = ref({ name: null, phone: null })

// Validation rules
const isNameValid = computed(() => {
  return formData.value.name.trim().length >= 1
})

const isPhoneValid = computed(() => {
  const phoneRegex = /^1[3-9]\d{9}$/
  return phoneRegex.test(formData.value.phone) && formData.value.phone.length === 11
})

const canSubmit = computed(() => {
  return isNameValid.value && isPhoneValid.value && !errors.value.name && !errors.value.phone
})

// Methods
function validateName() {
  if (!formData.value.name.trim()) {
    errors.value.name = '姓名不能为空'
    return false
  } else if (formData.value.name.trim().length < 2) {
    errors.value.name = '姓名至少需要 2 个字符'
    return false
  } else {
    errors.value.name = null
    return true
  }
}

function validatePhone() {
  const phoneRegex = /^1[3-9]\d{9}$/
  
  if (!formData.value.phone) {
    errors.value.phone = '手机号不能为空'
    return false
  } else if (formData.value.phone.length !== 11) {
    errors.value.phone = '请输入正确的 11 位手机号'
    return false
  } else if (!phoneRegex.test(formData.value.phone)) {
    errors.value.phone = '手机号格式不正确'
    return false
  } else {
    errors.value.phone = null
    return true
  }
}

function handleSubmit() {
  // Validate before submit
  const nameValid = validateName()
  const phoneValid = validatePhone()
  
  if (!nameValid || !phoneValid) return
  
  emit('submit', formData.value)
}

function handleCancel() {
  emit('cancel')
}

// Clear errors on input change
function clearError(field) {
  errors.value[field] = null
}
</script>

<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="card max-w-md w-full">
      <h3 class="text-xl font-semibold mb-6">预约信息确认</h3>

      <!-- Booking Summary -->
      <div class="bg-gray-light rounded-lg p-4 mb-6 text-sm">
        <div class="flex items-center gap-2 mb-2">
          <img 
            v-if="instructor.avatar_url" 
            :src="instructor.avatar_url" 
            alt=""
            class="w-8 h-8 rounded-full object-cover"
          />
          <span class="font-medium">{{ instructor.name }}</span>
        </div>
        <div>{{ date }}</div>
        <div>{{ timeSlot.start_time }} - {{ timeSlot.end_time }}</div>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleSubmit" class="space-y-4">
        <!-- Name Field -->
        <div>
          <label for="name" class="block text-sm font-medium mb-2">姓名 *</label>
          <input 
            id="name"
            v-model="formData.name"
            type="text"
            placeholder="请输入您的姓名"
            @blur="validateName"
            :class="[
              'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:outline-none transition-shadow',
              errors.name ? 'border-red-500 focus:ring-red-500' : 'border-gray-300 focus:ring-blue-500'
            ]"
          />
          <p v-if="errors.name" class="text-red-500 text-xs mt-1">{{ errors.name }}</p>
        </div>

        <!-- Phone Field -->
        <div>
          <label for="phone" class="block text-sm font-medium mb-2">手机号 *</label>
          <input 
            id="phone"
            v-model="formData.phone"
            type="tel"
            placeholder="请输入您的 11 位手机号"
            maxlength="11"
            @blur="validatePhone"
            :class="[
              'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:outline-none transition-shadow',
              errors.phone ? 'border-red-500 focus:ring-red-500' : 'border-gray-300 focus:ring-blue-500'
            ]"
          />
          <p v-if="errors.phone" class="text-red-500 text-xs mt-1">{{ errors.phone }}</p>
        </div>

        <!-- Action Buttons -->
        <div class="flex gap-3 pt-4">
          <button 
            type="button" 
            @click="handleCancel"
            class="btn-secondary flex-1 py-2 px-6 rounded-lg font-medium transition-colors"
          >
            取消
          </button>
          <button 
            type="submit" 
            :disabled="!canSubmit"
            class="btn-primary flex-1 py-2 px-6 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            确认预约
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
/* Additional component styles if needed */
</style>
