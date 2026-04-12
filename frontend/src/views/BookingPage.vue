<script setup>
import { ref, onMounted } from 'vue'
import { useBookingStore } from '../stores/booking'
import Header from '../components/common/Header.vue'

const store = useBookingStore()

// Reactive state
const selectedDate = ref(new Date().toISOString().split('T')[0])
const selectedInstructor = ref(null)
const selectedTimeSlot = ref(null)
const bookingFormVisible = ref(false)
const userData = ref({ name: '', phone: '' })

// Methods
function handleDateChange(date) {
  selectedDate.value = date
  store.fetchSchedules(date, selectedInstructor.value)
}

function handleInstructorSelect(instructor) {
  selectedInstructor.value = instructor.id
  store.fetchSchedules(selectedDate.value, instructor.id)
}

function handleTimeSlotSelect(slot) {
  selectedTimeSlot.value = slot
  bookingFormVisible.value = true
}

async function submitBooking() {
  if (!userData.value.name || !userData.value.phone) {
    alert('请填写姓名和手机号')
    return
  }

  try {
    await store.createBooking({
      name: userData.value.name,
      phone: userData.value.phone,
      instructor_id: selectedInstructor.value,
      studio_id: 1, // Default studio for now
      date: selectedDate.value,
      time_slot_start: selectedTimeSlot.value.start_time,
      time_slot_end: selectedTimeSlot.value.end_time
    })
    
    alert('预约成功！')
    bookingFormVisible.value = false
    
    // Reset form
    userData.value = { name: '', phone: '' }
    selectedTimeSlot.value = null
  } catch (error) {
    alert(`预约失败：${error.message}`)
  }
}

// Lifecycle
onMounted(() => {
  store.fetchInstructors()
})
</script>

<template>
  <div class="min-h-screen bg-gray-light">
    <Header />

    <!-- Hero Section -->
    <section class="section-hero py-16 px-4">
      <div class="max-w-4xl mx-auto text-center">
        <h1 class="text-display-hero mb-4">预约你的瑜伽课程</h1>
        <p class="text-2xl font-light leading-relaxed mb-8">
          选择日期、教练和时间，开始你的练习之旅
        </p>
      </div>
    </section>

    <!-- Main Content -->
    <main class="max-w-6xl mx-auto px-4 py-12">
      <!-- Date Selector -->
      <section class="mb-12">
        <h3 class="text-section-heading mb-6">选择日期</h3>
        <div class="flex gap-4 overflow-x-auto pb-4">
          <button 
            v-for="day in 7" 
            :key="day"
            @click="handleDateChange(new Date(Date.now() + day * 86400000).toISOString().split('T')[0])"
            class="btn-filter px-6 py-3 min-w-[120px]"
          >
            {{ new Date(Date.now() + day * 86400000).toLocaleDateString('zh-CN', { weekday: 'short', month: 'numeric', day: 'numeric' }) }}
          </button>
        </div>
      </section>

      <!-- Instructors Grid -->
      <section class="mb-12">
        <h3 class="text-section-heading mb-6">选择教练</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div 
            v-for="instructor in store.instructors" 
            :key="instructor.id"
            @click="handleInstructorSelect(instructor)"
            class="card cursor-pointer transition-all hover:scale-[1.02]"
            :class="{ 'ring-2 ring-blue-500': selectedInstructor === instructor.id }"
          >
            <img 
              v-if="instructor.avatar_url" 
              :src="instructor.avatar_url" 
              alt=""
              class="w-full h-48 object-cover rounded-lg mb-4"
            />
            <div class="text-xl font-semibold">{{ instructor.name }}</div>
            <p v-if="instructor.bio" class="text-caption text-secondary mt-2">
              {{ instructor.bio }}
            </p>
          </div>
        </div>
      </section>

      <!-- Time Slots Grid -->
      <section v-if="selectedInstructor && store.schedules.length > 0">
        <h3 class="text-section-heading mb-6">可用时段</h3>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button 
            v-for="(slot, index) in store.schedules" 
            :key="index"
            @click="handleTimeSlotSelect(slot)"
            class="btn-primary py-4 px-6 transition-all hover:scale-[1.05]"
          >
            {{ slot.start_time }} - {{ slot.end_time }}
          </button>
        </div>
      </section>

      <!-- Empty State -->
      <div v-if="!store.instructors.length" class="text-center py-12">
        <p class="text-lg text-secondary">暂无可用教练，请稍后重试</p>
      </div>
    </main>

    <!-- Booking Modal -->
    <div 
      v-if="bookingFormVisible" 
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="bookingFormVisible = false"
    >
      <div class="card max-w-md w-full">
        <h3 class="text-xl font-semibold mb-6">确认预约</h3>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-2">姓名</label>
            <input 
              v-model="userData.name"
              type="text"
              placeholder="请输入您的姓名"
              class="input-field"
            />
          </div>

          <div>
            <label class="block text-sm font-medium mb-2">手机号</label>
            <input 
              v-model="userData.phone"
              type="tel"
              placeholder="请输入您的 11 位手机号"
              maxlength="11"
              class="input-field"
            />
          </div>

          <div class="pt-4 flex gap-3">
            <button @click="bookingFormVisible = false" class="btn-secondary flex-1">取消</button>
            <button @click="submitBooking" class="btn-primary flex-1">确认预约</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer placeholder -->
    <footer class="mt-auto py-8 text-center text-caption text-secondary">
      © 2026 Appt - Yoga Studio Scheduler
    </footer>
  </div>
</template>

<style scoped>
/* Additional component-specific styles if needed */
</style>
