<template>
  <div 
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    @click.self="$emit('close')"
    v-if="showModal"
  >
    <transition name="modal">
      <div 
        class="bg-white rounded-xl shadow-2xl w-full max-w-lg mx-4 overflow-hidden"
        @click.stop
      >
        
        <!-- Modal Header -->
        <div class="px-6 py-4 border-b flex items-center justify-between bg-gradient-to-r from-green-50 to-blue-50">
          <h3 class="text-xl font-bold text-gray-800 flex items-center gap-2">
            {{ isEdit ? '✏️ 编辑教练' : '➕ 添加新教练' }}
          </h3>
          <button 
            @click="$emit('close')"
            class="text-gray-400 hover:text-gray-600 transition hover:bg-white rounded-full p-1"
          >
            ✕
          </button>
        </div>

        <!-- Modal Body (Form) -->
        <form @submit.prevent="handleSubmit" class="px-6 py-5">
          
          <!-- Name Field (Required) -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              教练姓名 <span class="text-red-500">*</span>
            </label>
            <input 
              v-model="form.name"
              type="text" 
              required
              minlength="2"
              maxlength="100"
              placeholder="请输入教练姓名（至少 2 个字符）"
              :class="{ 'border-red-500': errors.name }"
              class="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-green-500 outline-none transition"
            />
            <p v-if="errors.name" class="mt-1 text-sm text-red-600">{{ errors.name }}</p>
          </div>

          <!-- Bio Field (Optional) -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">个人简介</label>
            <textarea 
              v-model="form.bio"
              rows="3"
              maxlength="500"
              placeholder="介绍一下教练的专业背景和教学经验..."
              :class="{ 'border-red-500': errors.bio }"
              class="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-green-500 outline-none transition resize-y"
            ></textarea>
            <div class="flex items-center justify-between mt-1">
              <p v-if="errors.bio" class="text-sm text-red-600">{{ errors.bio }}</p>
              <p class="text-xs text-gray-500">{{ form.bio.length }}/500</p>
            </div>
          </div>

          <!-- Phone Field (Optional) -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">手机号码</label>
            <input 
              v-model="form.phone"
              type="tel" 
              pattern="^1[3-9]\d{9}$"
              placeholder="11 位手机号（可选）"
              :class="{ 'border-red-500': errors.phone }"
              class="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-green-500 outline-none transition"
            />
            <p v-if="errors.phone" class="mt-1 text-sm text-red-600">{{ errors.phone }}</p>
          </div>

          <!-- Photo URL Field (Optional) -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">头像图片 URL</label>
            <input 
              v-model="form.photo_url"
              type="url" 
              placeholder="https://example.com/avatar.jpg（可选）"
              :class="{ 'border-red-500': errors.photo_url }"
              class="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-green-500 outline-none transition"
            />
            <p v-if="errors.photo_url" class="mt-1 text-sm text-red-600">{{ errors.photo_url }}</p>
            
            <!-- Preview Image -->
            <div v-if="form.photo_url && !errors.photo_url" class="mt-3 flex items-center gap-3">
              <img 
                :src="form.photo_url" 
                alt="头像预览"
                class="h-20 w-20 rounded-full object-cover border-2 border-green-500 shadow-sm"
                @error="errors.photo_url = '图片加载失败，请检查 URL'"
              />
              <button
                type="button"
                @click="form.photo_url = ''"
                class="text-xs text-red-600 hover:text-red-800 underline"
              >
                移除头像
              </button>
            </div>
          </div>

          <!-- Active Status Toggle (Edit mode only) -->
          <div v-if="isEdit" class="mb-4 p-3 bg-gray-50 rounded-lg">
            <label class="flex items-center cursor-pointer">
              <input 
                type="checkbox" 
                v-model="form.is_active"
                class="w-5 h-5 text-green-600 rounded focus:ring-green-500 border-gray-300"
              />
              <span class="ml-3 text-sm font-medium text-gray-700">启用该教练</span>
            </label>
            <p class="text-xs text-gray-500 mt-2 ml-8">
              {{ form.is_active ? '教练将显示在列表中' : '教练将被隐藏，但数据保留' }}
            </p>
          </div>

          <!-- Error Alert -->
          <div v-if="generalError" class="mb-4 bg-red-50 border border-red-200 rounded-lg p-3">
            <p class="text-sm text-red-700 flex items-center gap-2">
              <span>⚠️</span> {{ generalError }}
            </p>
          </div>

        </form>

        <!-- Modal Footer (Actions) -->
        <div class="px-6 py-4 bg-gray-50 border-t flex items-center justify-end gap-3">
          <button 
            type="button"
            @click="$emit('close')"
            :disabled="isSubmitting"
            class="px-5 py-2.5 border border-gray-300 rounded-lg hover:bg-gray-100 disabled:opacity-50 transition text-sm font-medium"
          >
            取消
          </button>
          <button 
            type="submit"
            @click="handleSubmit"
            :disabled="isSubmitting || !!generalError"
            class="px-5 py-2.5 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition transform hover:-translate-y-0.5 shadow-md text-sm font-medium flex items-center gap-2"
          >
            <span v-if="isSubmitting" class="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></span>
            {{ isSubmitting ? '保存中...' : (isEdit ? '保存修改' : '创建教练') }}
          </button>
        </div>

      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'

