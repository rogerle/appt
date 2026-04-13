# Phase 1: 项目初始化 + Docker 环境搭建

## 📋 原子级任务清单

| ID | 任务名称 | 描述 | 预估耗时 | 依赖 |
|----|----------|------|----------|------|
| P1-01 | 创建项目根目录结构 | 创建 `appt/` 主目录及基础文件夹 (`frontend/`, `backend/`, `.gitignore`) | 2min | - |
| P1-02 | 配置后端核心模块 | 创建 `backend/app/core/` 并编写 `config.py` (配置管理) 和 `security.py` (安全工具) | 8min | P1-01 |
| P1-03 | 创建数据库层基础文件 | 创建 `backend/app/db/` 并编写 `base.py` (BaseModel), `session.py` (会话管理), `init_db.py` (初始化脚本) | 6min | P1-02 |
| P1-04 | 定义数据模型与 Schema | 创建 `backend/app/models/` 和 `schemas/`, 编写用户模型及 Pydantic 验证模式 | 10min | P1-03 |
| P1-05 | 配置 API 路由结构 | 创建 `backend/app/api/v1/` 并编写 `router.py` (主路由) 和 `dependencies.py` (依赖注入) | 6min | P1-04 |
| P1-06 | 完成后端入口与依赖配置 | 创建 `main.py`, `requirements.txt`, `Dockerfile`, `.env.docker` | 8min | P1-05 |
| P1-07 | 初始化 Vue3+Vite 前端项目 | 使用 Vite CLI 创建前端脚手架，安装核心依赖 (Vue, Router, Pinia) | 5min | P1-01 |
| P1-08 | 配置前端目录结构 | 创建 `src/{components,views,stores,router,api}` 目录及基础文件框架 | 6min | P1-07 |
| P1-09 | 编写 Vite 配置文件 | 完成 `vite.config.ts` (代理配置、PWA 插件、构建优化) | 5min | P1-08 |
| P1-10 | 创建前端入口文件 | 编写 `main.ts`, `App.vue`, `index.html`, `router/index.ts`, `stores/user.ts` | 8min | P1-09 |
| P1-11 | 配置 Docker Compose | 编写 `docker-compose.yml` (定义 backend, frontend, postgres, redis 服务) | 10min | P1-06, P1-10 |
| P1-12 | 创建环境变量模板 | 编写 `.env.example` (包含数据库、JWT、API 配置等所有必要变量说明) | 4min | P1-11 |

## 📊 任务统计

- **总任务数**: 12 个
- **预估总耗时**: ~78 分钟 (~1.5 小时)
- **关键路径**: P1-01 → P1-02 → P1-03 → P1-04 → P1-05 → P1-06 → P1-11

## 🗂️ 文件结构映射

```
appt/
├── .gitignore                    # [P1-01]
├── docker-compose.yml            # [P1-11]
├── .env.example                  # [P1-12]
│
├── backend/
│   ├── Dockerfile                # [P1-06]
│   ├── requirements.txt          # [P1-06]
│   ├── .env.docker               # [P1-06]
│   └── app/
│       ├── main.py               # [P1-06]
│       ├── core/
│       │   ├── config.py         # [P1-02]
│       │   └── security.py       # [P1-02]
│       ├── db/
│       │   ├── base.py           # [P1-03]
│       │   ├── session.py        # [P1-03]
│       │   └── init_db.py        # [P1-03]
│       ├── models/               # [P1-04]
│       ├── schemas/              # [P1-04]
│       └── api/v1/
│           ├── router.py         # [P1-05]
│           └── dependencies.py   # [P1-05]
│
└── frontend/
    ├── vite.config.ts            # [P1-09]
    ├── package.json              # [P1-07]
    ├── index.html                # [P1-10]
    └── src/
        ├── main.ts               # [P1-10]
        ├── App.vue               # [P1-10]
        ├── components/           # [P1-08]
        ├── views/                # [P1-08]
        ├── stores/user.ts        # [P1-10]
        └── router/index.ts       # [P1-10]
```

## ✅ 验收标准

Phase 1 完成时，应满足以下条件：
- [ ] `docker-compose up -d` 能成功启动所有服务
- [ ] 后端 FastAPI 应用可通过 http://localhost:8000/docs 访问 Swagger UI
- [ ] 前端 Vue 应用可通过 http://localhost:3000 访问
- [ ] 数据库初始化脚本自动执行完成
- [ ] 环境变量配置完整，无缺失必要项
