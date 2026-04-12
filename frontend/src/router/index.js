import { createRouter, createWebHistory } from 'vue-router'
import BookingPage from '../views/BookingPage.vue'
import MyBookings from '../views/MyBookings.vue'

// 动态设置页面标题
const updateTitle = (title) => {
  document.title = title ? `${title} - Appt` : 'Appt - Yoga Studio Scheduler'
}

const routes = [
  {
    path: '/',
    name: 'Home',
    component: BookingPage
  },
  {
    path: '/bookings',
    name: 'MyBookings',
    component: MyBookings,
    meta: { title: '我的预约' }
  },
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: () => import('../views/admin/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: () => import('../views/admin/Login.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// Update page title on route change
router.afterEach((to) => {
  updateTitle(to.meta.title)
})

// Route guard for admin pages
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('admin_token')
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/admin/login')
  } else {
    next()
  }
})

export default router
