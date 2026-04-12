# 压力测试指南 - Stress Test Guide

## 🎯 任务概述

**Task 85**: 压力测试：50 并发预约请求模拟

本测试模拟 50 个并发用户同时进行预约操作，验证系统在负载下的性能和稳定性。

---

## 📋 测试文件说明

### 1. `stress_test_50_concurrent.py`
- **用途**: Python asyncio + aiohttp 实现的精确并发控制压力测试
- **特点**: 
  - 精确控制并发用户数（默认 50）
  - 使用异步 I/O，真实模拟网络请求
  - 详细的统计报告和性能指标
  - JSON 格式结果导出

### 2. `performance_test.py` (Locust)
- **用途**: Locust 框架的分布式压力测试
- **特点**:
  - Web UI 可视化监控
  - 支持分布式测试集群
  - 复杂用户行为模拟

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
   pip install aiohttp asyncio locust
   ```

### 执行方式 A：使用 Shell 脚本（推荐）

```bash
cd /home/claw/.openclaw/workspace-rogers/projects/appt/backend
chmod +x run_stress_test.sh
./run_stress_test.sh http://localhost:8000 50
```

参数说明：
- `http://localhost:8000`: API 服务器地址（可选，默认 localhost:8000）
- `50`: 并发用户数（可选，默认 50）

### 执行方式 B：直接运行 Python 脚本

```bash
cd /home/claw/.openclaw/workspace-rogers/projects/appt/backend
python tests/stress_test_50_concurrent.py \
    --url http://localhost:8000 \
    --users 50 \
    --output stress_test_results.json
```

### 执行方式 C：使用 Locust（Web UI）

```bash
cd /home/claw/.openclaw/workspace-rogers/projects/appt/backend
locust -f tests/performance_test.py --host http://localhost:8000
```

然后在浏览器打开 `http://localhost:8089`，配置：
- **User Count**: 50
- **Spawn Rate**: 10 (每秒启动 10 个用户)
- **Run Time**: 60s (运行时长)

---

## 📊 测试结果指标

### 性能目标（Apple Design System）

| 指标 | 目标值 | 说明 |
|------|--------|------|
| **平均响应时间** | <200ms | API 处理时间的平均值 |
| **P95 响应时间** | <300ms | 95% 的请求在此时间内完成 |
| **失败率** | <1% | 请求失败的百分比 |

### 报告输出

测试完成后会生成以下信息：

1. **控制台输出**:
   - 总请求数 / 成功数 / 失败数
   - 响应时间统计（平均、最小、最大）
   - 百分位数（P50, P95, P99）
   - HTTP 状态码分布
   - 性能目标验证结果

2. **JSON 文件** (`stress_test_results.json`):
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

## 🔧 性能优化建议

如果测试结果未达标，可参考以下优化方向：

### 数据库层面
- ✅ **添加索引**: `instructor_id`, `schedule_date`, `customer_phone`
- ✅ **使用连接池**: 配置 `pool_size=10`, `max_overflow=20`
- ✅ **查询优化**: 使用 `joinedload()` 避免 N+1 问题

### API 层面
- ✅ **响应压缩**: 启用 Gzip 压缩
- ✅ **缓存策略**: Redis 缓存热点数据（教练列表、排课信息）
- ✅ **异步处理**: 非关键操作使用后台任务队列

### 应用层
- ✅ **请求限流**: 防止恶意刷接口
- ✅ **超时控制**: 设置合理的数据库查询超时
- ✅ **错误降级**: 部分服务失败时不影响核心功能

---

## 📝 测试场景覆盖

### 已实现的测试场景

1. **用户注册与登录** (Auth Flow)
   - 新瑜伽馆注册
   - 管理员登录获取 Token

2. **教练管理** (Instructor Management)
   - 创建/更新/禁用教练
   - 批量操作性能

3. **排课管理** (Schedule Management)
   - 单次排课创建
   - 周排课批量创建

4. **预约流程** (Booking Flow) ⭐ 重点测试
   - 并发提交预约请求
   - 冲突检测机制验证
   - 数据一致性检查

---

## 🛠️ Troubleshooting

### Q: "Server not responding" 错误

**A**: 确保 API 服务器已启动并监听正确端口：
```bash
# 检查服务状态
curl http://localhost:8000/health

# 如果没有响应，启动服务器
cd backend && uvicorn app.main:app --reload
```

### Q: 测试失败率高（>10%）

**A**: 
1. 检查服务器日志，查看具体错误原因
2. 确认数据库连接正常
3. 验证预约数据没有冲突（同一时间段重复预约会返回 409）

### Q: 响应时间超过目标值

**A**:
1. 检查数据库索引是否完善
2. 减少单次查询的数据量
3. 考虑引入 Redis 缓存
4. 使用 `EXPLAIN` 分析慢查询

---

## 📚 相关文档

- [Locust 官方文档](https://docs.locust.io/)
- [FastAPI 性能优化指南](https://fastapi.tiangolo.com/deployment/performance/)
- [SQLAlchemy 查询优化](https://docs.sqlalchemy.org/en/20/core/connections.html#using-sqlite-with-future-style-synchronous-connection-pooling)

---

## ✅ Task 85 完成标准

- [x] 创建 `stress_test_50_concurrent.py` 并发测试脚本
- [x] 实现精确的 50 用户并发控制
- [x] 生成完整的性能分析报告
- [x] 支持 JSON 格式结果导出
- [x] 提供 Shell 脚本简化执行流程
- [x] 验证 API 响应时间 <200ms（平均）
- [x] 验证失败率 <1%

---

**最后更新**: 2026-04-11  
**维护者**: Rogers (罗杰斯) 🤖
