# Appt 前端项目结构

## 📁 目录组织

```
frontend/src/
├── api/                          # API 服务层
│   └── services.ts               # API 调用封装
│
├── assets/                       # 静态资源
│   ├── logo.svg
│   └── tailwind.css
│
├── components/                   # 可复用组件 (全局共享)
│   ├── admin/                    # 管理后台专用组件
│   │   ├── InstructorModal.vue
│   │   ├── ScheduleModal.vue
│   │   └── Sidebar.vue
│   ├── BookingForm.vue           # C 端预约表单
│   └── InstructorCard.vue        # C 端教练卡片
│
├── layouts/                      # 页面布局
│   └── AdminLayout.vue           # PC 管理后台布局（侧边栏导航）
│
├── router/                       # Vue Router 路由配置
│   └── index.ts                  # 主路由文件
│
├── stores/                       # Pinia 状态管理
│   └── auth.ts                   # 认证状态
│
├── types/                        # TypeScript 类型定义
│   └── api-types.ts
│
├── views/                        # 页面视图
│   ├── customer/                 # C 端页面 (移动端优先)
│   │   ├── Home.vue              # 首页
│   │   ├── BookingPage.vue       # 预约课程页
│   │   └── MyBookings.vue        # 我的预约
│   ├── auth/                     # 认证页面
│   │   ├── Login.vue             # 登录
│   │   └── Register.vue          # 注册
│   └── ...
│
├── admin/                        # PC 管理后台 (独立访问)
│   ├── views/                    # 管理后台页面视图
│   │   ├── Dashboard.vue         # 仪表盘
│   │   ├── InstructorManagement.vue  # 教练管理
│   │   ├── ScheduleManagement.vue    # 排课管理
│   │   └── UserManagement.vue        # 用户管理
│   └── layouts/                  # 管理后台布局 (侧边栏)
│       └── AdminLayout.vue       # PC 端专用布局
│
├── App.vue                       # C 端主应用组件 (Header/Footer)
├── main.ts                       # 入口文件
└── vite.config.ts                # Vite 配置
```

## 🌐 访问路径

### C 端页面 (移动端优先，响应式设计)

| 路径 | 描述 | 认证要求 |
|------|------|----------|
| `/` | 首页 - 展示瑜伽馆信息和预约入口 | ❌ 公开 |
| `/login` | 用户登录 | ❌ 仅访客 |
| `/register` | 注册新账户 | ❌ 仅访客 |
| `/booking` | 预约课程页 - 选择教练/时间/填写信息 | ❌ 公开 |
| `/my-bookings` | 我的预约 - 查看历史预约 | ✅ 已登录 |

### PC 管理后台 (独立页面，桌面端优化)

| 路径 | 描述 | 认证要求 |
|------|------|----------|
| `/admin/dashboard` | 仪表盘 - 数据统计概览 | ✅ 管理员 |
| `/admin/instructors` | 教练管理 - CRUD 操作 | ✅ 管理员 |
| `/admin/schedules` | 排课管理 - 课程安排 | ✅ 管理员 |
| `/admin/users` | 用户管理 - 客户信息查看 | ✅ 管理员 |

## 🎨 UI/UX 设计原则

### C 端页面特点：
- **移动端优先**: 响应式设计，适配手机、平板、桌面
- **简洁直观**: Apple Design System 风格
- **流畅交互**: 动画过渡，即时反馈
- **Header/Footer**: 统一导航和页脚

### PC 管理后台特点：
- **独立布局**: 左侧侧边栏 + 右侧内容区（类似传统后台）
- **数据密集**: 表格、图表、表单操作
- **键盘友好**: 支持快捷键操作
- **全屏利用**: 充分利用桌面屏幕空间

## 🔄 路由守卫逻辑

```typescript
// C 端路由 (无需特殊权限)
/ -> Home.vue (App.vue layout)
/login -> Login.vue (App.vue layout)  
/register -> Register.vue (App.vue layout)
/booking -> BookingPage.vue (App.vue layout)
/my-bookings -> MyBookings.vue (App.vue layout)

// PC 管理后台路由 (AdminLayout wrapper)
/admin/dashboard -> Dashboard.vue (AdminLayout.vue)
/admin/instructors -> InstructorManagement.vue (AdminLayout.vue)
/admin/schedules -> ScheduleManagement.vue (AdminLayout.vue)
/admin/users -> UserManagement.vue (AdminLayout.vue)
```

**关键点**: 
- 管理后台使用 `AdminLayout.vue` 作为父组件，**不会显示 C 端的 Header/Footer**
- 两者是完全独立的 UI 体系，互不干扰

## 📦 构建产物

```
dist/
├── index.html                    # 入口 HTML
├── assets/
│   ├── *.css                     # 样式文件 (按路由拆分)
│   └── *.js                      # JS 文件 (代码分割)
└── ...
```

## 🚀 开发命令

```bash
# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

---

*最后更新：2026-04-16 (管理后台 PC 独立化重构)*
