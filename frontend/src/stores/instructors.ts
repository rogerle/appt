import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient from '../api/client'

export interface Instructor {
  id: number
  name: string
  description?: string
  avatar_url?: string
  is_active: boolean
  created_at: string
}

export interface TimeSlot {
  start_time: string // "10:00" format
  end_time: string   // "11:00" format
  available_spots: number
}

export interface InstructorWithSlots extends Instructor {
  available_slots?: TimeSlot[]
}

interface InstructorState {
  instructors: InstructorWithSlots[]
  isLoading: boolean
  selectedDate: Date | null
  error: string | null
}

export const useInstructorStore = defineStore('instructors', () => {
  // State
  const instructors = ref<InstructorWithSlots[]>([])
  const isLoading = ref(false)
  const selectedDate = ref<Date | null>(null)
  const error = ref<string | null>(null)
  
  // Computed properties
  const activeInstructors = computed(() => 
    instructors.value.filter(i => i.is_active)
  )
  
  const instructorById = (id: number): InstructorWithSlots | undefined => {
    return instructors.value.find(i => i.id === id)
  }
  
  // Actions
  async function fetchInstructors(dateParam?: Date): Promise<void> {
    isLoading.value = true
    error.value = null
    
    try {
      const params: Record<string, string | boolean> = {}
      
      if (dateParam) {
        selectedDate.value = dateParam
        params.date = dateParam.toISOString().split('T')[0]
      }
      
      if (!params.date && !selectedDate.value) {
        // Default to today's date
        const today = new Date()
        selectedDate.value = today
        params.date = today.toISOString().split('T')[0]
      }
      
      const response = await apiClient.get('/instructors', { params })
      instructors.value = response.data as InstructorWithSlots[]
    } catch (err) {
      error.value = '获取教练列表失败，请稍后重试'
      console.error('Failed to fetch instructors:', err)
    } finally {
      isLoading.value = false
    }
  }
  
  async function fetchInstructorById(id: number): Promise<InstructorWithSlots> {
    try {
      const response = await apiClient.get(`/instructors/${id}`)
      return response.data as InstructorWithSlots
    } catch (err) {
      throw new Error('获取教练信息失败')
    }
  }
  
  function clearError(): void {
    error.value = null
  }
  
  return {
    // State
    instructors,
    activeInstructors,
    isLoading,
    selectedDate,
    error,
    
    // Computed helpers
    instructorById,
    
    // Actions
    fetchInstructors,
    fetchInstructorById,
    clearError
  }
}, {
  persist: true // Persist selected date across page refreshes
})
