<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import InstructorCard from '../components/InstructorCard.vue'
import { instructorApi, scheduleApi, bookingApi } from '../api/services'

const router = useRouter()

// Step tracking (1: date, 2: instructor, 3: time slot, 4: form)
const currentStep = ref(1)

// Form state
const selectedDate = ref('')
const selectedInstructorId = ref<number | null>(null)
const selectedTimeSlot = ref<{ start: string; end: string; scheduleId?: number } | null>(null)

// Customer info
const customerName = ref('')
const customerPhone = ref('')
const customerNote = ref('')

// Loading state
const loading = ref(false)
const instructors = ref<any[]>([])
const timeSlots = ref<any[]>([])
const error = ref<string | null>(null)

onMounted(() => {
  // Initialize date to today
  selectedDate.value = new Date().toISOString().split('T')[0]
})

// Watch for date changes to reload instructors
watch(selectedDate, async (newDate) => {
  if (newDate && currentStep.value >= 2) {
    await loadInstructors(newDate)
  }
})



function prevStep() {
  if (currentStep.value > 1) currentStep.value--
}

async function submitBooking() {
  if (!customerName.value || !customerPhone.value) {
    return alert('请填写姓名和电话')
  }
  
  // Use the stored schedule ID directly, or find from timeSlots
  let scheduleId: number | undefined
  
  if (selectedTimeSlot.value?.scheduleId) {
    // New approach: use stored ID
    scheduleId = selectedTimeSlot.value.scheduleId
  } else {
    // Fallback: find by time comparison
    const selectedSlot = timeSlots.value.find(
      slot => formatTime(slot.start_time) === formatTime(selectedTimeSlot.value!.start) &&
              formatTime(slot.end_time) === formatTime(selectedTimeSlot.value!.end)
    )
    scheduleId = selectedSlot?.id
  }
  
  if (!scheduleId) {
    return alert('未找到选中的时间段，请重新选择')
  }
  
  loading.value = true
  error.value = null
  
  try {
    const response = await bookingApi.createBooking({
      schedule_id: scheduleId,
      customer_name: customerName.value,
      customer_phone: customerPhone.value,
      notes: customerNote.value || undefined
    })
    
    alert(response.message || '预约成功！')
    router.push('/my-bookings')
  } catch (err: any) {
    console.error('Booking failed:', err)
    
    // Handle specific error types
    if (err.isConflict) {
      alert(err.message || '预约冲突：该时段已满或您已有预约')
    } else if (err.response?.status === 404) {
      alert('时间段不存在或不可用')
    } else {
      alert('预约失败：' + (err.message || '请稍后重试'))
    }
  } finally {
    loading.value = false
  }
}

// Load instructors for selected date
async function loadInstructors(dateStr?: string) {
  const dateToLoad = dateStr || selectedDate.value
  if (!dateToLoad) return
  
  loading.value = true
  error.value = null
  
  try {
    instructors.value = await instructorApi.getAll(dateToLoad)
    console.log('Loaded instructors:', instructors.value.length)
  } catch (err: any) {
    console.error('Failed to load instructors:', err)
    error.value = '加载教练列表失败，请重试'
  } finally {
    loading.value = false
  }
}

// Load time slots for selected instructor and date
async function loadTimeSlots() {
  if (!selectedInstructorId.value || !selectedDate.value) {
    console.log('⚠️ loadTimeSlots: missing data - instructorId:', selectedInstructorId.value, 'date:', selectedDate.value)
    return
  }
  
  loading.value = true
  error.value = null
  
  try {
    timeSlots.value = await scheduleApi.getAvailableSlots(
      selectedDate.value,
      selectedInstructorId.value
    )
    console.log('✅ Loaded time slots:', timeSlots.value.length)
    if (timeSlots.value.length > 0) {
      console.log('📋 First slot data:', timeSlots.value[0])
      console.log('🔢 available_spots type:', typeof timeSlots.value[0].available_spots)
      console.log('✓ Available slots count:', timeSlots.value.filter(s => isSlotAvailable(s)).length)
    }
  } catch (err: any) {
    console.error('❌ Failed to load time slots:', err)
    error.value = '加载时间段失败，请重试'
  } finally {
    loading.value = false
  }
}

// Helper functions for time slot handling
function formatTime(timeStr: string): string {
  // Convert "HH:MM:SS" to "HH:MM"
  if (!timeStr) return ''
  const parts = timeStr.split(':')
  if (parts.length >= 2) {
    return `${parts[0]}:${parts[1]}`
  }
  return timeStr
}

function isSlotSelected(slot: any): boolean {
  if (!selectedTimeSlot.value) return false
  // Compare using formatted times to handle "HH:MM:SS" vs "HH:MM"
  return formatTime(selectedTimeSlot.value.start) === formatTime(slot.start_time) &&
         formatTime(selectedTimeSlot.value.end) === formatTime(slot.end_time)
}

