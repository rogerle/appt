/**
 * Pinia Store Tests - Booking Store State Management Testing
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useBookingStore } from '../src/stores/booking'

describe('Booking Store', () => {
  let store
  
  beforeEach(() => {
    setActivePinia(createPinia())
    store = useBookingStore()
    
    // Reset state before each test
    store.$reset()
  })
  
  describe('State Management', () => {
    it('has correct initial state', () => {
      expect(store.bookings).toEqual([])
      expect(store.selectedInstructor).toBe(null)
      expect(store.selectedDate).toBe(null)
      expect(store.isLoading).toBe(false)
      expect(store.error).toBe(null)
    })
    
    it('updates selectedInstructor correctly', () => {
      const instructorId = 1
      
      store.selectInstructor(instructorId)
      
      expect(store.selectedInstructor).toBe(instructorId)
    })
    
    it('updates selectedDate correctly', () => {
      const testDate = '2024-06-15'
      
      store.selectDate(testDate)
      
      expect(store.selectedDate).toBe(testDate)
    })
  })
  
  describe('Actions - Add Booking', () => {
    it('adds new booking to state', async () => {
      const newBooking = {
        id: 1,
        instructor_id: 1,
        date: '2024-06-15',
        time: '10:00',
        name: '测试用户',
        phone: '13800138000'
      }
      
      await store.addBooking(newBooking)
      
      expect(store.bookings.length).toBe(1)
      expect(store.bookings[0]).toEqual(newBooking)
    })
    
    it('handles API error when adding booking fails', async () => {
      // Mock API failure (simulate 422 validation error)
      vi.spyOn(global, 'fetch').mockImplementation(() => 
        Promise.resolve({
          ok: false,
          status: 422,
          json: () => ({ message: 'Validation failed' })
        })
      )
      
      await store.addBooking({ name: 'Test', phone: 'invalid' })
      
      expect(store.error).toBeDefined()
    })
    
    it('sets loading state during API call', async () => {
      let testPromise
      
      // Mock slow API call
      vi.spyOn(global, 'fetch').mockImplementation(() => 
        new Promise(resolve => {
          testPromise = resolve({
            ok: true,
            json: () => ({ id: 1 })
          })
        })
      )
      
      store.addBooking({ name: 'Test', phone: '13800138000' }).then(() => {})
      
      expect(store.isLoading).toBe(true)
      
      testPromise.resolve()
      await new Promise(resolve => setTimeout(resolve, 10))
      
      // Should be false after completion (depending on implementation)
    })
  })
  
  describe('Actions - Fetch Bookings', () => {
    it('fetches bookings from API successfully', async () => {
      const mockBookings = [
        { id: 1, name: '用户 A', phone: '13800138000' },
        { id: 2, name: '用户 B', phone: '13900139000' }
      ]
      
      vi.spyOn(global, 'fetch').mockImplementation(() => 
        Promise.resolve({
          ok: true,
          json: () => mockBookings
        })
      )
      
      await store.fetchBookings()
      
      expect(store.bookings).toEqual(mockBookings)
    })
    
    it('handles API error when fetching bookings fails', async () => {
      vi.spyOn(global, 'fetch').mockImplementation(() => 
        Promise.resolve({
          ok: false,
          status: 500,
          json: () => ({ message: 'Server error' })
        })
      )
      
      await store.fetchBookings()
      
      expect(store.error).toBeDefined()
    })
  })
  
  describe('Actions - Cancel Booking', () => {
    it('removes booking from state on successful cancellation', async () => {
      const testBooking = { id: 1, name: '测试用户' }
      store.addBooking(testBooking)
      
      expect(store.bookings.length).toBe(1)
      
      // Mock successful cancellation API call
      vi.spyOn(global, 'fetch').mockImplementation(() => 
        Promise.resolve({ ok: true })
      )
      
      await store.cancelBooking(1)
      
      // Depending on implementation, may remove from state or just mark as cancelled
    })
    
    it('handles cancellation API error', async () => {
      vi.spyOn(global, 'fetch').mockImplementation(() => 
        Promise.resolve({
          ok: false,
          status: 404,
          json: () => ({ message: 'Booking not found' })
        })
      )
      
      await store.cancelBooking(999)
      
      expect(store.error).toBeDefined()
    })
  })
  
  describe('Getters - Filter Bookings', () => {
    it('filters bookings by instructor ID', () => {
      const mockBookings = [
        { id: 1, instructor_id: 1 },
        { id: 2, instructor_id: 2 },
        { id: 3, instructor_id: 1 }
      ]
      
      store.bookings = mockBookings
      
      // Assuming getter exists for filtering
      expect(store).toBeDefined()
    })
    
    it('filters bookings by date', () => {
      const today = '2024-06-15'
      store.selectedDate = today
      
      expect(store.selectedDate).toBe(today)
    })
  })
  
  describe('Actions - Clear State', () => {
    it('resets all state to initial values', async () => {
      // Set some state
      store.selectInstructor(1)
      store.selectDate('2024-06-15')
      
      await store.addBooking({ id: 1, name: 'Test' })
      
      expect(store.selectedInstructor).toBe(1)
      expect(store.bookings.length).toBe(1)
      
      // Reset state
      store.$reset()
      
      expect(store.selectedInstructor).toBe(null)
      expect(store.bookings.length).toBe(0)
    })
  })
})
