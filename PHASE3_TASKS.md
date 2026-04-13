# Phase 3 Tasks - 用户端核心功能（预约流程）

**目标**: 完成用户预约端的 Vue 3 前端开发，包括组件、状态管理、API 集成和 PWA 配置  
**预计耗时**: 6 小时

---

## 📦 任务清单 (18 个原子级任务)

### 🔧 基础设置阶段 (任务 1-4)

#### Task 1: Vue 3 + Vite 项目初始化
- **文件**: `frontend/package.json`
- **操作**: 
  - 安装 Vue 3, Vite, Pinia, Vue Router, Axios
  - 安装 Tailwind CSS 及相关插件
  - 安装 @vitejs/plugin-pwa

#### Task 2: Tailwind CSS 配置
- **文件**: `frontend/tailwind.config.js`
- **操作**: 
  - 配置 content paths
  - 定义瑜伽主题色 (米白、浅灰、淡绿)
  - 配置自定义字体

#### Task 3: Axios HTTP Client 封装
- **文件**: `frontend/src/utils/http.ts`
- **操作**: 
  - 创建 axios instance
  - 设置 baseURL, timeout
  - 添加 request/response interceptors
  - 统一错误处理

#### Task 4: Vue Router 配置
- **文件**: `frontend/src/router/index.ts`
- **操作**: 
  - 定义路由：/, /booking, /my-bookings
  - 配置路由元信息 (meta)
  - 添加路由守卫

---

### 📱 UI 组件开发阶段 (任务 5-10)

#### Task 5: 日期选择器组件
- **文件**: `frontend/src/components/DatePicker.vue`
- **操作**: 
  - 实现月份切换视图
  - 高亮可用日期
  - 响应式布局适配移动端

#### Task 6: 教练卡片组件
- **文件**: `frontend/src/components/InstructorCard.vue`
- **操作**: 
  - 显示头像、姓名、简介
  - 展示可约时间段列表
  - 点击选中状态

#### Task 7: 时间槽选择器组件
- **文件**: `frontend/src/components/TimeSlotPicker.vue`
- **操作**: 
  - 网格布局展示可用时段
  - ✓ (可用) / ✗ (已选满) 状态标识
  - 点击选中/取消

#### Task 8: 预约表单组件
- **文件**: `frontend/src/components/BookingForm.vue`
- **操作**: 
  - 姓名输入框 (required, validation)
  - 电话输入框 (required, phone format validation)
  - 备注文本域 (optional)

#### Task 9: PWA Manifest 配置
- **文件**: `frontend/public/manifest.json`
- **操作**: 
  - 定义应用名称、图标
  - 设置主题色、背景色
  - 配置 display: standalone

#### Task 10: PWA Service Worker 配置
- **文件**: `frontend/src/pwa-config.js`
- **操作**: 
  - 使用 vitePWA plugin
  - 配置缓存策略 (静态资源)
  - 实现离线页面支持

---

### 🗄️ Pinia Store & API 集成阶段 (任务 11-15)

#### Task 11: instructors store
- **文件**: `frontend/src/stores/instructors.ts`
- **操作**: 
  - 定义 state: list, selectedId
  - Action: fetchInstructorsByDate(date)
  - Getter: availableSlotsMap

#### Task 12: schedules store
- **文件**: `frontend/src/stores/schedules.ts`
- **操作**: 
  - 定义 state: slots[], selectedSlot
  - Action: fetchSchedules(date, instructorId)
  - Action: selectSlot(slotId)

#### Task 13: bookings store + API 集成
- **文件**: `frontend/src/stores/bookings.ts`
- **操作**: 
  - 定义 state: myBookings[], currentBooking
  - Action: submitBooking(formData) → POST /api/v1/bookings
  - Action: fetchMyBookings(phone) → GET /api/v1/bookings?phone=xxx
  - Action: cancelBooking(bookingId)

#### Task 14: BookingPage 页面组件
- **文件**: `frontend/src/views/BookingPage.vue`
- **操作**: 
  - 组合 DatePicker + InstructorCard + TimeSlotPicker + BookingForm
  - 实现预约流程状态管理 (step 1→2→3→4)
  - 表单提交到 bookings store

#### Task 15: MyBookings 页面组件
- **文件**: `frontend/src/views/MyBookings.vue`
- **操作**: 
  - 电话输入框 + 查询按钮
  - 列表展示预约记录 (时间、教练、状态)
  - 取消按钮 (仅未开始的预约)

---

### 🎨 UI 优化与测试阶段 (任务 16-18)

#### Task 16: 移动端响应式优化
- **文件**: `frontend/src/assets/css/tailwind.css` + 各组件
- **操作**: 
  - 大按钮设计 (min-height: 44px)
  - touch-friendly spacing
  - 适配不同手机尺寸

#### Task 17: Loading & Error UI
- **文件**: `frontend/src/components/LoadingSpinner.vue`, `ErrorBoundary.vue`
- **操作**: 
  - 数据加载时的 loading 状态
  - API 错误友好提示
  - 网络异常处理

#### Task 18: PWA 图标资源生成
- **文件**: `frontend/public/icons/*`
- **操作**: 
  - 生成多尺寸图标 (192x192, 512x512)
  - 添加 maskable icon
  - favicon.ico

---

## 📋 API 接口映射表

| Store Action | HTTP Method | Endpoint |
|--------------|-------------|----------|
| fetchInstructorsByDate(date) | GET | /api/v1/instructors?date=xxx |
| fetchSchedules(date, instructorId) | GET | /api/v1/schedules?date=xxx&instructor_id=xxx |
| submitBooking(formData) | POST | /api/v1/bookings |
| fetchMyBookings(phone) | GET | /api/v1/bookings?phone=xxx |

---

## ✅ 验收标准

- [ ] 所有组件使用 Composition API (setup() 或 <script setup>)
- [ ] Pinia stores 完整实现 state/action/getter 模式
- [ ] Axios interceptors 统一处理错误和 token
- [ ] PWA 可添加到主屏，离线有提示页面
- [ ] 移动端预约流程可在 3 步内完成

---

*创建时间：2026-04-13*  
*预计完成：Phase 3 (6 小时)*
