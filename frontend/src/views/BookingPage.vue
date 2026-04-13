<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import InstructorCard from '../components/InstructorCard.vue'

const router = useRouter()

// Step tracking (1: date, 2: instructor, 3: time slot, 4: form)
const currentStep = ref(1)

// Form state
const selectedDate = ref('')
const selectedInstructorId = ref<number | null>(null)
const selectedTimeSlot = ref<{ start: string; end: string } | null>(null)

// Customer info
const customerName = ref('')
const customerPhone = ref('')
const customerNote = ref('')

// Loading state
const loading = ref(false)

onMounted(() => {
  // Initialize date to today
  selectedDate.value = new Date().toISOString().split('T')[0]
})

async function nextStep() {
  if (currentStep.value === 1 && !selectedDate.value) return alert('请选择日期')
  if (currentStep.value === 2 && !selectedInstructorId.value) return alert('请选择教练')
  if (currentStep.value === 3 && !selectedTimeSlot.value) return alert('请选择时间段')
  
  currentStep.value++
}

function prevStep() {
  if (currentStep.value > 1) currentStep.value--
}

async function submitBooking() {
  if (!customerName.value || !customerPhone.value) {
    return alert('请填写姓名和电话')
  }
  
  loading.value = true
  
  // TODO: Call API to create booking
  try {
    await new Promise(resolve => setTimeout(resolve, 1000)) // Simulate API call
    
    router.push('/my-bookings')
    alert('预约成功！')
  } catch (error) {
    console.error('Booking failed:', error)
    alert('预约失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// TODO: Implement these functions by calling API client
function loadInstructors() { return [] as any[] }
function loadTimeSlots() { return [] as any[] }
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
        
        <!-- Placeholder for now - TODO: Connect to API -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <InstructorCard 
            v-for="i in 3" 
            :key="i"
            :instructor="{ id: i, name: ['张伟', '李娜', '王强'][i-1], bio: '资深瑜伽教练，拥有 5+ 年教学经验，擅长流瑜伽和阴瑜伽' }"
            :selected="selectedInstructorId === i"
            @click="selectedInstructorId = i"
          />
        </div>

        <p v-if="!selectedInstructorId" class="text-center text-gray-500 py-8">
          📝 请选择一位教练继续预约流程
        </p>
      </div>

      <!-- Step 3: Select Time Slot -->
      <div v-if="currentStep === 3">
        <h2 class="text-xl font-semibold text-primary-700 mb-4">⏰ 选择时间段</h2>
        
        <p class="mb-4 text-gray-600">
          教练：{{ selectedInstructorId || '未选择' }} | 日期：{{ selectedDate }}
        </p>

        <!-- Placeholder time slots - TODO: Connect to API -->
        <div class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-3 mb-4">
          <button
            v-for="slot in [
              { start_time: '08:00', end_time: '09:00', duration_minutes: 60, available: true },
              { start_time: '10:00', end_time: '11:00', duration_minutes: 60, available: true },
              { start_time: '14:00', end_time: '15:00', duration_minutes: 60, available: false },
              { start_time: '16:00', end_time: '17:00', duration_minutes: 60, available: true },
              { start_time: '19:00', end_time: '20:30', duration_minutes: 90, available: true }
            ]"
            :key="slot.start_time"
            @click="selectedTimeSlot = { start: slot.start_time, end: slot.end_time }"
            class="p-3 rounded-lg border-2 transition-all duration-200 text-sm font-medium min-h-[70px] flex flex-col items-center justify-center"
            :class="[
              selectedTimeSlot?.start === slot.start_time 
                ? 'border-accent-dark bg-accent-light text-accent-dark shadow-md scale-105' 
                : 'border-primary-200 hover:border-accent-green hover:bg-primary-50',
              !slot.available ? 'opacity-40 cursor-not-allowed bg-gray-100' : 'cursor-pointer'
            ]"
            :disabled="!slot.available"
          >
            <div class="font-bold">{{ slot.start_time }}</div>
            <div class="text-xs text-gray-600 mt-1">({{ slot.duration_minutes }}分钟)</div>
            <div v-if="!slot.available" class="absolute inset-0 flex items-center justify-center">
              <span class="text-lg opacity-50">✗</span>
            </div>
          </button>
        </div>
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