// Props
interface Props {
  instructor: any | null
}

const props = defineProps<Props>()
const emit = defineEmits(['close', 'save'])

// Computed
const isEdit = computed(() => props.instructor?.id !== undefined)

// Modal visibility (always show when component exists)
const showModal = ref(true)

// Form State
const form = reactive({
  name: '',
  bio: '',
  phone: '',
  photo_url: '',
  is_active: true
})

// Validation Errors
const errors = reactive<{[key: string]: string}>({})
const generalError = ref<string | null>(null)
const isSubmitting = ref(false)

// Initialize form from instructor data (if editing)
watch(() => props.instructor, (newVal) => {
  if (newVal) {
    form.name = newVal.name || ''
    form.bio = newVal.bio || ''
    form.phone = newVal.phone || ''
    form.photo_url = newVal.photo_url || ''
    form.is_active = newVal.is_active !== undefined ? newVal.is_active : true
  } else {
    // Reset for create mode
    resetForm()
  }
}, { immediate: true })

function resetForm() {
  form.name = ''
  form.bio = ''
  form.phone = ''
  form.photo_url = ''
  form.is_active = true
  clearErrors()
}

function clearErrors() {
  Object.keys(errors).forEach(key => delete errors[key])
  generalError.value = null
}

// Validation Rules
function validateForm(): boolean {
  clearErrors()
  
  // Name validation (required, min 2 chars)
  if (!form.name || form.name.trim().length < 2) {
    errors.name = '请输入至少 2 个字符的姓名'
    return false
  }
  
  if (form.name.length > 100) {
    errors.name = '姓名不能超过 100 个字符'
    return false
  }
  
  // Bio validation (optional, max length check)
  if (form.bio && form.bio.length > 500) {
    errors.bio = '简介不能超过 500 个字符'
    return false
  }
  
  // Phone validation (optional, but must be valid format if provided)
  const phoneRegex = /^1[3-9]\d{9}$/
  if (form.phone && !phoneRegex.test(form.phone)) {
    errors.phone = '请输入有效的 11 位手机号码'
    return false
  }
  
  // Photo URL validation (optional, but must be valid URL)
  if (form.photo_url) {
    try {
      new URL(form.photo_url)
    } catch {
      errors.photo_url = '请输入有效的图片 URL'
      return false
    }
    
    // Check if it looks like an image URL
    const isImage = /\.(jpg|jpeg|png|gif|webp)$/i.test(form.photo_url)
    if (!isImage && !form.photo_url.includes('http')) {
      errors.photo_url = '请确保这是一个有效的图片链接'
      return false
    }
  }
  
  return true
}

async function handleSubmit() {
  // Validate form first
  if (!validateForm()) {
    return
  }
  
  isSubmitting.value = true
  generalError.value = null
  
  try {
    // Prepare data for save (map to backend schema)
    const saveData = {
      name: form.name.trim(),
      bio: form.bio || null,
      phone: form.phone || null,
      photo_url: form.photo_url || null
    }
    
    if (isEdit.value) {
      // Include is_active for updates
      saveData.is_active = form.is_active
    }
    
    emit('save', saveData)
  } catch (err: any) {
    generalError.value = err.message || '操作失败'
  } finally {
    isSubmitting.value = false
  }
}

</script>

<style scoped>
/* Modal Transition */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(-20px);
}

/* Custom scrollbar */
textarea::-webkit-scrollbar {
  width: 6px;
}

textarea::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

textarea::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}

textarea::-webkit-scrollbar-thumb:hover {
  background: #666;
}

/* Input focus effects */
input:focus, textarea:focus {
  box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.1);
}

/* Button hover effect */
button:hover:not(:disabled) {
  transform: translateY(-1px);
}

button:active:not(:disabled) {
  transform: translateY(0);
}
</style>
