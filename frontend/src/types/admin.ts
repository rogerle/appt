// Admin-related TypeScript types matching backend schemas

export interface DashboardStats {
  total_bookings_today: number
  total_bookings_week: number
  total_bookings_month: number
  active_instructors: number
  available_slots: number
  revenue_this_month: number
}

export interface RecentBookingResponse {
  id: number
  customer_name: string
  customer_phone: string
  booking_date: Date | null  // Changed from 'date' to avoid conflicts
  start_time: any | null    // time type not available in JS
  end_time: any | null      // time type not available in JS
  class_type: string
  instructor_name: string
  status: string            // pending, confirmed, cancelled, completed
  created_at: Date
  notes?: string
}

export interface InstructorResponse {
  id: number
  name: string
  phone: string
  studio_name: string
  bio?: string | null
  experience_years: number
  specialties: string[]
  is_active: boolean
  created_at: Date
  schedules_count?: number
  bookings_count?: number
}

export interface ScheduleResponse {
  id: number
  instructor_id: number
  date: Date
  start_time: any
  end_time: any
  max_bookings: number     // Changed from max_participants
  instructor_name?: string | null
  confirmed_bookings_count?: number
  pending_bookings_count?: number
  is_active?: boolean
}

export interface UserResponse {
  id: number
  email: string
  username: string
  role: 'user' | 'admin'
  is_active: boolean
  created_at: Date
  last_login_at?: Date | null
  booking_count?: number
}
