# Appt - 瑜伽馆预约系统

## 📋 项目概述

一个轻量级的瑜伽馆预约管理系统，专为小型独立瑜伽馆和个人教练设计。解决传统电话 + 手工记录的低效问题，提供简洁易用的在线预约功能。

**核心理念**: 简单、专注、本地部署、无需复杂配置

---

## 🎯 目标用户
- 小型独立瑜伽馆（1-5 人团队）
- 个人瑜伽教练
- 人手有限的微型工作室

**痛点解决**: 
- ❌ 电话预约容易漏单/冲突
- ❌ 手工记录效率低、易出错
- ✅ 在线选择时间 + 教练，自动避免冲突

---

## 🚀 技术栈

### 前端
- **框架**: Vue 3 + Composition API
- **构建工具**: Vite
- **状态管理**: Pinia
- **样式**: Tailwind CSS
- **PWA**: @vitejs/plugin-pwa（移动端体验，无需下载 App）

### 后端
- **框架**: FastAPI (Python)
- **ORM**: SQLAlchemy
- **验证**: Pydantic
- **数据库**: PostgreSQL (本地部署)

### 部署
- **容器化**: Docker + Docker Compose
- **模式**: 本地部署为主（瑜伽馆自行维护）

---

## 📦 核心功能清单

### 1. 后台管理端（瑜伽馆/教练使用）

#### 教练管理
- [ ] 添加教练信息（姓名、头像简介）
- [ ] 启用/禁用教练
- [ ] 设置教练可授课时间范围

#### 排课管理
- [ ] 创建排课计划（选择教练 + 时间段）
- [ ] 设置日期和时间段（如：周一 10:00-11:00）
- [ ] 批量复制周排课
- [ ] 查看某日/某教练的预约情况

#### 预约管理
- [ ] 查看所有预约列表（按日期筛选）
- [ ] 手动取消预约
- [ ] 导出预约数据（CSV/Excel）

---

### 2. 用户预约端（客户使用）

#### 浏览功能
- [ ] 查看教练介绍和可约时间
- [ ] 按日期筛选可用时段

#### 预约流程
1. **选择教练** → 
2. **选择时间段** → 
3. **填写信息**（姓名、电话）→ 
4. **提交预约**

#### 个人中心
- [ ] 查看我的预约记录
- [ ] 取消未开始的预约
- [ ] 历史记录查询

---

## 🗄️ 数据库设计

### 核心表结构

```sql
-- 瑜伽馆信息
CREATE TABLE studios (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 教练信息
CREATE TABLE instructors (
    id SERIAL PRIMARY KEY,
    studio_id INT REFERENCES studios(id),
    name VARCHAR(50) NOT NULL,
    avatar_url TEXT,
    description TEXT,          -- 教练简介
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 排课计划（可预约时间段）
CREATE TABLE schedules (
    id SERIAL PRIMARY KEY,
    instructor_id INT REFERENCES instructors(id),
    studio_id INT REFERENCES studios(id),
    schedule_date DATE NOT NULL,      -- 日期
    start_time TIME NOT NULL,         -- 开始时间
    end_time TIME NOT NULL,           -- 结束时间
    max_bookings INT DEFAULT 1,       -- 最大预约人数（默认单人课）
    is_recurring BOOLEAN DEFAULT FALSE,  -- 是否重复排课
    recurrence_pattern JSONB,         -- 重复规则（如：每周周一三五）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 防止时间冲突的约束
    CONSTRAINT time_overlap CHECK (end_time > start_time)
);

-- 预约记录
CREATE TABLE bookings (
    id SERIAL PRIMARY KEY,
    schedule_id INT REFERENCES schedules(id),
    customer_name VARCHAR(50) NOT NULL,
    customer_phone VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'confirmed',  -- confirmed/cancelled/no_show
    notes TEXT,                          -- 备注（如：过敏史、特殊需求）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 确保同时间段预约不超限
    CONSTRAINT booking_limit CHECK (
        (SELECT COUNT(*) FROM bookings WHERE schedule_id = schedules.id AND status != 'cancelled') <= 
        (SELECT max_bookings FROM schedules WHERE id = schedule_id)
    )
);

-- 索引优化查询性能
CREATE INDEX idx_schedules_date ON schedules(schedule_date);
CREATE INDEX idx_bookings_schedule ON bookings(schedule_id);
CREATE INDEX idx_bookings_customer ON bookings(customer_phone);
```

---

## 🔌 API 接口设计

### 用户端 API（公开访问）

#### 1. 获取教练列表（按日期筛选）
```http
GET /api/v1/instructors?date=2026-04-15
Response: 
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "李老师",
      "avatar_url": "/avatars/li.jpg",
      "available_slots": [
        {"time": "10:00-11:00"},
        {"time": "15:00-16:00"}
      ]
    }
  ]
}
```

