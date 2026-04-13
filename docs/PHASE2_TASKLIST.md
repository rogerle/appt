# Phase 2: 数据库设计 + API 基础框架 - 任务拆解表

**目标**: 完成 SQLAlchemy ORM models、Pydantic schemas、Alembic 配置以及核心 API 端点（Auth、Instructors、Schedules、Bookings）

**预估总耗时**: 4 小时  
**任务数量**: 17 个

## 📋 任务列表

| ID | 任务名称 | 描述 | 文件路径 | 预估耗时 | 依赖 |
|----|----------|------|----------|----------|------|
| P2-01 | 配置数据库连接 | 创建 SQLAlchemy 引擎和会话管理，支持 PostgreSQL | `backend/app/db/database.py` | 15min | - |
| P2-02 | 创建 Studio 模型 | 实现 studios 表的 ORM 模型（id, name, phone, address） | `backend/app/db/models/studio.py` | 15min | P2-01 |
| P2-03 | 创建 Instructor 模型 | 实现 instructors 表 ORM 模型，包含与 studio 的外键关系 | `backend/app/db/models/instructor.py` | 20min | P2-01, P2-02 |
| P2-04 | 创建 Schedule 模型 | 实现 schedules 表 ORM 模型（日期、时间、最大预约数） | `backend/app/db/models/schedule.py` | 25min | P2-01, P2-03 |
| P2-05 | 创建 Booking 模型 | 实现 bookings 表 ORM 模型，包含状态枚举和备注字段 | `backend/app/db/models/booking.py` | 20min | P2-01, P2-04 |
| P2-06 | 统一导出所有模型 | 在 models/__init__.py 中集中导出所有 ORM 模型 | `backend/app/db/models/__init__.py` | 5min | P2-02~P2-05 |
| P2-07 | 配置 Alembic | 初始化 Alembic 迁移工具，配置与 SQLAlchemy 的集成 | `backend/alembic.ini` + `backend/alembic/` | 20min | P2-01, P2-06 |
| P2-08 | 创建初始迁移脚本 | 生成首条 Alembic migration，包含所有表结构 | `backend/alembic/versions/xxxx_initial_schema.py` | 15min | P2-07 |
| P2-09 | 创建 Auth Pydantic Schemas | 定义登录/注册的请求和响应模型（LoginRequest, RegisterRequest） | `backend/app/schemas/auth.py` | 15min | - |
| P2-10 | 创建 Instructor Pydantic Schemas | 定义教练 CRUD 的请求/响应模型 | `backend/app/schemas/instructor.py` | 15min | - |
| P2-11 | 创建 Schedule Pydantic Schemas | 定义排课计划的请求/响应模型（含批量创建） | `backend/app/schemas/schedule.py` | 15min | - |
| P2-12 | 创建 Booking Pydantic Schemas | 定义预约的请求/响应模型，包含冲突检测字段 | `backend/app/schemas/booking.py` | 15min | - |
| P2-13 | 实现 JWT 认证工具 | 实现 token 生成、验证和依赖注入的 helper 函数 | `backend/app/core/security.py` | 20min | - |
| P2-14 | 实现 Auth API 端点 | 完成 /api/v1/auth/login 和 /register 接口逻辑 | `backend/app/api/v1/auth.py` | 25min | P2-09, P2-13 |
| P2-15 | 实现 Instructors API 端点 | 完成教练 CRUD（GET/POST/PUT/DELETE）四个端点 | `backend/app/api/v1/instructors.py` | 30min | P2-10, P2-13 |
| P2-16 | 实现 Schedules API 端点 | 完成排课创建、列表查询、批量创建三个端点 | `backend/app/api/v1/schedules.py` | 35min | P2-11, P2-13 |
| P2-17 | 实现 Bookings API 端点 | 完成预约创建（含冲突检测）和取消预约端点 | `backend/app/api/v1/bookings.py` | 40min | P2-12, P2-13 |

---

## 📊 任务分类统计

| 类别 | 任务 ID | 数量 |
|------|--------|------|
| **数据库模型** | P2-01 ~ P2-06 | 6 |
| **迁移配置** | P2-07 ~ P2-08 | 2 |
| **Pydantic Schemas** | P2-09 ~ P2-12 | 4 |
| **API 端点** | P2-13 ~ P2-17 | 5 |

---

## 🔗 依赖关系图

```
P2-01 (数据库连接)
   ├── P2-02 (Studio) ──┐
   ├── P2-03 (Instructor) │
   ├── P2-04 (Schedule)   │
   └── P2-05 (Booking)    │
                          ↓
P2-06 (统一导出) ───────→ P2-07 (Alembic 配置) → P2-08 (初始迁移)

独立任务（无依赖）:
- P2-09 ~ P2-12 (Schemas，可并行开发)
- P2-13 (JWT 认证工具)

API 端点（需等待 Schema + JWT 完成）:
P2-14 (Auth API) ←──┬─ P2-09, P2-13
P2-15 (Instructors) ─┴─ P2-10, P2-13
P2-16 (Schedules)   ──┬─ P2-11, P2-13
P2-17 (Bookings)    ─┴─ P2-12, P2-13
```

---

## ✅ 验收检查点

完成 Phase 2 后应满足：

- [ ] `docker-compose up` 启动后端服务成功
- [ ] 访问 `/api/docs` 能看到 Swagger UI 和所有端点
- [ ] Alembic migration 可成功执行：`alembic upgrade head`
- [ ] Auth API: POST /login 返回有效 JWT token
- [ ] Instructors API: CRUD 操作全部通过测试
- [ ] Schedules API: 单条创建 + 批量创建均正常
- [ ] Bookings API: 冲突检测生效（同一时段不超限）

---

*生成时间：2026-04-13*  
*依据文档：PROJECT_SPEC.md v1.1*
