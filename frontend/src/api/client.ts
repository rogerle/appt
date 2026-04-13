import axios from 'axios'

// Create axios instance with default configuration
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  timeout: 10000, // 10 seconds
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor - Add auth token to requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - Handle errors globally
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid - logout user
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    } else if (error.response?.status === 409 && error.config?.url?.includes('/bookings')) {
      // Handle booking conflicts gracefully
      const conflictData = error.response.data
      
      return Promise.reject({
        ...error,
        isConflict: true,
        message: conflictData.detail || '预约冲突：时间 slot 已满或重复预约'
      })
    } else if (error.code === 'ECONNABORTED') {
      // Network timeout - user-friendly error
      return Promise.reject({
        ...error,
        message: '请求超时，请检查网络连接后重试'
      })
    }
    
    return Promise.reject(error)
  }
)

export default apiClient
