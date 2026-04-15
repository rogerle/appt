import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient from '../api/client'

export interface User {
  id: number
  email: string
  username: string
  role: 'user' | 'admin'
  is_active: boolean
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('access_token'))
  
  // Computed properties
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  
  // Actions
  
  /**
   * Login with email and password
   * @param email - User email address 
   * @param password - Password
   */
  async function login(email: string, password: string): Promise<void> {
    try {
      const response = await apiClient.post('/auth/login', {
        email: email,
        password: password
      })
      
      token.value = response.data.access_token
      localStorage.setItem('access_token', token.value)
      
      // Fetch user info after login
      await fetchCurrentUser()
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    }
  }
  
  /**
   * Register new account with email and password
   * @param email - User email address
   * @param username - Username (3-100 chars, unique)
   * @param password - Password (min 8 chars)
   */
  async function register(email: string, username: string, password: string): Promise<void> {
    try {
      const response = await apiClient.post('/auth/register', {
        email: email,
        username: username,
        password: password
      })
      
      // Auto-login after registration
      token.value = response.data.access_token
      localStorage.setItem('access_token', token.value)
      
      // Fetch user info
      await fetchCurrentUser()
    } catch (error) {
      console.error('Registration failed:', error)
      throw error
    }
  }
  
  /**
   * Fetch current user information from /auth/me endpoint
   */
  async function fetchCurrentUser(): Promise<void> {
    try {
      const response = await apiClient.get('/auth/me')
      user.value = response.data as User
    } catch (error) {
      console.error('Failed to fetch user info:', error)
      // Clear token if current user fetch fails
      logout()
    }
  }
  
  /**
   * Logout - clear all auth data and redirect to login page
   */
  function logout(): void {
    // Optional: call backend logout API for audit/logging
    apiClient.post('/auth/logout').catch(() => {})
    
    user.value = null
    token.value = null
    localStorage.removeItem('access_token')
    
    // Redirect to homepage (not /login for better UX - users can click login button)
    window.location.href = '/'
  }
  
  /**
   * Set token directly (e.g., from URL parameter or deep link)
   */
  function setToken(newToken: string): void {
    token.value = newToken
    localStorage.setItem('access_token', newToken)
  }
  
  return {
    // State
    user,
    token,
    isAuthenticated,
    isAdmin,
    
    // Actions
    login,
    register,
    fetchCurrentUser,
    logout,
    setToken
  }
}, {
  persist: {
    key: 'appt-auth',
    storage: localStorage,
    paths: ['token'] // Only persist token, not user (fetch on each load)
  }
})
