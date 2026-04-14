# 🐳 Docker Service Management Guide

**Appt Yoga Booking System - 快速管理脚本使用指南**

---

## 🚀 Quick Start (一分钟上手)

### 启动服务
```bash
./manage.sh start
```
- 自动构建最新代码
- 启动数据库、后端 API、前端应用
- 等待健康检查通过 (~15 秒)
- 显示访问 URL

### 停止服务
```bash
./manage.sh stop
```
- 优雅关闭所有容器
- **保留数据**（数据库不会丢失）

### 重启服务（代码更新后使用）
```bash
./manage.sh restart
```
- 先停止现有服务
- 重新构建 Docker 镜像
- 启动最新版本的服務

---

## 📋 Available Commands (可用命令)

| Command | Description | When to Use |
|---------|-------------|-------------|
| `start` | Build and start all services | First time, or after pulling new code |
| `stop` | Stop all services gracefully | Temporary shutdown, preserve data |
| `restart` | Rebuild and restart everything | After making code changes |
| `status` | Show service health & status | Check if system is running properly |
| `logs [service]` | View logs (follow mode) | Debugging issues |
| `clean` | Remove ALL data + containers | Fresh start, **⚠️ destroys database!** |
| `shell` | Access container shells | Interactive debugging |

---

## 💡 Common Workflows (常见工作流)

### Scenario 1: Daily Development Start
```bash
# Morning: Start services
./manage.sh start

# Check everything is healthy  
./manage.sh status

# Open browser
echo "Visit http://localhost:8080 in your browser"
```

### Scenario 2: After Code Changes
```bash
# Commit your changes first (optional but recommended)
git add . && git commit -m "Your changes here"

# Restart with rebuild
./manage.sh restart

# Verify services are healthy
./manage.sh status

# Test in browser
echo "Visit http://localhost:8080 to test new features"
```

### Scenario 3: Debugging Issues
```bash
# Check service status first
./manage.sh status

# View backend logs (if API errors)
./manage.sh logs backend

# Or view all services logs  
./manage.sh logs

# Press Ctrl+C to stop following logs
```

### Scenario 4: Access Database Directly
```bash
# Option 1: Use manage.sh shell menu
./manage.sh shell
# Then type 'appt-db' and press Enter

# Option 2: Direct command (faster)
docker exec -it appt-db psql -U appt -d appt_db

# Useful SQL queries:
SELECT * FROM instructors;           # View all coaches
SELECT COUNT(*) FROM bookings;        # Total booking count  
SELECT * FROM bookings WHERE status = 'confirmed';  # Active bookings
```

### Scenario 5: Fresh Start (Delete Everything)
```bash
⚠️ WARNING: This will DELETE ALL DATABASE DATA!

./manage.sh clean

# Confirm by typing 'yes' when prompted

# Then rebuild from scratch
./manage.sh start

# Re-seed database with sample data (if needed)
docker exec appt-backend python scripts/seed_data.py
```

---

## 🔍 Command Details & Examples

### `start` - Start Services
**What it does:**
- Builds Docker images from latest code (`--build` flag)
- Starts all services in background mode (`-d` flag)
- Waits 15 seconds for health checks
- Shows service status and access URLs

**Output example:**
```
================================================================
Starting Appt Services
================================================================
ℹ Building and starting all services...
✓ All services started successfully!
ℹ Waiting for services to become healthy (this may take ~30 seconds)...

================================================================
Service Status
================================================================

SERVICE              STATUS                    PORTS                         
appt-db              running (healthy)         5432                          
appt-backend         running (healthy)         8000                          
appt-frontend        running (starting)        8080                          

ℹ Checking service accessibility...
✓ Frontend (port 8080) is responding
✓ Backend API (port 8000) is healthy

Access URLs:
  Frontend:     http://localhost:8080
  Backend API:  http://localhost:8000
  Swagger Docs: http://localhost:8000/docs
```

### `status` - Check Health
**What it does:**
- Shows running/stopped status for each service
- Displays health check results (healthy/unhealthy/starting)
- Lists exposed ports
- Tests if services are actually responding to requests

**Color coding:**
- 🟢 Green = healthy/running normally
- 🟡 Yellow = starting or degraded  
- 🔴 Red = stopped, unhealthy, or not found

