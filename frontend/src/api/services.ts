import apiClient from './client'

// ==================== Type Definitions ====================

export interface Instructor {
  id: number
  name: string
  description?: string
  avatar_url?: string
  is_active: boolean
}

export interface TimeSlot {
  start_time: string
  end_time: string
  available_spots: number
}

export interface InstructorWithSlots extends Instructor {
  available_slots: TimeSlot[]
}

export interface ScheduleSlot {
  id: number
  start_time: string
  end_time: string
  available_spots: number
}

export interface BookingData {
  schedule_id: number
  customer_name: string
  customer_phone: string
  notes?: string
}

export interface BookingResponse {
  success: boolean
  message: string
  booking_id: number
}

export interface UserBooking {
  id: number
  customer_name: string
  customer_phone_masked: string
  instructor_name: string
  schedule_date: string
  start_time: string
  end_time: string
  status: string
}

// ==================== API Services ====================

export const instructorApi = {
  // Get all instructors with optional date filter
  getAll: async (date?: string): Promise<InstructorWithSlots[]> => {
    const params = date ? { date } : undefined
    const response = await apiClient.get('/instructors', { params })
    return response.data
  },

  // Get specific instructor by ID
  getById: async (id: number): Promise<Instructor> => {
    const response = await apiClient.get(`/instructors/${id}`)
    return response.data
  }
}

export const scheduleApi = {
  // Get available time slots for a date, optionally filtered by instructor
  getAvailableSlots: async (date: string, instructorId?: number): Promise<ScheduleSlot[]> => {
    const params: Record<string, any> = { date }
    if (instructorId) {
      params.instructor_id = instructorId
    }
    const response = await apiClient.get('/schedules', { params })
    return response.data
  }
}

export const bookingApi = {
  // Create a new booking
  createBooking: async (data: BookingData): Promise<BookingResponse> => {
    const response = await apiClient.post('/bookings', data)
    return response.data
  },

  // Get user's bookings by phone number
  getMyBookings: async (phone: string): Promise<UserBooking[]> => {
    const response = await apiClient.get('/bookings', { params: { phone } })
    return response.data
  },

  // Cancel a booking
  cancelBooking: async (bookingId: number): Promise<void> => {
    await apiClient.delete(`/bookings/${bookingId}`)
  }
}
