<script setup>
import { ref, onMounted } from 'vue'
import { useBookingStore } from '../stores/booking'
import Header from '../components/common/Header.vue'

const store = useBookingStore()

// Reactive state
const phoneInput = ref('')
const userBookings = ref([])
const loading = ref(false)

// Methods
async function fetchMyBookings() {
  if (!phoneInput.value || phoneInput.value.length !== 11) {
    alert('请输入正确的 11 位手机号')
    return
  }

  loading.value = true
  try {
    const bookings = await store.fetchBookings(phoneInput.value)
    userBookings.value = bookings
  } catch (error) {
    console.error('Failed to fetch bookings:', error)
    alert('获取预约失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

async function cancelBooking(bookingId, bookingDate) {
  const today = new Date().toISOString().split('T')[0]
  
  if (bookingDate < today) {
    alert('无法取消已过期的预约')
    return
  }

  if (!confirm('确定要取消这个预约吗？')) {
    return
  }

  try {
    await store.cancelBooking(bookingId)
    
    // Remove from local list immediately for better UX
    userBookings.value = userBookings.value.filter(b => b.id !== bookingId)
    
    alert('预约已取消')
  } catch (error) {
    console.error('Failed to cancel booking:', error)
    alert('取消预约失败，请稍后重试')
  }
}

// Lifecycle
onMounted(() => {
  // Auto-fetch if phone is in localStorage (for demo convenience)
  const savedPhone = localStorage.getItem('user_phone')
  if (savedPhone && savedPhone.length === 11) {
    phoneInput.value = savedPhone
    fetchMyBookings()
  }
})

function savePhoneAndFetch() {
  localStorage.setItem('user_phone', phoneInput.value)
  fetchMyBookings()
}
</script>

<template>
  <div class="min-h-screen bg-gray-light">
    <Header />

    <!-- Hero Section -->
    <section class="bg-black text-white py-16 px-4">
      <div class="max-w-4xl mx-auto text-center">
        <h1 class="text-display-hero mb-4">我的预约</h1>
        <p class="text-xl leading-relaxed">查询和管理您的瑜伽课程预约</p>
      </div>
    </section>

    <!-- Main Content -->
    <main class="max-w-4xl mx-auto px-4 py-12">
      <!-- Phone Input Section -->
      <section class="mb-8 bg-white rounded-lg p-6 shadow-sm">
        <label for="phone" class="block text-lg font-medium mb-3">请输入您的手机号</label>
        <div class="flex gap-3">
          <input 
            id="phone"
            v-model="phoneInput"
            type="tel"
            placeholder="11 位手机号码"
            maxlength="11"
            class="input-field flex-1"
          />
          <button 
            @click="savePhoneAndFetch"
            :disabled="loading || phoneInput.length !== 11"
            class="btn-primary py-3 px-8 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {{ loading ? '查询中...' : '查询' }}
          </button>
        </div>
      </section>

      <!-- Bookings List -->
      <section v-if="userBookings.length > 0">
        <h3 class="text-section-heading mb-6 flex items-center justify-between">
          <span>预约记录</span>
          <span class="text-caption text-secondary">{{ userBookings.length }}条</span>
        </h3>

        <div class="space-y-4">
          <div 
            v-for="booking in userBookings" 
            :key="booking.id"
            class="card transition-all hover:shadow-md"
          >
            <!-- Booking Header -->
            <div class="flex items-start justify-between mb-4">
              <div>
                <h4 class="text-xl font-semibold">{{ booking.instructor_name || '教练' }}</h4>
                <p class="text-secondary text-sm mt-1">{{ booking.date }} {{ booking.time_slot_start }} - {{ booking.time_slot_end }}</p>
              </div>
              <span 
                :class="[
                  'px-3 py-1 rounded-full text-xs font-medium',
                  booking.status === 'confirmed' ? 'bg-green-100 text-green-700' :
                  booking.status === 'completed' ? 'bg-blue-100 text-blue-700' :
                  booking.status === 'cancelled' ? 'bg-gray-200 text-gray-600' :
                  'bg-yellow-100 text-yellow-700'
                ]"
              >
                {{ 
                  booking.status === 'confirmed' ? '已确认' :
                  booking.status === 'completed' ? '已完成' :
                  booking.status === 'cancelled' ? '已取消' :
                  '待处理'
                }}
              </span>
            </div>

            <!-- Booking Details -->
            <div class="flex items-center gap-4 text-sm mb-4">
              <div class="flex items-center gap-2">
                <svg class="w-5 h-5 text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                <span>{{ booking.name }}</span>
              </div>
            </div>

            <!-- Action Buttons -->
            <div v-if="booking.status === 'confirmed'" class="flex gap-3">
              <button 
                @click="cancelBooking(booking.id, booking.date)"
                class="btn-secondary py-2 px-6 rounded-lg text-sm transition-colors"
              >
                取消预约
              </button>
            </div>

            <!-- Divider -->
            <div v-if="userBookings.indexOf(booking) !== userBookings.length - 1" 
                 class="border-t border-gray-200 mt-4 pt-4">
            </div>
          </div>
        </div>
      </section>

      <!-- Empty State -->
      <div v-if="!loading && phoneInput.length === 11 && userBookings.length === 0" 
           class="text-center py-12 bg-white rounded-lg">
        <svg class="w-16 h-16 text-secondary mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        <p class="text-lg text-secondary mb-2">暂无预约记录</p>
        <button @click="$router.push('/')" class="btn-primary py-3 px-8 rounded-lg">立即预约</button>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <svg class="animate-spin h-10 w-10 text-blue-500 mx-auto" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <p class="text-secondary mt-4">查询中...</p>
      </div>

      <!-- Hint for first-time users -->
      <div v-if="!loading && phoneInput.length === 0" 
           class="bg-white rounded-lg p-6 text-center">
        <p class="text-secondary mb-4">首次使用请输入手机号查询预约记录</p>
        <button @click="savePhoneAndFetch" disabled class="btn-primary py-3 px-8 rounded-lg opacity-50 cursor-not-allowed">
          输入手机号后点击查询
        </button>
      </div>
    </main>

    <!-- Footer -->
    <footer class="mt-auto py-8 text-center text-caption text-secondary">
      © 2026 Appt - Yoga Studio Scheduler
    </footer>
  </div>
</template>

<style scoped>
/* Additional component-specific styles if needed */
</style>