#### 2. 获取某日期的可用时间段（按教练筛选）
```http
GET /api/v1/schedules?date=2026-04-15&instructor_id=1
Response:
{
  "success": true,
  "data": [
    {
      "id": 101,
      "start_time": "10:00",
      "end_time": "11:00",
      "available_spots": 1,
      "booked_spots": 0
    }
  ]
}
```

#### 3. 提交预约
```http
POST /api/v1/bookings
Body: {
  "schedule_id": 101,
  "customer_name": "张三",
  "customer_phone": "13800138000",
  "notes": "第一次来瑜伽课"
}

Response:
{
  "success": true,
  "data": {
    "id": 501,
    "confirmation_code": "YOGA20260415",
    "message": "预约成功！"
  }
}
```

#### 4. 查看我的预约
```http
GET /api/v1/bookings?phone=13800138000
Response:
{
  "success": true,
  "data": [
    {
      "id": 501,
      "instructor": "李老师",
      "date": "2026-04-15",
      "time": "10:00-11:00",
      "status": "confirmed"
    }
  ]
}
```

---

### 管理端 API（需要认证）

#### 1. 登录/注册
```http
POST /api/v1/auth/login
Body: { "username": "studio_owner", "password": "xxx" }

POST /api/v1/auth/register
Body: { 
  "studio_name": "阳光瑜伽馆", 
  "owner_phone": "13800138000",
  "password": "xxx" 
}
```

#### 2. 创建教练
```http
POST /api/v1/studio/instructors
Headers: { Authorization: Bearer <token> }
Body: {
  "name": "李老师",
  "description": "擅长哈他瑜伽和冥想课程"
}
```

#### 3. 创建排课计划（仅选择教练 + 时间）
```http
POST /api/v1/studio/schedules
Headers: { Authorization: Bearer <token> }
Body: {
  "instructor_id": 3,
  "schedule_date": "2026-04-15",
  "start_time": "10:00",
  "end_time": "11:00",
  "max_bookings": 1
}
```

#### 4. 批量创建周排课
```http
POST /api/v1/studio/schedules/batch
Headers: { Authorization: Bearer <token> }
Body: {
  "instructor_id": 3,
  "start_date": "2026-04-15",
  "end_date": "2026-04-21",
  "weekdays": [1, 3, 5],  // 周一三五
  "start_time": "10:00",
  "end_time": "11:00"
}
```

#### 5. 获取预约列表
```http
GET /api/v1/studio/bookings?date=2026-04-15
Headers: { Authorization: Bearer <token> }

Response:
{
  "success": true,
  "data": [
    {
      "id": 501,
      "customer_name": "张三",
      "customer_phone": "138****8000",
      "instructor": "李老师",
      "time": "10:00-11:00",
      "status": "confirmed"
    }
  ]
}
```

#### 6. 取消预约（管理端）
```http
DELETE /api/v1/studio/bookings/{id}
Headers: { Authorization: Bearer <token> }
```

---

## 🎨 UI/UX设计要求

### 风格定位
- **色调**: 柔和、宁静的色彩（米白、浅灰、淡绿）
- **字体**: 清晰易读的无衬线字体
- **图标**: 简约线条图标，避免过多装饰

### 移动端优先
- ✅ 响应式设计，适配各种手机尺寸
- ✅ PWA 支持：添加主屏图标、离线缓存
- ✅ 大按钮设计，方便手指点击
- ✅ 简洁流程，3 步内完成预约

### 关键页面布局

#### 用户预约页 (`/booking`)
```
┌─────────────────────┐
│   Logo + 标题        │
├─────────────────────┤
│  [日期选择器]        │
├─────────────────────┤
│  [教练选择]          │
│  (显示头像)         │
├─────────────────────┤
│  [可用时间段网格]    │
│  ✓ 10:00-11:00      │
│  ✓ 15:00-16:00      │
│  ✗ 已选             │
├─────────────────────┤
│  [姓名输入框]        │
│  [电话输入框]        │
├─────────────────────┤
│     [提交预约]       │
└─────────────────────┘
```

#### 管理后台 (`/admin/dashboard`)
```
┌───────────────────────────┐
│ Logo | 欢迎，阳光瑜伽馆   │
├───────────────────────────┤
│ 侧边栏导航：               │
│ - 📊 今日预约              │
│ - 📅 排课管理              │
│ - 👥 教练管理              │
│ - ⚙️ 设置                 │
├───────────────────────────┤
│ 主内容区：今日预约列表      │
│ ┌────┬────┬────┬────┐    │
│ │时间│学员│教练│操作│    │
│ ├────┼────┼────┼────┤    │
│ │10:00│张三│李老师│详情│   │
│ └────┴────┴────┴────┘    │
└───────────────────────────┘
```

---

## 🐳 Docker Compose 配置

### docker-compose.yml
```yaml
version: '3.8'

services:
  # PostgreSQL 数据库
  postgres:
    image: postgres:15-alpine
    container_name: appt-db
    environment:
      POSTGRES_DB: appt
      POSTGRES_USER: appt_user
      POSTGRES_PASSWORD: appt_password_2026
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U appt_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Python FastAPI 后端
  backend:
    build: ./backend
    container_name: appt-backend
    environment:
      DATABASE_URL: postgresql://appt_user:appt_password_2026@postgres:5432/appt
      FASTAPI_ENV: production
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./backend:/app

  # Vue 3 前端
  frontend:
    build: ./frontend
    container_name: appt-frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    volumes:
      - ./frontend:/app

volumes:
  postgres_data:
```

