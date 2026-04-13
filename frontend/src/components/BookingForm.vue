<script setup lang="ts">
import { ref, computed } from 'vue'

const props = defineProps<{
  customerName?: string
  customerPhone?: string
  customerNote?: string
}>()

const emit = defineEmits<{
  update: [data: { name: string; phone: string; note: string }]
  submit: []
}>()

// Local form state
const formData = ref({
  name: props.customerName || '',
  phone: props.customerPhone || '',
  note: props.customerNote || ''
})

// Validation errors
const errors = {
  name: computed(() => !formData.value.name.trim() ? '请输入姓名' : ''),
  phone: computed(() => {
    if (!formData.value.phone) return '请输入联系电话'
    const pattern = /^1[3-9]\d{9}$/
    return pattern.test(formData.value.phone) ? '' : '请输入有效的手机号码（11 位）'
  })
})

// Form validity
const isFormValid = computed(() => {
  return formData.value.name.trim() && 
         !errors.value.name && 
         !errors.value.phone
})

function updateField(field: keyof typeof formData.value, value: string) {
  formData.value[field] = value
  
  // Emit update event
  emit('update', {
    name: formData.value.name,
    phone: formData.value.phone,
    note: formData.value.note
  })
}

function handleSubmit() {
  if (isFormValid.value) {
    emit('submit')
  } else {
    // Trigger validation on all fields
    Object.keys(errors).forEach(() => {})
  }
}

// Format phone number with spaces for readability (e.g., 138 0000 0000)
function formatPhone(value: string) {
  const digits = value.replace(/\D/g, '').slice(0, 11)
  
  if (digits.length <= 3) return digits
  if (digits.length <= 7) return `${digits.slice(0, 3)} ${digits.slice(3)}`
  return `${digits.slice(0, 3)} ${digits.slice(3, 7)} ${digits.slice(7)}`
}
</script>

<template>
  <form @submit.prevent="handleSubmit" class="booking-form">
    <!-- Name Field -->
    <div class="mb-5">
      <label class="block text-sm font-semibold text-gray-700 mb-2">
        📝 姓名 <span class="text-red-500">*</span>
      </label>
      <input 
        type="text" 
        v-model="formData.name"
        @input="$event.target.value = $event.target.value.trim()"
        placeholder="请输入您的真实姓名"
        :class="[
          'w-full px-4 py-3 rounded-lg border-2 transition-all duration-200',
          errors.name ? 'border-red-400 focus:ring-2 focus:ring-red-200' 
                     : 'border-primary-300 focus:border-accent-green focus:ring-2 focus:ring-accent-light'
        ]"
      />
      <p v-if="errors.name" class="mt-1 text-sm text-red-600 flex items-center">
        ⚠️ {{ errors.name }}
      </p>
    </div>

    <!-- Phone Field -->
    <div class="mb-5">
      <label class="block text-sm font-semibold text-gray-700 mb-2">
        📱 联系电话 <span class="text-red-500">*</span>
      </label>
      <input 
        type="tel" 
        v-model="formData.phone"
        @input="$event.target.value = formatPhone($event.target.value.replace(/\s/g, ''))"
        placeholder="请输入 11 位手机号码"
        maxlength="13"
        :class="[
          'w-full px-4 py-3 rounded-lg border-2 transition-all duration-200',
          errors.phone ? 'border-red-400 focus:ring-2 focus:ring-red-200' 
                      : 'border-primary-300 focus:border-accent-green focus:ring-2 focus:ring-accent-light'
        ]"
      />
      <p v-if="errors.phone" class="mt-1 text-sm text-red-600 flex items-center">
        ⚠️ {{ errors.phone }}
      </p>
      <p class="mt-1 text-xs text-gray-500">
        ℹ️ 预约成功后将发送短信通知到该手机
      </p>
    </div>

    <!-- Note Field (Optional) -->
    <div class="mb-6">
      <label class="block text-sm font-semibold text-gray-700 mb-2">
        💬 备注（可选）
      </label>
      <textarea 
        v-model="formData.note"
        @input="updateField('note', $event.target.value)"
        placeholder="如有特殊需求、身体状况或疑问，请在此留言..."
        rows="4"
        class="w-full px-4 py-3 rounded-lg border-2 border-primary-300 focus:border-accent-green focus:ring-2 focus:ring-accent-light transition-all duration-200 resize-none"
      ></textarea>
      <p class="mt-1 text-xs text-gray-500">
        例如：初次练习、腰部不适需要关注等
      </p>
    </div>

    <!-- Submit Button -->
    <button 
      type="submit"
      :disabled="!isFormValid"
      class="w-full bg-accent-dark hover:bg-accent-green disabled:bg-gray-400 text-white font-bold py-4 px-6 rounded-lg transition-all duration-200 transform hover:scale-[1.02] disabled:transform-none disabled:cursor-not-allowed shadow-md"
    >
      ✅ 确认预约
    </button>

    <!-- Privacy Notice -->
    <p class="mt-4 text-xs text-center text-gray-500">
      🔒 您的个人信息将严格保密，仅用于本次预约服务
    </p>
  </form>
</template>

<style scoped></style>
