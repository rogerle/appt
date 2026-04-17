<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

function startBooking() {
  router.push('/booking')
}
</script>

<template>
  <div class="home-page min-h-screen flex items-center justify-center bg-gradient-to-br from-accent-light via-primary-50 to-primary-100">
    <div class="container-mobile py-12 px-4 text-center">
      
      <!-- Logo & Welcome -->
      <div class="mb-8 animate-fade-in">
        <div class="text-7xl mb-4">🧘‍♀️</div>
        <h1 class="text-3xl md:text-4xl font-bold text-primary-800 mb-2">
          欢迎来到 Appt Yoga
        </h1>
        <p class="text-xl text-gray-600">专业的瑜伽馆预约系统</p>
      </div>

      <!-- CTA Card -->
      <div class="card max-w-md mx-auto shadow-lg animate-scale-in">
        <div class="p-8">
          <h2 class="text-2xl font-bold text-primary-700 mb-4">开始您的瑜伽之旅</h2>
          
          <p class="text-gray-600 mb-6 leading-relaxed">
            选择您心仪的教练和时间段，<br />轻松完成课程预约，享受健康美好的瑜伽时光！
          </p>

          <!-- Main CTA Button -->
          <button 
            @click="startBooking"
            class="w-full bg-accent-dark hover:bg-accent-green text-white font-bold py-4 px-8 rounded-lg transition-all duration-300 transform hover:scale-105 shadow-xl text-lg flex items-center justify-center gap-2 mx-auto"
          >
            <span>📅 立即预约</span>
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </button>

          <p class="mt-4 text-sm text-gray-500">
            🔒 安全预约 · 即时确认 · 短信提醒
          </p>
        </div>
      </div>

      <!-- Features Grid -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8 max-w-2xl mx-auto">
        <div class="bg-white rounded-lg p-4 shadow-sm animate-fade-in" style="animation-delay: 0.1s;">
          <div class="text-3xl mb-2">⏰</div>
          <h3 class="font-semibold text-primary-700 mb-1">灵活时间</h3>
          <p class="text-sm text-gray-600">多时段可选，随时调整</p>
        </div>

        <div class="bg-white rounded-lg p-4 shadow-sm animate-fade-in" style="animation-delay: 0.2s;">
          <div class="text-3xl mb-2">👨‍🏫</div>
          <h3 class="font-semibold text-primary-700 mb-1">专业教练</h3>
          <p class="text-sm text-gray-600">资深导师，因材施教</p>
        </div>

        <div class="bg-white rounded-lg p-4 shadow-sm animate-fade-in" style="animation-delay: 0.3s;">
          <div class="text-3xl mb-2">📱</div>
          <h3 class="font-semibold text-primary-700 mb-1">便捷提醒</h3>
          <p class="text-sm text-gray-600">短信通知，不会忘记</p>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped></style>