---

## 📝 开发规范

### 代码风格
- **前端**: ESLint + Prettier (Vue3 推荐配置)
- **后端**: Black + Flake8 (Python 标准格式)

### Git 分支策略
```
main              # 生产环境
├── develop       # 开发分支
├── feature/*    # 功能分支（如：feature/booking-system）
└── hotfix/*     # 紧急修复分支
```

### API 版本管理
- URL 路径包含版本号：`/api/v1/...`
- 保持向后兼容，新版本通过 `/api/v2/` 发布

---

## 🚀 部署流程（本地部署）

### 1. 环境准备
```bash
# 安装 Docker 和 Docker Compose
curl -fsSL https://get.docker.com | sh
sudo systemctl enable docker
```

### 2. 克隆项目
```bash
git clone <repository-url> appt
cd appt
```

### 3. 一键启动
```bash
docker-compose up -d

# 查看日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 4. 初始化数据库
```bash
# 运行迁移脚本（首次部署）
docker-compose exec backend python alembic upgrade head
```

### 5. 访问系统
- 前端：http://localhost
- API: http://localhost:8000/api/docs (自动生成的 Swagger UI)

---

## 📊 项目文件结构

```
appt/
├── frontend/                  # Vue 3 + Vite 前端
│   ├── public/               # 静态资源
│   │   ├── icons/           # PWA 图标
│   │   └── favicon.ico
│   ├── src/
│   │   ├── assets/          # CSS/图片资源
│   │   ├── components/      # 可复用组件
│   │   │   ├── TimeSlotPicker.vue
│   │   │   └── BookingForm.vue
│   │   ├── views/           # 页面组件
│   │   │   ├── BookingPage.vue       # 预约页
│   │   │   ├── MyBookings.vue        # 我的预约
│   │   │   └── admin/                # 管理后台
│   │   ├── stores/          # Pinia store
│   │   ├── router/          # Vue Router 配置
│   │   └── pwa-config.js    # PWA 配置
│   ├── index.html
│   ├── vite.config.ts
│   └── package.json
│
├── backend/                   # Python FastAPI 后端
│   ├── app/
│   │   ├── api/             # API路由
│   │   │   ├── v1/
│   │   │   │   ├── auth.py
│   │   │   │   ├── instructors.py
│   │   │   │   ├── schedules.py
│   │   │   │   └── bookings.py
│   │   ├── core/            # 核心配置
│   │   │   ├── config.py    # 环境变量
│   │   │   └── security.py  # JWT认证
│   │   ├── db/              # 数据库相关
│   │   │   ├── database.py  # DB连接
│   │   │   └── models/      # SQLAlchemy模型
│   │   │       ├── instructor.py
│   │   │       └── booking.py
│   │   └── schemas/         # Pydantic 验证模型
│   ├── alembic/             # 数据库迁移
│   ├── Dockerfile
│   └── requirements.txt
│
├── docker-compose.yml       # 容器编排配置
├── README.md                # 项目说明文档
└── .env.example            # 环境变量示例
```

---

## ✅ 验收标准

### 功能验收
- [ ] 用户可以在线选择教练、时间完成预约
- [ ] 管理端可以创建/查看/取消预约
- [ ] 同一时间段不会重复预约（冲突检测）
- [ ] 移动端 PWA 体验流畅，可添加到主屏

### 性能验收
- [ ] API 响应时间在 200ms 以内
- [ ] 页面加载时间 < 3s
- [ ] 支持至少 50 个并发预约请求

### 安全验收
- [ ] 管理端需要登录认证
- [ ] SQL 注入防护（使用 ORM）
- [ ] XSS 防护（Vue 自动转义）
- [ ] CORS 配置正确

---

## 📅 开发时间表（预估）

| 阶段 | 任务 | 耗时 |
|------|------|------|
| **Phase 1** | 项目初始化 + Docker 环境搭建 | 2 小时 |
| **Phase 2** | 数据库设计 + API 基础框架 | 4 小时 |
| **Phase 3** | 用户端核心功能（预约流程） | 6 小时 |
| **Phase 4** | 管理后台功能（排课 + 查看） | 6 小时 |
| **Phase 5** | PWA 配置 + 移动端优化 | 2 小时 |
| **Phase 6** | 测试 + Bug 修复 | 3 小时 |
| **总计** | - | **约 23 小时** |

---

## 📞 联系方式

如有问题，请联系项目负责人。

---

*文档版本：v1.1 (修正后)*  
*最后更新：2026-04-10*  
*修改说明：移除课程管理功能，简化为教练 + 时间安排*  
*创建人：面包（基于与爸爸的头脑风暴）*
