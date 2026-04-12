# 🧪 Appt 项目 - 完整测试指南

## 📊 测试金字塔概览

```
                    ┌─────────────┐
                    │   Stress    │ ← Task 85: 50 concurrent users
                  ┌─┤  Testing    │
                  │ └─────────────┘
                ┌─┴─┐
                │Load│ ← Task 84: Locust/k6 load testing
                └───┘
              ┌─────┴─────┐
              │Integration│ ← Task 83: End-to-end user flows
              └───────────┘
            ┌─────────────┴─────────────┐
            │      Unit Tests           │ ← Tasks 81-82 (Backend + Frontend)
            └───────────────────────────┘
```

---

## 🚀 快速开始

### 前置条件

1. **启动 API 服务器**（必需）:
   ```bash
   cd /home/claw/.openclaw/workspace-rogers/projects/appt/backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **安装测试依赖**:
   ```bash
   pip install pytest pytest-asyncio httpx aiohttp locust k6
   ```

---

## ✅ Task 81: Backend Unit Tests (pytest)

**文件位置**: `projects/appt/backend/tests/`

### 测试内容
- **27 个测试用例**覆盖所有 API 端点
- Auth, Instructor, Schedule, Booking 四大模块
- In-memory SQLite 数据库隔离

### 执行方式

```bash
cd /home/claw/.openclaw/workspace-rogers/projects/appt/backend

# 运行所有单元测试
pytest tests/test_api_v1.py -v

# 单个测试文件
pytest tests/test_api_v1.py::test_register_success -xvs

# 生成覆盖率报告
pytest tests/test_api_v1.py --cov=app --cov-report=html
```

### 预期结果
- ✅ All 27 tests pass
- ⏱️ Execution time: <10 seconds
- 📊 Coverage: Auth (8), Instructor (6), Schedule (6), Booking (7)

---

## ✅ Task 83: Backend Integration Tests (pytest + httpx)

**文件位置**: `projects/appt/backend/tests/`

### 测试内容
- **10 个完整用户流程**从注册到预约取消
- End-to-end API 集成验证
- 数据库依赖注入隔离

### 执行方式

```bash
cd /home/claw/.openclaw/workspace-rogers/projects/appt/backend

# 运行所有集成测试
pytest tests/test_integration.py -xvs

# 快速模式（停止于第一个失败）
./run_tests.sh integration
```

### 预期结果
- ✅ All 10 integration flows pass
- ⏱️ Execution time: <30 seconds
- 🔄 Complete user journey validation

---

## ✅ Task 82: Frontend Unit Tests (Vitest)

**文件位置**: `projects/appt/frontend/`

### 测试内容
- **40+ 个测试用例**覆盖所有 Vue 组件和 Pinia store
- Header, Footer, BookingPage, Login 组件测试
- JSDOM browser simulation

### 执行方式

```bash
cd /home/claw/.openclaw/workspace-rogers/projects/appt/frontend

# 运行所有前端单元测试
npm test -- --run

# 单个组件测试
npx vitest run tests/Header.test.vue -v

# 生成覆盖率报告
npm test -- --run --coverage
```

### 预期结果
- ✅ All 40+ component tests pass
- ⏱️ Execution time: <20 seconds
- 📊 Coverage: Components (28), Pinia Store (12)

---

## ✅ Task 84: Performance & Load Testing (Locust/k6)

**文件位置**: `projects/appt/backend/tests/`

### 测试内容
- **9 个负载测试场景**覆盖公共和管理端 API
- Locust Python + k6 JavaScript双框架支持
- P95 <300ms, Failure Rate <1%目标验证

### 执行方式 A: Locust (推荐)

```bash
cd /home/claw/.openclaw/workspace-rogers/projects/appt/backend

# Web UI 交互测试（手动控制）
locust -f tests/performance_test.py --host http://localhost:8000
# 打开浏览器：http://localhost:8089

# Headless模式（自动化）
locust -f tests/performance_test.py --headless \
  -u 50 -r 5 --run-time 120s \
  --host http://localhost:8000
```

### 执行方式 B: k6 (Cloud Native)

```bash
cd /home/claw/.openclaw/workspace-rogers/projects/appt/backend

# Standard load test
k6 run --vus 25 --duration 2m tests/k6_performance.js

# With thresholds enforcement
k6 run \
  --thresholds 'http_req_duration=p(95)<300ms' \
  --thresholds 'http_req_failed=rate<0.01' \
  tests/k6_performance.js
```

### 执行方式 C: Shell Script（一键执行）

```bash
cd /home/claw/.openclaw/workspace-rogers/projects/appt/backend
./run_performance_tests.sh
```

### 性能目标验证
| Metric | Target | Status |
|--------|--------|--------|
| Average Response Time | <100ms | ✅/⚠️ |
| P95 Response Time | <300ms | ✅ Threshold enforced |
| Failure Rate | <1% | ✅ Monitored |

---

## ✅ Task 85: Stress Testing - 50 Concurrent Booking Requests

**文件位置**: `projects/appt/backend/tests/`

### 测试内容
- **精确的 50 并发用户控制**使用 Python asyncio + aiohttp
- Realistic network request simulation
- Comprehensive metrics and JSON export

### 执行方式 A: Shell Script（推荐）

```bash
cd /home/claw/.openclaw/workspace-rogers/projects/appt/backend

# Quick execution with defaults (50 users, localhost:8000)
./run_stress_test.sh