function isSlotAvailable(slot: any): boolean {
  // Handle various data types for available_spots (string, number, etc.)
  let spots = 0
  if (slot.available_spots !== undefined && slot.available_spots !== null) {
    // Convert to number regardless of input type (handles string like "1")
    spots = parseInt(String(slot.available_spots), 10)
  }
  return !isNaN(spots) && spots > 0
}

function handleSlotClick(slot: any) {
  console.log('🕐 Slot clicked:', slot)
  console.log('Available spots:', slot.available_spots, typeof slot.available_spots)
  console.log('Is available?', isSlotAvailable(slot))
  
  if (!isSlotAvailable(slot)) {
    alert('该时段已约满，请选择其他时间')
    return
  }
  // Store the full time string from API (with seconds)
  selectedTimeSlot.value = { 
    start: slot.start_time, 
    end: slot.end_time,
    scheduleId: slot.id  // Also store ID for easier lookup
  }
  console.log('✅ Selected:', selectedTimeSlot.value)
}

// Override nextStep to trigger data loading
async function nextStep() {
  console.log('🔽 nextStep called - from step:', currentStep.value)
  
  if (currentStep.value === 1 && !selectedDate.value) return alert('请选择日期')
  if (currentStep.value === 2 && !selectedInstructorId.value) return alert('请选择教练')
  if (currentStep.value === 3 && !selectedTimeSlot.value) return alert('请选择时间段')
  
  // Load data when moving to next step
  if (currentStep.value === 1) {
    console.log('👨‍🏫 Loading instructors for date:', selectedDate.value)
    await loadInstructors()
  } else if (currentStep.value === 2) {
    console.log('⏰ Loading time slots for instructor:', selectedInstructorId.value, 'date:', selectedDate.value)
    await loadTimeSlots()
  }
  
  currentStep.value++
  console.log('➡️ Moved to step:', currentStep.value)
}
</script>

