import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useBookingStore = defineStore('booking', () => {
  // State
  const bookings = ref([])
  const instructors = ref([])
  const schedules = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Actions
  async function fetchBookings(phone) {
    loading.value = true
    try {
      const response = await fetch(`/api/v1/bookings?phone=${phone}`)
      if (!response.ok) throw new Error('Failed to fetch bookings')
      bookings.value = await response.json()
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  async function createBooking(bookingData) {
    loading.value = true
    try {
      const response = await fetch('/api/v1/bookings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(bookingData)
      })
      if (!response.ok) throw new Error('Failed to create booking')
      const newBooking = await response.json()
      bookings.value.push(newBooking)
      return newBooking
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function cancelBooking(bookingId) {
    try {
      const response = await fetch(`/api/v1/studio/bookings/${bookingId}`, {
        method: 'DELETE'
      })
      if (!response.ok) throw new Error('Failed to cancel booking')
      bookings.value = bookings.value.filter(b => b.id !== bookingId)
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  async function fetchInstructors(date = null) {
    const url = date ? `/api/v1/instructors?date=${date}` : '/api/v1/instructors'
    try {
      const response = await fetch(url)
      if (!response.ok) throw new Error('Failed to fetch instructors')
      instructors.value = await response.json()
    } catch (err) {
      error.value = err.message
    }
  }

  async function fetchSchedules(date = null, instructorId = null) {
    const params = new URLSearchParams()
    if (date) params.append('date', date)
    if (instructorId) params.append('instructor_id', instructorId)
    
    try {
      const response = await fetch(`/api/v1/schedules?${params}`)
      if (!response.ok) throw new Error('Failed to fetch schedules')
      schedules.value = await response.json()
    } catch (err) {
      error.value = err.message
    }
  }

  return {
    bookings,
    instructors,
    schedules,
    loading,
    error,
    fetchBookings,
    createBooking,
    cancelBooking,
    fetchInstructors,
    fetchSchedules
  }
})
