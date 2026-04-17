<script setup lang="ts">
import { ref, computed } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'
import { useAuthStore } from './stores/auth'

const showMobileMenu = ref(false)
const route = useRoute()
const authStore = useAuthStore()

// Computed properties for UI state
const isLoggedIn = computed(() => authStore.isAuthenticated)
const isAdminUser = computed(() => authStore.isAdmin)

// Check if we're on an admin page (hide C-side header/footer)
const isOnAdminPage = computed(() => {
  return route.path.startsWith('/admin')
})

/**
 * Handle logout click
 */
function handleLogout(): void {
  if (confirm('确定要退出登录吗？')) {
    authStore.logout()
  }
}



</script>

<template>
  <div class="min-h-screen flex flex-col bg-primary-50">
    <!-- C-side Header (hide on admin pages) -->
    <header v-if="!isOnAdminPage" class="bg-white shadow-sm border-b border-primary-200 sticky top-0 z-50">
      <div class="container-mobile flex items-center justify-between py-4 px-4">
        <!-- Logo -->
        <RouterLink to="/" class="text-xl font-bold text-accent-dark hover:text-accent-green transition-colors">
          🧘 Appt Yoga
        </RouterLink>
        
        <!-- Desktop Navigation -->
        <nav class="hidden md:flex items-center space-x-6">
          <!-- Customer Routes -->
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
            v-if="isLoggedIn"
            to="/my-bookings" 
            :class="[
              'px-3 py-2 rounded-lg font-medium transition-colors',
              route.path === '/my-bookings' ? 'bg-accent-light text-accent-dark' : 'text-primary-600 hover:text-primary-900'
            ]"
          >
            我的预约
          </RouterLink>
          
          <!-- Admin Route (only show to admin users) -->
          <template v-if="isAdminUser">
            <div class="admin-menu">
              <span class="menu-label">管理</span>
              <RouterLink 
                to="/admin/dashboard" 
                :class="[
                  'px-3 py-2 rounded-lg font-medium transition-colors',
                  route.path === '/admin/dashboard' ? 'bg-accent-light text-accent-dark' : 'text-primary-600 hover:text-primary-900'
                ]"
              >
                仪表盘
              </RouterLink>
            </div>
          </template>

          <!-- Auth Buttons -->
          <template v-if="!isLoggedIn">
            <RouterLink 
              to="/login"
              class="px-4 py-2 rounded-lg font-medium text-primary-600 hover:text-primary-900 transition-colors"
            >
              登录
            </RouterLink>
            
            <RouterLink 
              to="/register"
              class="px-4 py-2 rounded-lg font-medium bg-accent-green text-white hover:bg-emerald-700 transition-colors shadow-sm"
            >
              注册
            </RouterLink>
          </template>

          <button 
            v-else 
            @click="handleLogout"
            class="px-4 py-2 rounded-lg font-medium text-primary-600 hover:text-red-600 transition-colors border border-primary-200 hover:bg-primary-50"
          >
            退出 ({{ authStore.user?.username }})
          </button>
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
          v-if="isLoggedIn"
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
          v-if="isAdminUser"
          to="/admin/dashboard"
          @click="showMobileMenu = false"
          :class="[
            'block px-3 py-2 rounded-lg font-medium transition-colors',
            route.path.startsWith('/admin') ? 'bg-accent-light text-accent-dark' : 'text-primary-600 hover:text-primary-900'
          ]"
        >
          管理后台
        </RouterLink>

        <!-- Mobile Auth Buttons -->
        <template v-if="!isLoggedIn">
          <div class="pt-2 pb-1 text-xs font-semibold text-primary-400 uppercase tracking-wider">账户</div>
          
          <RouterLink 
            to="/login"
            @click="showMobileMenu = false"
            class="block px-3 py-2 rounded-lg font-medium text-primary-600 hover:text-primary-900 transition-colors"
          >
            登录
          </RouterLink>

          <RouterLink 
            to="/register"
            @click="showMobileMenu = false"
            class="block px-3 py-2 rounded-lg font-medium bg-accent-green text-white hover:bg-emerald-700 transition-colors shadow-sm"
          >
            注册
          </RouterLink>
        </template>

        <button 
          v-if="isLoggedIn"
          @click="handleLogout; showMobileMenu = false"
          class="w-full text-left px-3 py-2 rounded-lg font-medium text-primary-600 hover:text-red-600 transition-colors border border-primary-200 hover:bg-primary-50"
        >
          退出 ({{ authStore.user?.username }})
        </button>
      </nav>
    </header>



    <!-- C-side Main Content (hide on admin pages) -->
    <main v-if="!isOnAdminPage" class="flex-grow container-mobile py-6 px-4 animate-fade-in">
      <RouterView />
    </main>

    <!-- Admin Pages: RouterView will render inside AdminLayout.vue -->
    <div v-if="isOnAdminPage">
      <RouterView />
    </div>

    <!-- Footer (only show on C-side pages) -->
    <footer v-if="!isOnAdminPage" class="bg-white border-t border-primary-200 mt-auto">
      <div class="container-mobile py-6 px-4 text-center text-sm text-primary-500">
        <p>© 2026 Appt Yoga. Made with ❤️ for yoga studios</p>
      </div>
    </footer>
  </div>
</template>

<style scoped></style>
