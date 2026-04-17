<template>
  <aside class="admin-sidebar">
    <div class="sidebar-header">
      <h2>管理后台</h2>
      <p class="subtitle">{{ authStore.user?.username }}</p>
    </div>

    <nav class="sidebar-nav">
      <RouterLink 
        to="/admin/dashboard" 
        class="nav-item"
        :class="{ active: route.path === '/admin/dashboard' || !route.path.startsWith('/admin') && route.path !== '/' }"
      >
        <span class="icon">📊</span>
        <span>仪表盘</span>
      </RouterLink>

      <RouterLink 
        to="/admin/instructors" 
        class="nav-item"
        :class="{ active: route.path === '/admin/instructors' }"
      >
        <span class="icon">🧘</span>
        <span>教练管理</span>
      </RouterLink>

      <RouterLink 
        to="/admin/schedules" 
        class="nav-item"
        :class="{ active: route.path === '/admin/schedules' }"
      >
        <span class="icon">📅</span>
        <span>排课管理</span>
      </RouterLink>

      <RouterLink 
        to="/admin/users" 
        class="nav-item"
        :class="{ active: route.path === '/admin/users' }"
      >
        <span class="icon">👥</span>
        <span>用户管理</span>
      </RouterLink>
    </nav>

    <div class="sidebar-footer">
      <button @click="goHome" class="btn-home">
        🏠 返回首页
      </button>
      
      <button @click="logout" class="btn-logout">
        🔒 退出登录
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const route = router.currentRoute

// Go to homepage
function goHome(): void {
  router.push('/')
}

// Logout with confirmation
function logout(): void {
  if (confirm('确定要退出登录吗？')) {
    authStore.logout()
    router.push('/')
  }
}
</script>

<style scoped>
.admin-sidebar {
  width: 240px;
  background: linear-gradient(180deg, #1e3a8a 0%, #1e40af 100%);
  color: white;
  display: flex;
  flex-direction: column;
  height: 100vh; /* Full viewport height */
  position: sticky;
  top: 0;
}

.sidebar-header {
  padding: 24px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.sidebar-header h2 {
  margin: 0 0 8px 0;
  font-size: 20px;
}

.subtitle {
  margin: 0;
  font-size: 13px;
  opacity: 0.8;
}

.sidebar-nav {
  flex: 1;
  padding: 16px 0;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 24px;
  color: white;
  text-decoration: none;
  transition: all 0.2s ease;
}

.nav-item:hover {
  background: rgba(255,255,255,0.1);
}

.nav-item.active {
  background: rgba(255,255,255,0.2);
  border-left: 4px solid #60a5fa;
}

.icon {
  font-size: 18px;
}

.sidebar-footer {
  padding: 16px 24px;
  border-top: 1px solid rgba(255,255,255,0.1);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.btn-home, .btn-logout {
  padding: 10px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.btn-home {
  background: rgba(255,255,255,0.1);
  color: white;
}

.btn-home:hover {
  background: rgba(255,255,255,0.2);
}

.btn-logout {
  background: #ef4444;
  color: white;
}

.btn-logout:hover {
  background: #dc2626;
}

@media (max-width: 768px) {
  .admin-sidebar {
    width: 100%;
    height: auto;
    position: relative;
    top: 0;
  }
}
</style>
