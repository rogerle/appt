<template>
  <div class="dashboard">
    <div class="header">
      <h1>📊 管理仪表盘</h1>
      <p class="subtitle">实时数据概览</p>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div v-for="stat in statsCards" :key="stat.id" class="stat-card" :class="'card-' + stat.color">
        <div class="icon">{{ stat.icon }}</div>
        <div class="content">
          <h3>{{ stat.label }}</h3>
          <p class="value">{{ stat.value }}</p>
        </div>
      </div>
    </div>

    <!-- Recent Bookings -->
    <div class="recent-section">
      <div class="section-header">
        <h2>最近预约</h2>
        <button @click="refreshData" :disabled="loading" class="btn-refresh">
          🔄 刷新
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="loading && !recentBookings.length" class="loading-state">
        <span class="spinner"></span> 加载中...
      </div>

      <!-- Empty State -->
      <div v-else-if="!recentBookings.length" class="empty-state">
        📭 暂无预约数据
      </div>

      <!-- Bookings Table -->
      <div v-else class="table-container">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>客户姓名</th>
              <th>电话</th>
              <th>日期</th>
              <th>时间</th>
              <th>课程类型</th>
              <th>教练</th>
              <th>状态</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="booking in recentBookings" :key="booking.id">
              <td>#{{ booking.id }}</td>
              <td>{{ booking.customer_name }}</td>
              <td>{{ maskPhone(booking.customer_phone) }}</td>
              <td>{{ formatDate(booking.booking_date) }}</td>
              <td>{{ formatTimeRange(booking.start_time, booking.end_time) }}</td>
              <td>{{ booking.class_type }}</td>
              <td>{{ booking.instructor_name }}</td>
              <td><span class="status-badge" :class="'status-' + booking.status">{{ getStatusText(booking.status) }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Auto-refresh notice -->
    <p v-if="lastRefreshedAt" class="refresh-notice">
      最后更新：{{ formatLastUpdated(lastRefreshedAt) }}（30 秒自动刷新）
    </p>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import apiClient from '../../api/client'
import type { RecentBookingResponse } from '@/types/admin'

interface StatsCard {
  id: string
  label: string
  value: number | string
  color: string
  icon: string
}

// State
const loading = ref(false)
const statsCards = ref<StatsCard[]>([
  { id: 'today', label: '今日预约', value: 0, color: 'blue', icon: '📅' },
  { id: 'week', label: '本周预约', value: 0, color: 'green', icon: '📊' },
  { id: 'instructors', label: '活跃教练', value: 0, color: 'purple', icon: '🧘' },
  { id: 'slots', label: '可用名额', value: 0, color: 'orange', icon: '⏰' }
])
const recentBookings = ref<RecentBookingResponse[]>([])
const lastRefreshedAt = ref<Date | null>(null)

let refreshInterval: number | null = null

// Fetch dashboard data
async function fetchDashboardData(): Promise<void> {
  loading.value = true
  
  try {
    console.log('🔍 Fetching dashboard data...')
    // Fetch stats
    const statsRes = await apiClient.get('/admin/dashboard/stats')
    console.log('✅ Stats response:', statsRes.data)
    updateStatsCards(statsRes.data)
    
    // Fetch recent bookings  
    const bookingsRes = await apiClient.get('/admin/dashboard/recent-bookings', { params: { limit: 10 } })
    console.log('✅ Bookings response:', bookingsRes.data)
    recentBookings.value = bookingsRes.data
    
    lastRefreshedAt.value = new Date()
  } catch (error: any) {
    console.error('❌ Failed to fetch dashboard data:', error)
    if (error.response?.status === 401) {
      alert('请先登录！')
    }
  } finally {
    loading.value = false
  }
}

// Update stats cards with fetched data
function updateStatsCards(stats: any): void {
  statsCards.value[0].value = stats.total_bookings_today
  statsCards.value[1].value = stats.total_bookings_week  
  statsCards.value[2].value = stats.active_instructors
  statsCards.value[3].value = stats.available_slots
}

// Refresh data manually or on interval
function refreshData(): void {
  fetchDashboardData()
}

// Utility functions
function maskPhone(phone: string): string {
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}/${date.getDate()}`
}

function formatTimeRange(startTime: any, endTime: any): string {
  if (!startTime || !endTime) return '-'
  
  // startTime and endTime are strings like "14:00:00" from Pydantic
  const startStr = String(startTime)
  const endStr = String(endTime)
  
  // Extract HH:MM from HH:MM:SS format
  const extractHHMM = (timeStr: string): string => {
    if (!timeStr) return '00:00'
    const parts = timeStr.split(':')
    return `${parts[0].padStart(2, '0')}:${parts[1]?.padStart(2, '0') || '00'}`
  }
  
  return `${extractHHMM(startStr)} - ${extractHHMM(endStr)}`
}

function getStatusText(status: string): string {
  const statusMap: Record<string, string> = {
    pending: '待确认',
    confirmed: '已确认',
    cancelled: '已取消', 
    completed: '已完成'
  }
  return statusMap[status] || status
}

function formatLastUpdated(date: Date): string {
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

// Auto-refresh every 30 seconds
onMounted(() => {
  fetchDashboardData()
  
  refreshInterval = window.setInterval(() => {
    fetchDashboardData()
  }, 30000) // 30 seconds
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  text-align: center;
  margin-bottom: 32px;
}

.header h1 {
  font-size: 32px;
  color: #333;
  margin-bottom: 8px;
}

.subtitle {
  color: #666;
  font-size: 14px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: transform 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
}

.stat-card .icon {
  font-size: 36px;
  opacity: 0.9;
}

.stat-card .content h3 {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.stat-card .value {
  font-size: 28px;
  font-weight: bold;
  margin: 0;
}

.card-blue .content .value { color: #3b82f6; }
.card-green .content .value { color: #10b981; }
.card-purple .content .value { color: #8b5cf6; }
.card-orange .content .value { color: #f59e0b; }

.recent-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.btn-refresh {
  padding: 8px 16px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.btn-refresh:hover:not(:disabled) {
  background: #2563eb;
}

.loading-state, .empty-state {
  text-align: center;
  padding: 48px;
  color: #999;
}

.spinner {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 3px solid #f3f3f3;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-right: 8px;
}

@keyframes spin { to { transform: rotate(360deg); } }

.table-container {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

th {
  background: #f9fafb;
  font-weight: 600;
  color: #374151;
}

tr:hover {
  background: #f9fafb;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-confirmed { background: #d1fae5; color: #065f46; }
.status-pending { background: #fef3c7; color: #92400e; }
.status-cancelled { background: #fee2e2; color: #991b1b; }
.status-completed { background: #dbeafe; color: #1e40af; }

.refresh-notice {
  text-align: center;
  margin-top: 20px;
  color: #999;
  font-size: 13px;
}

/* Responsive */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  table {
    font-size: 14px;
  }
  
  th, td {
    padding: 8px;
  }
}
</style>