### `logs [service]` - View Logs
**Usage examples:**
```bash
# Follow all service logs (like docker-compose logs -f)
./manage.sh logs

# View specific service only
./manage.sh logs backend    # FastAPI application logs
./manage.sh logs frontend   # Nginx access logs  
./manage.sh logs db         # PostgreSQL query logs

# Show last 100 lines instead of default 50
./manage.sh logs --tail=100 backend

# Stop following: Press Ctrl+C
```

**Common log patterns to look for:**
- Backend startup: `INFO:     Application startup complete.`
- Database ready: `database system is ready to accept connections`  
- Frontend serving: Nginx access logs showing 200 OK responses
- Errors: Look for lines starting with `ERROR:` or `Exception:`

### `clean` - Nuclear Option ⚠️
**WARNING:** This command will:
- ❌ Delete all database data (irreversible!)
- ❌ Remove all Docker volumes
- ❌ Stop and remove all containers
- ❌ Delete custom networks

**When to use:**
- Fresh installation testing
- Database corruption recovery  
- Complete reset after major bugs

**Safer alternative:** Just stop services without deleting data:
```bash
./manage.sh stop    # Preserves database
```

### `shell` - Interactive Debugging
**Usage:**
```bash
./manage.sh shell
# Then choose: appt-db, appt-backend, appt-frontend, or 'all'
```

**Common tasks in shells:**

#### PostgreSQL Shell (appt-db)
```sql
-- View all tables
\dt

-- List instructors with their schedules
SELECT i.name, COUNT(s.id) as schedule_count 
FROM instructors i 
LEFT JOIN schedules s ON i.id = s.instructor_id 
GROUP BY i.id, i.name;

-- Check recent bookings
SELECT customer_name, phone_masked, created_at 
FROM bookings 
ORDER BY created_at DESC 
LIMIT 10;

-- Quit shell
\q
```

#### Backend Shell (appt-backend)  
```bash
# List files in container
ls -la /app

# Check Python environment
python --version
pip list | grep fastapi

# Test database connection from inside container
python -c "from app.core.config import settings; print(settings.DATABASE_URL)"

# Exit shell  
exit
```

#### Frontend Shell (appt-frontend)
```bash
# View served files
ls -la /usr/share/nginx/html

# Check nginx configuration
cat /etc/nginx/conf.d/default.conf

# Test if nginx is running
ps aux | grep nginx

# Exit shell
exit
```

---

## 🔧 Troubleshooting Guide

### Problem: Services won't start
**Symptoms:** `./manage.sh start` fails with errors

**Solutions:**
1. **Check Docker daemon is running:**
   ```bash
   systemctl status docker
   
   # If not running, start it:
   sudo systemctl start docker
   ```

2. **Check ports are available:**
   ```bash
   # See what's using the required ports
   sudo lsof -i :8080  # Frontend port
   sudo lsof -i :8000  # Backend port  
   sudo lsof -i :5432  # Database port
   
   # Kill conflicting processes (be careful!)
   sudo kill -9 <PID>
   ```

3. **Check disk space:**
   ```bash
   df -h /var/lib/docker
   
   # If >85% full, clean up old images:
   docker system prune -a
   ```

4. **Try fresh start:**
   ```bash
   ./manage.sh clean    # ⚠️ Deletes all data!
   ./manage.sh start
   ```

### Problem: Frontend shows blank page or 502 error
**Diagnosis:**
```bash
./manage.sh logs frontend
```

**Common causes & fixes:**

1. **Build failed silently:**
   ```bash
   # Check build output in detail
   docker-compose build frontend
   
   # Look for TypeScript/Vue compilation errors
   ```

2. **Nginx config issue:**
   ```bash
   # Test nginx configuration  
   docker exec appt-frontend nginx -t
   
   # View current config
   docker exec appt-frontend cat /etc/nginx/conf.d/default.conf
   ```

3. **SPA routing problem (404 on refresh):**
   - This is expected for Vue Router in production mode
   - Fix: Configure nginx `try_files $uri /index.html;`

### Problem: Backend API returns 500 errors
**Diagnosis:**
```bash
./manage.sh logs backend --tail=100
```

**Common causes & fixes:**

1. **Database not ready yet:**
   ```bash
   # Wait for database to be healthy
   ./manage.sh status
   
   # Check if you can connect  
   docker exec appt-backend python -c "from app.db.database import SessionLocal; print('DB OK' if SessionLocal() else 'DB Failed')"
   ```

