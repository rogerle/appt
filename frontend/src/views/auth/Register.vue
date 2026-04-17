<template>
  <div class="register-page">
    <div class="register-container">
      <!-- Header -->
      <div class="register-header">
        <h1>🧘 创建账户</h1>
        <p class="subtitle">填写以下信息注册新账户</p>
      </div>

      <!-- Register Form -->
      <form @submit.prevent="handleRegister" class="register-form">
        <div v-if="errorMessage" class="error-message">
          <span>{{ errorMessage }}</span>
        </div>

        <div class="form-group">
          <label for="email">邮箱 *</label>
          <input
            id="email"
            v-model="registerForm.email"
            type="email"
            placeholder="example@email.com"
            required
            :disabled="isLoading"
          />
          <span v-if="formErrors.email" class="field-error">{{ formErrors.email }}</span>
        </div>

        <div class="form-group">
          <label for="username">用户名 *</label>
          <input
            id="username"
            v-model="registerForm.username"
            type="text"
            placeholder="3-100 个字符，唯一"
            minlength="3"
            maxlength="100"
            required
            :disabled="isLoading"
          />
          <span v-if="formErrors.username" class="field-error">{{ formErrors.username }}</span>
        </div>

        <div class="form-group">
          <label for="password">密码 *</label>
          <input
            id="password"
            v-model="registerForm.password"
            type="password"
            placeholder="至少 8 个字符"
            minlength="8"
            required
            :disabled="isLoading"
          />
          <span v-if="formErrors.password" class="field-error">{{ formErrors.password }}</span>
        </div>

        <div class="form-group">
          <label for="confirmPassword">确认密码 *</label>
          <input
            id="confirmPassword"
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="再次输入密码"
            required
            :disabled="isLoading"
          />
          <span v-if="formErrors.confirmPassword" class="field-error">{{ formErrors.confirmPassword }}</span>
        </div>

        <button type="submit" class="btn-primary" :disabled="isLoading">
          <span v-if="!isLoading">注册</span>
          <span v-else class="loading-spinner">注册中...</span>
        </button>
      </form>

      <!-- Login Link -->
      <div class="register-footer">
        <p>已有账户？<router-link to="/login">立即登录</router-link></p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// Form data
const registerForm = reactive({
  email: '',
  username: '',
  password: '',
  confirmPassword: ''
})

// State
const isLoading = ref(false)
const errorMessage = ref('')
const formErrors = reactive({
  email: '',
  username: '',
  password: '',
  confirmPassword: ''
})

/**
 * Validate registration form
 */
function validateForm(): boolean {
  // Clear previous errors
  formErrors.email = ''
  formErrors.username = ''
  formErrors.password = ''
  formErrors.confirmPassword = ''

  let isValid = true

  // Email validation (basic regex)
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!registerForm.email || !emailRegex.test(registerForm.email)) {
    formErrors.email = '请输入有效的邮箱地址'
    isValid = false
  }

  // Username validation
  if (!registerForm.username) {
    formErrors.username = '用户名不能为空'
    isValid = false
  } else if (registerForm.username.length < 3 || registerForm.username.length > 100) {
    formErrors.username = '用户名长度必须在 3-100 个字符之间'
    isValid = false
  }

  // Password validation
  if (!registerForm.password) {
    formErrors.password = '密码不能为空'
    isValid = false
  } else if (registerForm.password.length < 8) {
    formErrors.password = '密码长度至少需要 8 个字符'
    isValid = false
  }

  // Confirm password validation
  if (!registerForm.confirmPassword) {
    formErrors.confirmPassword = '请确认密码'
    isValid = false
  } else if (registerForm.password !== registerForm.confirmPassword) {
    formErrors.confirmPassword = '两次输入的密码不一致'
    isValid = false
  }

  return isValid
}

/**
 * Handle registration submission
 */
async function handleRegister(): Promise<void> {
  // Reset error messages
  errorMessage.value = ''

  // Validate form
  if (!validateForm()) {
    errorMessage.value = '请修正表单中的错误'
    return
  }

  isLoading.value = true
  
  try {
    await authStore.register(
      registerForm.email,
      registerForm.username,
      registerForm.password
    )
    
    // Registration successful - redirect to homepage (already auto-logged in)
    router.push('/')
  } catch (error: any) {
    console.error('Registration error:', error)
    
    if (error.response?.status === 400) {
      errorMessage.value = '邮箱或用户名已被注册'
      
      // Clear form fields that caused conflict
      const detail = error.response?.data?.detail || ''
      if (detail.includes('邮箱')) {
        registerForm.email = ''
      } else if (detail.includes('用户名')) {
        registerForm.username = ''
      }
    } else if (error.response?.status === 422) {
      // Validation errors from backend
      errorMessage.value = '输入数据无效，请检查后重试'
      
      // Try to extract field-specific errors
      const validationErrors = error.response?.data?.detail
      if (validationErrors && Array.isArray(validationErrors)) {
        validationErrors.forEach((err: any) => {
          const field = err.loc[err.loc.length - 1]
          if (field in formErrors) {
            formErrors[field as keyof typeof formErrors] = err.msg
          }
        })
      }
    } else {
      errorMessage.value = error.response?.data?.detail || '注册失败，请重试'
    }
  } finally {
    isLoading.value = false
  }
}

// Clear confirmation password field when user types in password field
const originalPasswordHandler = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.type === 'password') {
    registerForm.confirmPassword = ''
  }
}

document.addEventListener('input', originalPasswordHandler)

// Cleanup on unmount
import { onUnmounted } from 'vue'
onUnmounted(() => {
  document.removeEventListener('input', originalPasswordHandler)
})
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.register-container {
  width: 100%;
  max-width: 480px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  padding: 40px;
}

.register-header {
  text-align: center;
  margin-bottom: 32px;
}

.register-header h1 {
  font-size: 28px;
  color: #333;
  margin-bottom: 8px;
}

.subtitle {
  color: #666;
  font-size: 14px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #333;
  font-weight: 500;
  font-size: 14px;
}

.form-group input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 15px;
  transition: all 0.3s ease;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-group input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.field-error {
  display: block;
  color: #c62828;
  font-size: 12px;
  margin-top: 4px;
}

.error-message {
  background-color: #fee;
  border-left: 4px solid #f44336;
  padding: 12px 16px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.error-message span {
  color: #c62828;
  font-size: 14px;
}

.btn-primary {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.register-footer {
  text-align: center;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #e0e0e0;
}

.register-footer p {
  color: #666;
  font-size: 14px;
}

.register-footer a {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}

.register-footer a:hover {
  text-decoration: underline;
}

.loading-spinner {
  display: inline-block;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}
</style>
