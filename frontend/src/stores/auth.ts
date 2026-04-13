import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient from '../api/client'

export interface User {
  id: number
  username: string
  studio_name?: string
  phone?: string
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('auth_token'))
  
  // Computed properties
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  
  // Actions
  async function login(username: string, password: string): Promise<void> {
    try {
      const formData = new URLSearchParams()
      formData.append('username', username)
      formData.append('password', password)
      
      const response = await apiClient.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      })
      
      token.value = response.data.access_token
      localStorage.setItem('auth_token', token.value)
      
      // Fetch user info after login
      await fetchCurrentUser()
    } catch (error) {
      throw error
    }
  }
  
  async function register(studioName: string, phone: string, password: string): Promise<User> {
    try {
      const response = await apiClient.post('/auth/register', {
        studio_name: studioName,
        phone: phone,
        password: password
      })
      
      // Auto-login after registration
      token.value = response.data.access_token || null
      
      user.value = response.data
      return response.data
    } catch (error) {
      throw error
    }
  }
  
  async function fetchCurrentUser(): Promise<void> {
    try {
      const response = await apiClient.get('/auth/me')
      user.value = response.data as User
    } catch (error) {
      // Clear token if current user fetch fails
      logout()
    }
  }
  
  function logout(): void {
    user.value = null
    token.value = null
    localStorage.removeItem('auth_token')
    
    // Redirect to login page if needed
    window.location.href = '/login' || '/'
  }
  
  return {
    // State
    user,
    token,
    isAuthenticated,
    
    // Actions
    login,
    register,
    fetchCurrentUser,
    logout
  }
}, {
  persist: true // Pinia plugin-persist will save to localStorage automatically (if configured)
})
