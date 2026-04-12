<script setup>
import { RouterLink } from 'vue-router'

const navLinks = [
  { name: '首页', path: '/' },
  { name: '我的预约', path: '/bookings' }
]
</script>

<template>
  <header class="bg-white shadow-sm sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center h-16">
        <!-- Logo -->
        <RouterLink to="/" class="text-2xl font-bold text-pink-500">
          Appt 🧘‍♀️
        </RouterLink>

        <!-- Navigation -->
        <nav class="flex space-x-8">
          <RouterLink 
            v-for="link in navLinks" 
            :key="link.path"
            :to="link.path"
            class="text-gray-600 hover:text-pink-500 px-3 py-2 rounded-md text-sm font-medium transition-colors"
          >
            {{ link.name }}
          </RouterLink>
        </nav>

        <!-- Admin Link (conditionally shown) -->
        <button 
          v-if="false"
          @click="$router.push('/admin')"
          class="text-gray-600 hover:text-pink-500 text-sm font-medium"
        >
          管理后台
        </button>

        <!-- Mobile menu button (placeholder) -->
        <div class="md:hidden">
          <button @click="$emit('menu-toggle')" class="text-gray-600 hover:text-pink-500">
            ☰
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<style scoped>
/* Additional styles can be added here */
</style>
