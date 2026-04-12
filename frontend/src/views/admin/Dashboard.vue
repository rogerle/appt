<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部导航栏 -->
    <Header />

    <div class="flex">
      <!-- 侧边栏导航 -->
      <aside class="w-64 bg-teal-700 min-h-screen text-white">
        <nav class="p-4 space-y-2">
          <router-link
            to="/admin/dashboard"
            class="block px-4 py-3 rounded-md hover:bg-teal-600 transition-colors"
            :class="{ 'bg-teal-600': $route.path === '/admin/dashboard' }"
          >
            📊 今日预约
          </router-link>

          <router-link
            to="/admin/schedules"
            class="block px-4 py-3 rounded-md hover:bg-teal-600 transition-colors"
            :class="{ 'bg-teal-600': $route.path.includes('schedules') }"
          >
            📅 排课管理
          </router-link>

          <router-link
            to="/admin/instructors"
            class="block px-4 py-3 rounded-md hover:bg-teal-600 transition-colors"
            :class="{ 'bg-teal-600': $route.path.includes('instructors') }"
          >
            👨‍🏫 教练管理
          </router-link>

          <div class="border-t border-teal-500 my-4 pt-4">
            <button
              @click="handleLogout"
              class="w-full px-4 py-3 rounded-md hover:bg-red-600 transition-colors text-left"
            >
              🔓 退出登录
            </button>
          </div>
        </nav>
      </aside>

      <!-- 主内容区 -->
      <main class="flex-1 p-8">
        <router-view />
      </main>
    </div>

    <!-- 底部组件 -->
    <Footer />
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import Header from '@/components/common/Header.vue'
import Footer from '@/components/common/Footer.vue'

const router = useRouter()

const handleLogout = () => {
  // 清除 token
  localStorage.removeItem('admin_token')
  
  // 跳转到登录页
  router.push('/admin/login')
}
</script>

<style scoped>
/* 使用 Tailwind CSS 类，无需额外样式 */
</style>
