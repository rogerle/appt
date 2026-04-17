import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  // ==================== C 端页面 (移动端优先) ====================
  
  {
    path: '/',
    name: 'home',
    component: () => import('../views/customer/Home.vue'),
    meta: { title: '首页' }
  },
  
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/auth/Login.vue'),
    meta: { title: '登录', requiresGuest: true }
  },
  
  {
    path: '/register',
    name: 'register',
    component: () => import('../views/auth/Register.vue'),
    meta: { title: '注册', requiresGuest: true }
  },

  // Customer routes (public, but show better UI when logged in)
  {
    path: '/booking',
    name: 'booking',
    component: () => import('../views/customer/BookingPage.vue'),
    meta: { title: '预约课程' }
  },
  
  {
    path: '/my-bookings',
    name: 'my-bookings',
    component: () => import('../views/customer/MyBookings.vue'),
    meta: { title: '我的预约' }
  },

  // ==================== 管理后台 (PC 端独立) ====================
  
  {
    path: '/admin',
    component: () => import('../admin/layouts/AdminLayout.vue'),
    redirect: '/admin/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: () => import('../admin/views/Dashboard.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'instructors',
        name: 'InstructorManagement',
        component: () => import('../admin/views/InstructorManagement.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'schedules',
        name: 'ScheduleManagement',
        component: () => import('../admin/views/ScheduleManagement.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'users',
        name: 'UserManagement',
        component: () => import('../admin/views/UserManagement.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
      }
    ]
  },

]

const router = createRouter({
  history: createWebHistory((import.meta as any).env.BASE_URL),
  routes,
  
  /**
   * Scroll to top on navigation (C 端)
   */
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

/**
 * Navigation guards for authentication and authorization
 */
router.beforeEach(async (to, from, next) => {
  // Set page title
  document.title = to.meta.title 
    ? `${to.meta.title} - Appt Yoga` 
    : 'Appt - 瑜伽馆预约系统'
  
  // Import auth store here to avoid circular dependency
  const { useAuthStore } = await import('../stores/auth')
  const authStore = useAuthStore()

  // If not authenticated, try to fetch current user (token might exist from previous session)
  if (!authStore.isAuthenticated && authStore.token) {
    try {
      await authStore.fetchCurrentUser()
    } catch (error) {
      console.warn('Failed to restore session:', error)
      // Token is invalid, will be handled by route guards below
    }
  }

  // Guard: Redirect authenticated users away from login/register pages
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next('/')
    return
  }

  // Guard: Require authentication for protected routes
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login', query: { from: to.fullPath } })
    return
  }

  // Guard: Require admin role for admin-only routes
  if (to.meta.requiresAdmin && authStore.isAuthenticated && !authStore.isAdmin) {
    alert('需要管理员权限才能访问此页面')
    next('/')
    return
  }

  // All checks passed, proceed to the route
  next()
})

export default router
