<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'

const showMobileMenu = ref(false)
const route = useRoute()
</script>

<template>
  <div class="min-h-screen flex flex-col bg-primary-50">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b border-primary-200 sticky top-0 z-50">
      <div class="container-mobile flex items-center justify-between py-4 px-4">
        <!-- Logo -->
        <RouterLink to="/" class="text-xl font-bold text-accent-dark hover:text-accent-green transition-colors">
          🧘 Appt Yoga
        </RouterLink>
        
        <!-- Desktop Navigation -->
        <nav class="hidden md:flex space-x-6">
          <RouterLink 
            to="/booking" 
            :class="[
              'px-3 py-2 rounded-lg font-medium transition-colors',
              route.path === '/booking' ? 'bg-accent-light text-accent-dark' : 'text-primary-600 hover:text-primary-900'
            ]"
          >
            预约课程
          </RouterLink>
          
          <RouterLink 
            to="/my-bookings" 
            :class="[
              'px-3 py-2 rounded-lg font-medium transition-colors',
              route.path === '/my-bookings' ? 'bg-accent-light text-accent-dark' : 'text-primary-600 hover:text-primary-900'
            ]"
          >
            我的预约
          </RouterLink>
          
          <RouterLink 
            to="/admin/dashboard" 
            :class="[
              'px-3 py-2 rounded-lg font-medium transition-colors',
              route.path.startsWith('/admin') ? 'bg-accent-light text-accent-dark' : 'text-primary-600 hover:text-primary-900'
            ]"
          >
            管理后台
          </RouterLink>
        </nav>
        
        <!-- Mobile Menu Button -->
        <button 
          @click="showMobileMenu = !showMobileMenu"
          class="md:hidden p-2 rounded-lg hover:bg-primary-100 transition-colors"
          aria-label="Toggle menu"
        >
          🍔
        </button>
      </div>
      
      <!-- Mobile Navigation -->
      <nav v-if="showMobileMenu" class="md:hidden bg-white border-t border-primary-200 px-4 py-2 space-y-1">
        <RouterLink 
          to="/booking"
          @click="showMobileMenu = false"
          :class="[
            'block px-3 py-2 rounded-lg font-medium transition-colors',
            route.path === '/booking' ? 'bg-accent-light text-accent-dark' : 'text-primary-600 hover:text-primary-900'
          ]"
        >
          预约课程
        </RouterLink>
        
        <RouterLink 
          to="/my-bookings"
          @click="showMobileMenu = false"
          :class="[
            'block px-3 py-2 rounded-lg font-medium transition-colors',
            route.path === '/my-bookings' ? 'bg-accent-light text-accent-dark' : 'text-primary-600 hover:text-primary-900'
          ]"
        >
          我的预约
        </RouterLink>
        
        <RouterLink 
          to="/admin/dashboard"
          @click="showMobileMenu = false"
          :class="[
            'block px-3 py-2 rounded-lg font-medium transition-colors',
            route.path.startsWith('/admin') ? 'bg-accent-light text-accent-dark' : 'text-primary-600 hover:text-primary-900'
          ]"
        >
          管理后台
        </RouterLink>
      </nav>
    </header>
    
    <!-- Main Content Area -->
    <main class="flex-grow container-mobile py-6 px-4 animate-fade-in">
      <RouterView />
    </main>
    
    <!-- Footer -->
    <footer class="bg-white border-t border-primary-200 mt-auto">
      <div class="container-mobile py-6 px-4 text-center text-sm text-primary-500">
        <p>© 2026 Appt Yoga. Made with ❤️ for yoga studios</p>
      </div>
    </footer>
  </div>
</template>

<style scoped></style>