2. **Missing environment variables:**
   ```bash
   # Check .env file exists and has required values
   cat .env | grep SECRET_KEY
   cat .env | grep DATABASE_URL
   
   # Restart to pick up changes
   ./manage.sh restart
   ```

3. **Migration issues:**
   ```bash
   # Run database migrations manually
   docker exec appt-backend alembic upgrade head
   ```

### Problem: Database is empty after start
**Solution:** Re-run seed script
```bash
# Check if tables exist but have no data
docker exec appt-db psql -U appt -d appt_db -c "SELECT COUNT(*) FROM instructors;"

# If count is 0, run seed script:
docker exec appt-backend python scripts/seed_data.py

# Verify data was added  
./manage.sh status
```

### Problem: Can't access http://localhost:8080 from another device
**Solution:** Bind to all interfaces (0.0.0.0) instead of localhost

Check `docker-compose.yml`:
```yaml
ports:
  - "0.0.0.0:8080:80"    # ✅ Accessible from network
  # NOT this:
  - "127.0.0.1:8080:80"  # ❌ Only localhost access
```

Then restart:
```bash
./manage.sh restart
```

Access from other devices on same network using your computer's IP:
- `http://<YOUR_IP>:8080` (e.g., http://192.168.1.100:8080)

---

## 📚 Additional Resources

### Docker Commands Reference
```bash
# View all running containers  
docker ps -a

# Remove stopped containers
docker container prune

# Remove unused images
docker image prune -a  

# View disk usage
docker system df

# Clean everything (images, volumes, networks)
docker system prune -a --volumes
```

### Useful Docker Compose Commands
```bash
# See detailed resource usage
docker stats appt-db appt-backend appt-frontend

# Execute arbitrary command in container  
docker exec appt-backend ls -la /app

# Copy files into running container
docker cp local-file.txt appt-backend:/app/remote-file.txt

# View container configuration
docker inspect appt-backend
```

### Project-Specific URLs (when services are running)
- **Frontend SPA:** http://localhost:8080
- **Backend API Docs (Swagger):** http://localhost:8000/docs  
- **Alternative API Docs (ReDoc):** http://localhost:8000/redoc
- **Health Check Endpoint:** http://localhost:8000/health

---

## 🎯 Best Practices

### Daily Development Workflow
```bash
# 1. Pull latest code from git
git pull origin develop

# 2. Restart services with rebuild  
./manage.sh restart

# 3. Verify everything is healthy
./manage.sh status

# 4. Test in browser before making changes
echo "Testing at http://localhost:8080"

# 5. Make code changes...

# 6. Repeat from step 2 after significant changes
```

### Before Committing Code
```bash
# Check your local changes don't break the build
./manage.sh restart

# Verify services start successfully  
./manage.sh status

# Quick smoke test: curl backend health endpoint
curl http://localhost:8000/health | jq .

# If all good, commit and push
git add . && git commit -m "Your changes" && git push origin develop
```

### Production Deployment Checklist
- [ ] All services pass health checks (`./manage.sh status` shows healthy)
- [ ] Database seeded with required data
- [ ] Environment variables configured for production (`.env.prod`)
- [ ] CORS origins set to production domain whitelist  
- [ ] SECRET_KEY is strong and unique (not default value)
- [ ] Firewall rules allow only necessary ports (80/443, not 5432/8000)
- [ ] SSL certificate configured (Let's Encrypt or similar)
- [ ] Database backup strategy in place

---

## 🆘 Getting Help

If you encounter issues not covered here:

1. **Check existing documentation:**
   - `README.md` - General project overview  
   - `DEPLOYMENT.md` - Production deployment guide
   - BUGFIX_* files - Known issues and solutions

2. **Search error messages in logs:**
   ```bash
   ./manage.sh logs backend 2>&1 | grep ERROR
   ```

3. **Ask the AI assistant (me!):**
   - Describe what you're trying to do
   - Share error output from `./manage.sh status` or `logs`
   - Include relevant code changes if recent

---

*Document Created: 2026-04-14 21:15 GMT+8*  
*Maintained By: Rogers (AI Assistant)*  
*Version: 1.0*  

**Happy coding! 🧘‍♀️✨**