# Custom configuration
./run_stress_test.sh http://localhost:8000 100  # 100 concurrent users
```

### 执行方式 B: Direct Python Execution

```bash
cd /home/claw/.openclaw/workspace-rogers/projects/appt/backend

python tests/stress_test_50_concurrent.py \
    --url http://localhost:8000 \
    --users 50 \
    --output stress_test_results.json
```

### 执行方式 C: Interactive Mode

```bash
# Run with default settings
python -m tests.stress_test_50_concurrent
```

### 测试流程

1. **Setup**: Register test studio + create schedule (one-time)
2. **Concurrent Execution**: 50 simultaneous booking requests via asyncio.gather()
3. **Metrics Collection**: Response times, status codes, success rates
4. **Report Generation**: Console output + JSON file export

### 性能目标验证（Apple Design System）

```python
✅ Average Response Time: <200ms
✅ P95 Response Time: <300ms  
✅ Failure Rate: <1%
```

### 输出示例

**Console Report:**
```
================================================================================
📊 STRESS TEST REPORT - 50 Concurrent Users
================================================================================

🎯 Overall Statistics:
   Total Requests: 50
   Successful: 48 (96.00%)
   Failed: 2 (4.00%)

⏱️  Response Time Analysis:
   Average: 145.32ms
   Minimum: 89.15ms
   Maximum: 456.78ms
   
📈 Percentiles:
   P50 (Median): 132.45ms
   P95: 289.67ms
   P99: 312.34ms

🍎 Performance Target Validation:
   ✅ Average Response Time: 145.32ms (Target: <200ms)
   ✅ P95 Response Time: 289.67ms (Target: <300ms)
   ❌ Failure Rate: 4.00% (Target: <1%)
```

**JSON Export (`stress_test_results.json`):**
```json
{
  "test_type": "50_concurrent_booking_requests",
  "total_requests": 50,
  "successful": 48,
  "failed": 2,
  "failure_rate_percent": 4.0,
  "response_time_stats": {
    "average_ms": 145.32,
    "min_ms": 89.15,
    "max_ms": 456.78,
    "p50_ms": 132.45,
    "p95_ms": 289.67,
    "p99_ms": 312.34
  },
  ...
}
```

---

## 📋 完整测试执行清单

### 推荐顺序（CI/CD友好）

```bash
cd /home/claw/.openclaw/workspace-rogers/projects/appt/backend

# Phase 1: Fast unit tests (<10s)
echo "🧪 Running backend unit tests..."
pytest tests/test_api_v1.py -v --tb=short

# Phase 2: Integration tests (<30s)
echo "🔄 Running integration tests..."
pytest tests/test_integration.py -xvs --tb=short

# Phase 3: Stress test (50 concurrent users, ~5-10s)
echo "⚡ Running stress test with 50 concurrent users..."
./run_stress_test.sh http://localhost:8000 50

# Phase 4: Load testing (optional, ~2-3min)
echo "📊 Running load tests with Locust..."
locust -f tests/performance_test.py --headless \
  -u 50 -r 5 --run-time 120s \
  --host http://localhost:8000

# Phase 5: Frontend unit tests (from frontend directory)
echo "🎨 Running frontend unit tests..."
cd /home/claw/.openclaw/workspace-rogers/projects/appt/frontend
npm test -- --run
```

---

## 🔧 Troubleshooting

### Q1: "Server not responding" 错误

**A**: 确保 API 服务器已启动：
```bash
# Check if server is running
curl http://localhost:8000/health

# If not, start it in a new terminal
cd /home/claw/.openclaw/workspace-rogers/projects/appt/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Q2: "ModuleNotFoundError" 错误

**A**: 安装缺失的依赖：
```bash
pip install pytest pytest-asyncio httpx aiohttp sqlalchemy fastapi uvicorn
cd frontend && npm install vitest @vue/test-utils jsdom
```

### Q3: 测试失败率高（>10%）

**A**: 
1. 检查 API 服务器日志查看具体错误原因
2. 确认数据库连接正常
3. 验证预约数据没有冲突（同一时间段重复预约会返回 409 Conflict）

### Q4: Locust UI 无法访问

**A**: 确保端口 8089未被占用：
```bash
# Check port usage
lsof -i :8089

# Kill process if necessary
kill -9 <PID>
```

---

## 📚 相关文档

- **STRESS_TEST_README.md**: Task 85详细测试指南和故障排除
- **DESIGN.md (Apple)**: Apple Design System 性能目标规范
- **FastAPI Performance Guide**: https://fastapi.tiangolo.com/deployment/performance/

---

## ✅ 验收标准（Task 81-85）

| Task | Deliverables | Acceptance Criteria | Status |
|------|--------------|---------------------|--------|
| **81** | Backend Unit Tests | 27+ test cases, all pass | ✅ Complete |
| **82** | Frontend Unit Tests | 40+ component tests, all pass | ✅ Complete |
| **83** | Integration Tests | 10 user flows, end-to-end validation | ✅ Complete |
| **84** | Load Testing | Locust + k6 configs, P95 <300ms | ✅ Complete |
| **85** | Stress Test (50 concurrent) | Precise concurrency control, JSON export | ✅ Complete |

---

*Last Updated: 2026-04-11*  
*Maintained by: Rogers (罗杰斯) 🤖*  
*Apple Design System Compliance: Fully implemented per projects/appt/apple/DESIGN.md*
