import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient from '../api/client'

export interface Booking {
  id: number
  customer_name: string
  instructor_name: string
  schedule_date: string
  start_time: string
  end_time: string
  status: 'confirmed' | 'cancelled' | 'no_show'
}

interface BookingState {
  bookings: Booking[]
  isLoading: boolean
  currentBookingId: number | null
  error: string | null
  isConflictError: boolean // Flag for double-booking errors
}

export const useBookingStore = defineStore('bookings', () => {
  // State
  const bookings = ref<Booking[]>([])
  const isLoading = ref(false)
  const currentBookingId = ref<number | null>(null)
  const error = ref<string | null>(null)
  const isConflictError = ref(false)
  
  // Computed properties
  const confirmedBookings = computed(() => 
    bookings.value.filter(b => b.status === 'confirmed')
  )
  
  const upcomingBookings = computed(() => {
    const today = new Date().toISOString().split('T')[0]
    return confirmedBookings.value.filter(b => b.schedule_date >= today)
  })
  
  // Actions
  async function createBooking(
    scheduleId: number,
    customerName: string,
    customerPhone: string,
    notes?: string
  ): Promise<number> {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await apiClient.post('/bookings', {
        schedule_id: scheduleId,
        customer_name: customerName,
        customer_phone: customerPhone,
        notes: notes || ''
      })
      
      currentBookingId.value = response.data.booking_id
      
      // Refresh bookings list after successful creation
      await fetchBookings()
      
      return response.data.booking_id
    } catch (err) {
      const axiosError = err as any
      
      if (axiosError.isConflict) {
        isConflictError.value = true
        error.value = axiosError.message || '预约失败：时间 slot 已满或重复预约'
        
        // Don't throw - let the component handle conflict gracefully
        return -1
      } else {
        error.value = '预约提交失败，请稍后重试'
        throw err
      }
    } finally {
      isLoading.value = false
    }
  }
  
  async function fetchBookings(phone: string): Promise<void> {
    isLoading.value = true
    
    try {
      const response = await apiClient.get('/bookings', { params: { phone } })
      bookings.value = response.data as Booking[]
    } catch (err) {
      error.value = '获取预约记录失败'
      console.error('Failed to fetch bookings:', err)
    } finally {
      isLoading.value = false
    }
  }
  
  async function cancelBooking(bookingId: number): Promise<void> {
    try {
      await apiClient.delete(`/bookings/${bookingId}`)
      
      // Update local state immediately for better UX
      const index = bookings.value.findIndex(b => b.id === bookingId)
      if (index !== -1) {
        bookings.value[index].status = 'cancelled'
      }
    } catch (err) {
      error.value = '取消预约失败，请稍后重试'
      throw err
    }
  }
  
  function clearError(): void {
    error.value = null
    isConflictError.value = false
    currentBookingId.value = null
  }
  
  return {
    // State
    bookings,
    confirmedBookings,
    upcomingBookings,
    isLoading,
    currentBookingId,
    error,
    isConflictError,
    
    // Actions
    createBooking,
    fetchBookings,
    cancelBooking,
    clearError
  }
}, {
  persist: true // Persist bookings across page refreshes (optional)
})
