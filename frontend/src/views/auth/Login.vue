<template>
  <div class="login-page">
    <div class="login-container">
      <!-- Logo / Branding -->
      <div class="login-header">
        <h1>🧘 Appt 瑜伽预约系统</h1>
        <p class="subtitle">登录您的账户开始使用</p>
      </div>

      <!-- Login Form -->
      <form @submit.prevent="handleLogin" class="login-form">
        <div v-if="errorMessage" class="error-message">
          <span>{{ errorMessage }}</span>
        </div>

        <div class="form-group">
          <label for="email">邮箱</label>
          <input
            id="email"
            v-model="loginForm.email"
            type="email"
            placeholder="请输入邮箱地址"
            required
            :disabled="isLoading"
          />
        </div>

        <div class="form-group">
          <label for="password">密码</label>
          <input
            id="password"
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            required
            :disabled="isLoading"
          />
        </div>

        <button type="submit" class="btn-primary" :disabled="isLoading">
          <span v-if="!isLoading">登录</span>
          <span v-else class="loading-spinner">登录中...</span>
        </button>
      </form>

      <!-- Register Link -->
      <div class="login-footer">
        <p>还没有账户？<router-link to="/register">立即注册</router-link></p>
      </div>

      <!-- Demo Credentials (Development Only) -->
      <div v-if="isDevEnv" class="demo-credentials">
        <p><strong>测试账号:</strong></p>
        <p>邮箱：admin@appt.com</p>
        <p>密码：admin123</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

import { computed } from 'vue'

const router = useRouter()
const authStore = useAuthStore()

// Computed - check if in development environment
const isDevEnv = computed(() => import.meta.env.DEV)

// Form data
const loginForm = reactive({
  email: '',
  password: ''
})

// State
const isLoading = ref(false)
const errorMessage = ref('')

/**
 * Handle login submission
 */
async function handleLogin(): Promise<void> {
  // Reset error message
  errorMessage.value = ''
  
  if (!loginForm.email || !loginForm.password) {
    errorMessage.value = '请输入邮箱和密码'
    return
  }

  isLoading.value = true
  
  try {
    await authStore.login(loginForm.email, loginForm.password)
    
    // Redirect to homepage or previous page
    const redirectFrom = (router.currentRoute.value.query.from || '/') as string
    router.push(redirectFrom)
  } catch (error: any) {
    console.error('Login error:', error)
    
    if (error.response?.status === 401) {
      errorMessage.value = '邮箱或密码错误'
    } else if (error.response?.status === 403) {
      errorMessage.value = '账户已被禁用，请联系管理员'
    } else {
      errorMessage.value = error.response?.data?.detail || '登录失败，请重试'
    }
  } finally {
    isLoading.value = false
  }
}

// Auto-fill email if provided in query params (for password reset flow)
if (new URLSearchParams(window.location.search).get('email')) {
  loginForm.email = new URLSearchParams(window.location.search).get('email') || ''
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-container {
  width: 100%;
  max-width: 420px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  padding: 40px;
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-header h1 {
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

.login-footer {
  text-align: center;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #e0e0e0;
}

.login-footer p {
  color: #666;
  font-size: 14px;
}

.login-footer a {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}

.login-footer a:hover {
  text-decoration: underline;
}

.demo-credentials {
  margin-top: 32px;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 8px;
  font-size: 13px;
  color: #666;
}

.demo-credentials p {
  margin: 4px 0;
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
