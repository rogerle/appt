<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { bookingApi } from '../../api/services'

const router = useRouter()

// State
const bookings = ref<any[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const phoneInput = ref('')
const showPhoneInput = ref(true)

onMounted(() => {
  // Check if user has entered phone before
  const savedPhone = localStorage.getItem('my_bookings_phone')
  if (savedPhone) {
    phoneInput.value = savedPhone
    loadBookings(savedPhone)
  }
})

async function loadBookings(phone: string) {
  loading.value = true
  error.value = null
  
  try {
    bookings.value = await bookingApi.getMyBookings(phone)
    
    // Save phone for next visit
    localStorage.setItem('my_bookings_phone', phone)
    showPhoneInput.value = false
    
    console.log('Loaded bookings:', bookings.value.length)
  } catch (err: any) {
    console.error('Failed to load bookings:', err)
    error.value = '加载预约记录失败，请检查电话号码是否正确'
  } finally {
    loading.value = false
  }
}

async function submitPhone() {
  if (!phoneInput.value || phoneInput.value.length < 11) {
    alert('请输入有效的手机号码')
    return
  }
  
  await loadBookings(phoneInput.value)
}

async function cancelBooking(bookingId: number, bookingName: string) {
  if (!confirm(`确定要取消预约：${bookingName} 吗？`)) {
    return
  }
  
  try {
    await bookingApi.cancelBooking(bookingId)
    
    // Remove from list optimistically
    bookings.value = bookings.value.filter(b => b.id !== bookingId)
    alert('预约已取消')
    
    // If no more bookings, show phone input again
    if (bookings.value.length === 0) {
      showPhoneInput.value = true
      localStorage.removeItem('my_bookings_phone')
    }
  } catch (err: any) {
    console.error('Failed to cancel booking:', err)
    alert('取消预约失败：' + (err.message || '请稍后重试'))
  }
}

function getStatusBadgeClass(status: string) {
  switch (status) {
    case 'confirmed':
      return 'bg-green-100 text-green-800 border-green-300'
    case 'cancelled':
      return 'bg-red-100 text-red-800 border-red-300'
    case 'no_show':
      return 'bg-gray-100 text-gray-800 border-gray-300'
    default:
      return 'bg-blue-100 text-blue-800 border-blue-300'
  }
}

function getStatusText(status: string) {
  switch (status) {
    case 'confirmed':
      return '已确认'
    case 'cancelled':
      return '已取消'
    case 'no_show':
      return '未到场'
    default:
      return status
  }
}

function formatDate(dateStr: string) {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', { 
    year: 'numeric', 
    month: '2-digit', 
    day: '2-digit' 
  })
}

</script>

<template>
  <div class="my-bookings-page">
    <h1 class="text-2xl font-bold text-primary-800 mb-6">我的预约</h1>
    
    <!-- Phone Input Form -->
    <div v-if="showPhoneInput" class="card max-w-md mx-auto">
      <h2 class="text-xl font-semibold text-primary-700 mb-4">查询预约记录</h2>
      
      <p class="mb-4 text-gray-600 text-sm">请输入您预约时使用的手机号码</p>
      
      <div v-if="error" class="bg-red-50 text-red-700 p-3 rounded-lg mb-4">
        {{ error }}
      </div>
      
      <label class="block text-sm font-medium text-gray-700 mb-2">手机号码</label>
      <input 
        type="tel" 
        v-model="phoneInput"
        placeholder="请输入 11 位手机号"
        maxlength="11"
        class="w-full px-4 py-3 rounded-lg border border-primary-300 focus:ring-2 focus:ring-accent-light focus:border-transparent transition-all duration-200 text-lg mb-4"
      />
      
      <button 
        @click="submitPhone"
        :disabled="loading"
        class="w-full py-3 px-4 rounded-lg bg-accent-dark text-white font-bold hover:bg-accent-green transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
      >
        <span v-if="loading" class="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></span>
        {{ loading ? '查询中...' : '查询预约' }}
      </button>
    </div>

    <!-- Bookings List -->
    <div v-else>
      <!-- Loading state -->
      <div v-if="loading" class="card text-center py-8">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-accent-dark mx-auto"></div>
        <p class="mt-4 text-gray-600">加载中...</p>
      </div>
      
      <!-- Error state -->
      <div v-else-if="error" class="card">
        <div class="bg-red-50 text-red-700 p-4 rounded-lg mb-4">
          {{ error }}
        </div>
        <button 
          @click="showPhoneInput = true"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
        >
          重新输入
        </button>
      </div>
      
      <!-- Empty state -->
      <div v-else-if="bookings.length === 0" class="card text-center py-8">
        <p class="text-gray-500 mb-4">暂无预约记录</p>
        <button 
          @click="router.push('/booking')"
          class="px-6 py-3 bg-accent-dark text-white rounded-lg font-bold hover:bg-accent-green transition-all duration-200 inline-block"
        >
          立即预约
        </button>
      </div>
      
      <!-- Bookings list -->
      <div v-else class="space-y-4">
        <div class="flex justify-between items-center mb-4">
          <p class="text-gray-600">手机号：{{ phoneInput }}</p>
          <button 
            @click="showPhoneInput = true"
            class="text-sm text-primary-600 hover:text-primary-800"
          >
            修改号码
          </button>
        </div>
        
        <!-- Booking Cards -->
        <div 
          v-for="booking in bookings" 
          :key="booking.id"
          class="card p-5 transition-all duration-200 hover:shadow-md"
        >
          <div class="flex justify-between items-start mb-3">
            <div>
              <h3 class="font-bold text-lg text-primary-800">{{ booking.instructor_name }}</h3>
              <p class="text-sm text-gray-600 mt-1">
                📅 {{ formatDate(booking.schedule_date) }} | 
                ⏰ {{ booking.start_time }} - {{ booking.end_time }}
              </p>
            </div>
            
            <span 
              class="px-3 py-1 rounded-full text-xs font-semibold border"
              :class="getStatusBadgeClass(booking.status)"
            >
              {{ getStatusText(booking.status) }}
            </span>
          </div>
          
          <div class="flex justify-between items-center pt-3 border-t border-gray-200">
            <p class="text-sm text-gray-600">预约人：{{ booking.customer_name }}</p>
            
            <button 
              v-if="booking.status === 'confirmed'"
              @click="cancelBooking(booking.id, booking.customer_name)"
              class="px-4 py-2 bg-red-100 text-red-700 rounded-lg text-sm font-medium hover:bg-red-200 transition-all duration-200"
            >
              取消预约
            </button>
          </div>
        </div>
        
        <!-- CTA at bottom -->
        <div class="text-center pt-4">
          <button 
            @click="router.push('/booking')"
            class="px-8 py-3 bg-accent-dark text-white rounded-lg font-bold hover:bg-accent-green transition-all duration-200 inline-block"
          >
            预约新课程
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped></style>
