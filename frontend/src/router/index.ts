import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  // Public routes
  {
    path: '/',
    name: 'home',
    component: () => import('../views/Home.vue'),
    meta: { title: '首页' }
  },
  
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/Login.vue'),
    meta: { title: '登录', requiresGuest: true }
  },
  
  {
    path: '/register',
    name: 'register',
    component: () => import('../views/Register.vue'),
    meta: { title: '注册', requiresGuest: true }
  },

  // Customer routes (public, but show better UI when logged in)
  {
    path: '/booking',
    name: 'booking',
    component: () => import('../views/BookingPage.vue'),
    meta: { title: '预约课程' }
  },
  
  {
    path: '/my-bookings',
    name: 'my-bookings',
    component: () => import('../views/MyBookings.vue'),
    meta: { title: '我的预约' }
  },
  
  // Admin routes (protected - requires authentication + admin role)
  {
    path: '/admin',
    redirect: '/admin/dashboard'
  },
  
  // Admin Layout wrapper
  {
    path: '/admin',
    name: 'admin-layout',
    component: () => import('../layouts/AdminLayout.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
    redirect: '/admin/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'admin-dashboard',
        component: () => import('../views/admin/Dashboard.vue'),
        meta: { title: '管理后台 - 仪表盘' }
      },
      {
        path: 'instructors',
        name: 'admin-instructors',
        component: () => import('../views/admin/InstructorManagement.vue'),
        meta: { title: '教练管理' }
      },
      {
        path: 'schedules',
        name: 'admin-schedules',
        component: () => import('../views/admin/ScheduleManagement.vue'),
        meta: { title: '排课管理' }
      },
      {
        path: 'users',
        name: 'admin-users',
        component: () => import('../views/admin/UserManagement.vue'),
        meta: { title: '用户管理' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory((import.meta as any).env.BASE_URL),
  routes,
  /**
   * Scroll to top on navigation
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
