import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/Home.vue'),
      meta: { title: '首页' }
    },
    
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
    
    // Admin routes (protected)
    {
      path: '/admin',
      redirect: '/admin/dashboard'
    },
    {
      path: '/admin/dashboard',
      name: 'admin-dashboard',
      component: () => import('../views/admin/Dashboard.vue'),
      meta: { title: '管理后台 - 仪表盘', requiresAuth: true }
    },
    {
      path: '/admin/instructors',
      name: 'admin-instructors',
      component: () => import('../views/admin/InstructorManagement.vue'),
      meta: { title: '教练管理', requiresAuth: true }
    },
    {
      path: '/admin/schedules',
      name: 'admin-schedules',
      component: () => import('../views/admin/ScheduleManagement.vue'),
      meta: { title: '排课管理', requiresAuth: true }
    }
  ],
  
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// Navigation guards
router.beforeEach((to, from, next) => {
  // Set page title
  document.title = to.meta.title 
    ? `${to.meta.title} - Appt Yoga` 
    : 'Appt - 瑜伽馆预约系统'
  
  // Auth guard for admin routes
  // TEMPORARILY DISABLED FOR TESTING - Remove in production!
  const token = localStorage.getItem('auth_token')
  
  if (to.meta.requiresAuth && !token) {
    // next('/login')  // Commented out for testing
    console.warn('Warning: Admin access without authentication (testing mode)')
    next()  // Allow access for now
  } else {
    next()
  }
})

export default router
