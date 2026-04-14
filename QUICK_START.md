# ⚡ Quick Start - Appt Yoga Booking System

**一分钟上手指南**

---

## 🚀 第一次使用 (5 分钟完成)

### Step 1: Clone & Setup (如果还没克隆代码)
```bash
git clone https://github.com/rogerle/appt.git
cd appt
cp .env.example .env   # 复制环境变量模板
# nano .env            # 编辑配置（可选，使用默认值也可以）
```

### Step 2: Start Services (启动服务)  
```bash
./manage.sh start
```

等待 ~30 秒，看到以下输出表示成功：
```
✓ All services started successfully!
✓ Frontend (port 8080) is responding
✓ Backend API (port 8000) is healthy
```

### Step 3: Open Browser (打开浏览器访问)
**http://localhost:8080** 🎉

---

## 📱 Daily Commands (日常使用命令)

### Start (启动服务)
```bash
./manage.sh start
```

### Stop (停止服务，保留数据)  
```bash
./manage.sh stop
```

### Restart (重启并重新构建，代码更新后用这个)
```bash
./manage.sh restart
```

### Check Status (检查状态)
```bash
./manage.sh status
```

### View Logs (查看日志)
```bash
# All services
./manage.sh logs

# Specific service  
./manage.sh logs backend   # API 日志
./manage.sh logs frontend  # 前端访问日志
./manage.sh logs db        # 数据库日志

# Press Ctrl+C to stop following
```

---

## 🔗 Access URLs (访问地址)

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:8080 | Vue.js SPA - 预约界面 |
| **Backend API** | http://localhost:8000 | FastAPI REST API |
| **Swagger Docs** | http://localhost:8000/docs | Interactive API testing |
| **ReDoc** | http://localhost:8000/redoc | Alternative API documentation |

---

## 🎯 Test Booking Flow (测试预约流程)

1. 打开 http://localhost:8080
2. Click "立即预约" button  
3. Select a future date (e.g., tomorrow)
4. Choose an instructor (张伟 / 李娜 / 王强)
5. Pick a time slot with available spots
6. Fill in your name and phone number
7. Submit booking ✅

**Expected:** Booking created successfully, redirected to MyBookings page showing new reservation! 🎊

---

## 🔧 Common Issues (常见问题速查)

### Port already in use
```bash
# See what's using the port
sudo lsof -i :8080   # or 8000 / 5432

# Kill the process  
sudo kill -9 <PID>

# Then restart services
./manage.sh start
```

### Database is empty
```bash
docker exec appt-backend python scripts/seed_data.py
```

### Services won't start
```bash
# Check Docker daemon
systemctl status docker

# If stopped, start it:
sudo systemctl start docker

# Then try again  
./manage.sh start
```

---

## 📚 More Documentation (详细文档)

- **README.md** - Full project overview and architecture
- **docs/DOCKER_MANAGEMENT.md** - Complete manage.sh command reference + troubleshooting  
- **docs/PHASE4_COMPLETE.md** - Development history and feature summary
- **docs/SYSTEM_STATUS.md** - Current system health report

---

## 🆘 Need Help? (需要帮助？)

```bash
# See all available commands
./manage.sh help

# View detailed documentation  
cat docs/DOCKER_MANAGEMENT.md
```

Or ask the AI assistant (Rogers) with error messages from logs! 💬

---

*Quick Start Guide - Keep this handy for daily development!* 📌