<template>
  <div class="booking-page">
    <h1 class="text-2xl font-bold text-primary-800 mb-6">预约瑜伽课程</h1>
    
    <!-- Step Progress Indicator -->
    <div class="flex items-center justify-between mb-8 bg-white rounded-lg p-4 shadow-sm">
      <template v-for="step in 4" :key="step">
        <div 
          class="flex flex-col items-center flex-1"
          :class="{ 'opacity-60': step > currentStep }"
        >
          <div 
            class="w-12 h-12 rounded-full flex items-center justify-center text-white font-bold mb-2 transition-all duration-300"
            :class="currentStep >= step ? 'bg-accent-dark scale-110' : 'bg-primary-300'"
          >
            {{ step }}
          </div>
          <span class="text-xs text-gray-600">
            {{ ['选择日期', '选择教练', '选择时间', '填写信息'][step - 1] }}
          </span>
        </div>
        
        <!-- Connector line -->
        <div 
          v-if="step < 4" 
          class="w-8 h-1 mx-2 bg-gray-200 rounded transition-colors duration-300"
          :class="{ 'bg-accent-dark': step < currentStep }"
        ></div>
      </template>
    </div>

    <!-- Step Content Card -->
    <div class="card animate-fade-in">
      <!-- Step 1: Select Date -->
      <div v-if="currentStep === 1">
        <h2 class="text-xl font-semibold text-primary-700 mb-4">📅 选择日期</h2>
        
        <label class="block text-sm font-medium text-gray-700 mb-2">预约日期</label>
        <input 
          type="date" 
          v-model="selectedDate"
          :min="new Date().toISOString().split('T')[0]"
          class="w-full px-4 py-3 rounded-lg border border-primary-300 focus:ring-2 focus:ring-accent-light focus:border-transparent transition-all duration-200 text-lg"
        />
        
        <div class="mt-4 p-3 bg-blue-50 rounded-lg text-sm text-gray-600">
          💡 提示：您可以选择今天或未来的任何日期进行预约
        </div>
      </div>

      <!-- Step 2: Select Instructor -->
      <div v-if="currentStep === 2">
        <h2 class="text-xl font-semibold text-primary-700 mb-4">👨‍🏫 选择教练</h2>
        
        <p class="mb-4 text-gray-600">预约日期：{{ selectedDate }}</p>
        
        <!-- Loading state -->
        <div v-if="loading" class="text-center py-8">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-accent-dark mx-auto"></div>
          <p class="mt-4 text-gray-600">加载中...</p>
        </div>
        
        <!-- Error state -->
        <div v-else-if="error" class="bg-red-50 text-red-700 p-4 rounded-lg text-center">
          {{ error }}
        </div>
        
        <!-- Instructor list from API -->
        <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <InstructorCard 
            v-for="instructor in instructors" 
            :key="instructor.id"
            :instructor="{ id: instructor.id, name: instructor.name, bio: instructor.description }"
            :selected="selectedInstructorId === instructor.id"
            @click="selectedInstructorId = instructor.id"
          />
        </div>

        <p v-if="!loading && !error && instructors.length === 0" class="text-center text-gray-500 py-8">
          📝 该日期暂无可用教练
        </p>
        <p v-else-if="!loading && !error && instructors.every(i => i.available_slots?.length === 0)" class="text-center text-gray-500 py-8">
          📝 该日期所有时段均已约满
        </p>
      </div>

      <!-- Step 3: Select Time Slot -->
      <div v-if="currentStep === 3">
        <h2 class="text-xl font-semibold text-primary-700 mb-4">⏰ 选择时间段</h2>
        
        <p class="mb-4 text-gray-600">
          教练：{{ instructors.find(i => i.id === selectedInstructorId)?.name || '未选择' }} | 日期：{{ selectedDate }}
        </p>

        <!-- Loading state -->
        <div v-if="loading" class="text-center py-8">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-accent-dark mx-auto"></div>
          <p class="mt-4 text-gray-600">加载中...</p>
        </div>
        
        <!-- Error state -->
        <div v-else-if="error" class="bg-red-50 text-red-700 p-4 rounded-lg text-center">
          {{ error }}
        </div>

        <!-- Time slots from API -->
        <div v-else class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-3 mb-4">
          <button
            v-for="slot in timeSlots" 
            :key="slot.id"
            @click="handleSlotClick(slot)"
            class="p-3 rounded-lg border-2 transition-all duration-200 text-sm font-medium min-h-[70px] flex flex-col items-center justify-center relative"
            :class="[
              isSlotSelected(slot)
                ? 'border-accent-dark bg-accent-light text-accent-dark shadow-md scale-105 cursor-pointer' 
                : !isSlotAvailable(slot)
                  ? 'border-gray-300 bg-gray-100 text-gray-400 cursor-not-allowed opacity-60'
                  : 'border-primary-200 hover:border-accent-green hover:bg-primary-50 cursor-pointer',
            ]"
          >
            <div class="font-bold">{{ formatTime(slot.start_time) }}</div>
            <div class="text-xs text-gray-600 mt-1">
              {{ isSlotAvailable(slot) ? '剩 ' + slot.available_spots + ' 位' : '已满' }}
            </div>
          </button>
        </div>

        <p v-if="!loading && !error && timeSlots.length === 0" class="text-center text-gray-500 py-8">
          📝 该教练在所选日期暂无可用时段
        </p>
      </div>

      <!-- Step 4: Customer Information Form -->
      <div v-if="currentStep === 4">
        <h2 class="text-xl font-semibold text-primary-700 mb-4">✍️ 填写预约信息</h2>
        
        <!-- Summary Card -->
        <div class="bg-accent-light rounded-lg p-4 mb-6">
          <h3 class="font-semibold text-accent-dark mb-2">📋 预约详情</h3>
          <div class="text-sm space-y-1 text-gray-700">
            <p><span class="font-medium">日期：</span>{{ selectedDate }}</p>
            <p v-if="selectedTimeSlot"><span class="font-medium">时间：</span>{{ selectedTimeSlot.start }} - {{ selectedTimeSlot.end }}</p>
          </div>
        </div>

        <!-- Use BookingForm component -->
        <BookingForm 
          @submit="submitBooking"
          :customer-name="customerName"
          :customer-phone="customerPhone"
          :customer-note="customerNote"
          @update="(data) => { customerName = data.name; customerPhone = data.phone; customerNote = data.note }"
        />
      </div>

      <!-- Navigation Buttons -->
      <div v-if="currentStep > 1 && currentStep < 4" class="flex gap-3 mt-6">
        <button 
          @click="prevStep"
          class="flex-1 py-3 px-4 rounded-lg border-2 border-primary-300 text-primary-700 font-semibold hover:bg-primary-50 transition-all duration-200"
        >
          ← 上一步
        </button>
        
        <button 
          @click="nextStep"
          class="flex-1 py-3 px-4 rounded-lg bg-accent-dark text-white font-bold hover:bg-accent-green transition-all duration-200 transform hover:scale-[1.02]"
        >
          下一步 →
        </button>
      </div>

      <button 
        v-if="currentStep === 1" 
        @click="nextStep"
        class="w-full mt-6 py-3 px-4 rounded-lg bg-accent-dark text-white font-bold hover:bg-accent-green transition-all duration-200 transform hover:scale-[1.02]"
      >
        下一步 →
      </button>
    </div>
  </div>
</template>

<style scoped></style>
