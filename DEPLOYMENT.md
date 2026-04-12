# 🚀 Appt Yoga Studio Scheduler - Deployment Guide

## Task 88: Deployment Documentation ✅ Completed

### 📋 Overview

This comprehensive deployment guide covers:
- Development environment setup
- Production deployment on VPS/cloud infrastructure
- Docker containerization (optional)
- CI/CD pipeline configuration
- Environment-specific configurations
- Security hardening checklist
- Monitoring and logging setup

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Development Environment Setup](#development-environment-setup)
3. [Production Deployment](#production-deployment)
4. [Docker Deployment (Optional)](#docker-deployment-optional)
5. [Environment Configuration](#environment-configuration)
6. [Security Hardening](#security-hardening)
7. [Monitoring & Logging](#monitoring--logging)
8. [Backup & Recovery](#backup--recovery)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

| Component | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.10+ | Backend runtime |
| **Node.js** | 18+ | Frontend build tools |
| **PostgreSQL** | 14+ (Production) / SQLite (Dev/Test) | Database |
| **Git** | Latest | Version control |
| **Docker** (Optional) | 20+ | Containerization |

### Cloud Infrastructure Requirements

For production deployment on VPS:
- **CPU**: 2+ cores recommended
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 20GB SSD
- **OS**: Ubuntu 22.04 LTS or Debian 11+
- **Network**: Public IP with port 80/443 open

---

## Development Environment Setup

### Step 1: Clone Repository

```bash
git clone https://github.com/your-org/appt-yoga-scheduler.git
cd appt-yoga-scheduler
```

### Step 2: Backend Setup

```bash
cd projects/appt/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
nano .env  # Edit as needed

# Run database migrations (if using PostgreSQL)
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 3: Frontend Setup

```bash
cd projects/appt/frontend

# Install dependencies
npm install

# Configure environment variables (optional)
cp .env.example .env.local

# Start development server
npm run dev

# Access application at: http://localhost:5173
```

### Step 4: Run Tests

```bash
cd projects/appt/backend

# Unit tests
pytest tests/test_api_v1.py -v

# Integration tests
pytest tests/test_integration.py -xvs

# Security tests
./tests/run_security_tests.sh

# Performance tests (requires server running)
npm run test:performance  # If configured
```

---

## Production Deployment

### Option A: Direct VPS Deployment (Recommended for Small Teams)

#### Step 1: Server Preparation

```bash
# SSH into your VPS
ssh root@your-server-ip

# Update system packages
apt update && apt upgrade -y

# Install required software
apt install -y python3.10 python3-pip nodejs npm nginx postgresql git curl

# Create application user
useradd -m -s /bin/bash appt
sudo -i -u appt bash
```

#### Step 2: Backend Deployment

```bash
# As appt user
cd ~

# Clone repository (or use existing deployment)
git clone https://github.com/your-org/appt-yoga-scheduler.git
cd appt-yoga-scheduler/projects/appt/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create production database
sudo -u postgres psql -c "CREATE DATABASE appt_production;"
sudo -u postgres psql -c "CREATE USER appt_user WITH PASSWORD 'your_secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE appt_production TO appt_user;"

# Configure environment variables
cat > .env << EOF
DATABASE_URL=postgresql://appt_user:your_secure_password@localhost/appt_production
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
DEBUG=False
ENVIRONMENT=production

# CORS settings for production
ALLOWED_ORIGINS=["https://your-domain.com","https://www.your-domain.com"]
EOF

# Run database migrations
alembic upgrade head

# Test the application locally first
uvicorn app.main:app --reload --port 8001 &
sleep 5
curl http://localhost:8001/health
kill %1

# Stop test server if running
pkill -f uvicorn
```

#### Step 3: Create Systemd Service

```bash
sudo nano /etc/systemd/system/appt-backend.service
```

Add the following content:

```ini
[Unit]
Description=Appt Yoga Studio Backend API
After=network.target postgresql.service

[Service]
Type=simple
User=appt
Group=appt
WorkingDirectory=/home/appt/appt-yoga-scheduler/projects/appt/backend
Environment="PATH=/home/appt/appt-yoga-scheduler/projects/appt/backend/venv/bin"
ExecStart=/home/appt/appt-yoga-scheduler/projects/appt/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable appt-backend
sudo systemctl start appt-backend
sudo systemctl status appt-backend
```

#### Step 4: Frontend Deployment

```bash
cd /home/appt/appt-yoga-scheduler/projects/appt/frontend

# Install dependencies
npm install

# Build for production
npm run build

# The built files will be in /home/appt/appt-yoga-scheduler/projects/appt/frontend/dist/
```

#### Step 5: Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/appt
```

Add the following configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Redirect HTTP to HTTPS (after obtaining SSL certificate)
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL Configuration (obtain certificate with Let's Encrypt later)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # Security headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Backend API proxy
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeout settings for long-running requests (bookings)
        proxy_connect_timeout 60s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }

    # Frontend static files
    location / {
        root /home/appt/appt-yoga-scheduler/projects/appt/frontend/dist;
        index index.html;
        
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Health check endpoint (for monitoring)
    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }
}
```

Enable and restart Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/appt /etc/nginx/sites-enabled/
sudo nginx -t  # Test configuration
sudo systemctl reload nginx
```

#### Step 6: SSL Certificate with Let's Encrypt

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal is configured automatically by Certbot
# Test renewal: sudo certbot renew --dry-run
```

---

### Option B: Docker Deployment (Recommended for Scalability)

#### Step 1: Create Docker Compose Configuration

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  # Backend API Service
  backend:
    build: 
      context: .
      dockerfile: Dockerfile.backend
    container_name: appt-backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://appt_user:your_secure_password@db:5432/appt_production
      - SECRET_KEY=${SECRET_KEY}
      - ALGORITHM=HS256
      - ACCESS_TOKEN_EXPIRE_MINUTES=15
      - DEBUG=False
      - ENVIRONMENT=production
    depends_on:
      - db
    restart: unless-stopped
    networks:
      - appt-network

  # Frontend Service (optional, can serve via Nginx directly)
  frontend:
    build: 
      context: .
      dockerfile: Dockerfile.frontend
    container_name: appt-frontend
    ports:
      - "80:80"
    restart: unless-stopped
    networks:
      - appt-network

  # PostgreSQL Database
  db:
    image: postgres:14-alpine
    container_name: appt-db
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=appt_production
      - POSTGRES_USER=appt_user
      - POSTGRES_PASSWORD=your_secure_password
    restart: unless-stopped
    networks:
      - appt-network

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: appt-nginx
    volumes:
      - ./nginx/prod.conf:/etc/nginx/conf.d/default.conf:ro
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - appt-network

volumes:
  pgdata:
    driver: local

networks:
  appt-network:
    driver: bridge
```

#### Step 2: Create Dockerfile.backend

```dockerfile
FROM python:3.10-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY backend/requirements.txt .
RUN pip wheel --no-cache-dir --no-deps -r requirements.txt

# Production image
FROM python:3.10-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /app/.venv .venv/

# Copy application code
COPY backend/ ./backend/

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

#### Step 3: Create Dockerfile.frontend

```dockerfile
FROM node:18-alpine as builder

WORKDIR /app

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ .
RUN npm run build

# Production image with Nginx
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

#### Step 4: Deploy with Docker Compose

```bash
# Generate secure secret key
export SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')

# Build and start services
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend
```

---

## Environment Configuration

### Development (.env)

```bash
DATABASE_URL=sqlite:///./dev.db
SECRET_KEY=your-dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
DEBUG=True
ENVIRONMENT=development
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

### Production (.env)

```bash
DATABASE_URL=postgresql://appt_user:your_secure_password@localhost/appt_production
SECRET_KEY=<generate-with-secrets-token-unsafe-long-string>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
DEBUG=False
ENVIRONMENT=production
ALLOWED_ORIGINS=["https://your-domain.com","https://www.your-domain.com"]

# Performance optimization settings
POOL_SIZE=10
MAX_OVERFLOW=20
POOL_RECYCLE=3600
```

### Testing (.env.test)

```bash
DATABASE_URL=sqlite:///./test.db
SECRET_KEY=test-secret-key-for-automation-only
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
DEBUG=True
ENVIRONMENT=testing
ALLOWED_ORIGINS=["*"]  # Allow all for testing
```

---

## Security Hardening Checklist

### Pre-Deployment Verification

- [ ] **Change all default passwords** (database, admin accounts)
- [ ] **Generate secure SECRET_KEY** using `secrets.token_urlsafe(32)`
- [ ] **Disable DEBUG mode** in production (`DEBUG=False`)
- [ ] **Configure CORS with specific origins** (never use `["*"]` with credentials)
- [ ] **Enable HTTPS** with valid SSL certificate (Let's Encrypt recommended)
- [ ] **Set up firewall rules** (UFW or cloud provider security groups)
- [ ] **Configure database user permissions** (least privilege principle)

### Server Security

```bash
# Install and configure UFW firewall
sudo apt install -y ufw
sudo ufw allow ssh  # Keep SSH accessible!
sudo ufw allow 'Nginx Full'  # HTTP + HTTPS
sudo ufw enable

# Enable fail2ban for brute force protection
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Configure automatic security updates
sudo apt install -y unattended-upgrades
```

### Application Security

- [ ] **SQL Injection**: All queries use parameterized statements (ORM) ✅
- [ ] **XSS Prevention**: Input sanitization + HTML escaping enabled ✅
- [ ] **CORS Misconfiguration**: Production-safe origin whitelist applied ✅
- [ ] **Input Validation**: Pydantic models validate all user input ✅
- [ ] **Password Security**: bcrypt hashing with automatic cost factor ✅
- [ ] **JWT Tokens**: Secure HS256 algorithm + expiration enforcement ✅

### Run Security Tests Before Deployment:

```bash
cd projects/appt/backend
./tests/run_security_tests.sh  # Automated security test suite
pytest tests/test_security.py -v --tb=short
```

---

## Monitoring & Logging

### Application Logging Configuration

Create `logging.conf` in backend root:

```ini
[loggers]
keys=root,app,uvicorn

[handlers]
keys=consoleHandler,fileHandler,errorHandler

[formatters]
keys=detailed

[logger_root]
level=INFO
handlers=consoleHandler,fileHandler

[logger_app]
level=INFO
handlers=fileHandler
qualName=app
propagate=0

[logger_uvicorn]
level=INFO
handlers=consoleHandler
qualName=uvicorn
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=detailed
args=(sys.stdout,)

[handler_fileHandler]
class=FileHandler
level=INFO
formatter=detailed
args=('logs/app.log', 'a')

[handler_errorHandler]
class=FileHandler
level=ERROR
formatter=detailed
args=('logs/error.log', 'a')

[formatter_detailed]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
datefmt=%Y-%m-%d %H:%M:%S
```

Update `app/main.py` to configure logging on startup:

```python
import logging
from logging.config import fileConfig

def setup_logging():
    if os.path.exists('logging.conf'):
        fileConfig('logging.conf', disable_existing_loggers=False)
    else:
        # Fallback configuration
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

# Call in main.py startup event
@app.on_event("startup")
async def startup_event():
    setup_logging()
```

### Health Check Endpoints

Backend automatically provides:
- `GET /health` - Basic health check (returns 200 OK)
- `GET /metrics` (if Prometheus exporter configured)

Add enhanced monitoring endpoint in `app/api/v1/monitoring.py`:

```python
from fastapi import APIRouter
import psutil
import time

router = APIRouter()

@router.get("/status")
async def get_system_status():
    """Get comprehensive system status for monitoring"""
    
    return {
        "uptime": int(time.time() - startup_time),
        "memory_usage": f"{psutil.virtual_memory().percent}%",
        "cpu_usage": f"{psutil.cpu_percent()}%",
        "disk_usage": f"{psutil.disk_usage('/').percent}%",
        "active_connections": connection_manager.total_connections,
        "database_pool_status": {
            "size": engine.pool.size(),
            "checked_in": engine.pool.checkedin(),
            "checked_out": engine.pool.checkedout(),
            "overflow": engine.pool.overflow()
        }
    }
```

### Monitoring Tools Setup

#### Prometheus + Grafana (Optional)

Install and configure Prometheus for metrics collection:

```bash
# Install Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz
tar xvfv prometheus-*.tar.gz
cd prometheus-*
./prometheus --config.file=prometheus.yml

# Configure Prometheus to scrape backend metrics
cat > prometheus.yml << EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'appt-backend'
    static_configs:
      - targets: ['localhost:8000']
EOF
```

#### Application Performance Monitoring (APM)

For production monitoring, consider integrating with:
- **Datadog** - Full-stack APM
- **Sentry** - Error tracking and performance monitoring
- **New Relic** - Application insights

---

## Backup & Recovery

### Database Backup Strategy

Create automated backup script `scripts/backup.sh`:

```bash
#!/bin/bash

# Appt Database Backup Script
# Run this daily via cron: 0 2 * * * /path/to/scripts/backup.sh

BACKUP_DIR="/backups/appt"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="appt_production"
DB_USER="appt_user"

# Ensure backup directory exists
mkdir -p $BACKUP_DIR

# Create database dump
pg_dump -U $DB_USER $DB_NAME > $BACKUP_DIR/${DB_NAME}_${DATE}.sql

# Compress the backup
gzip $BACKUP_DIR/${DB_NAME}_${DATE}.sql

# Retain only last 30 days of backups
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

# Log completion
echo "$(date): Backup completed - ${DB_NAME}_${DATE}.sql.gz" >> /var/log/appt-backup.log
```

Make executable and add to cron:

```bash
chmod +x scripts/backup.sh
sudo crontab -e

# Add this line for daily backup at 2 AM
0 2 * * * /home/appt/appt-yoga-scheduler/scripts/backup.sh
```

### Disaster Recovery Procedures

#### Full System Restore

1. **Restore database from latest backup:**
   ```bash
   gunzip appt_production_20260411_020000.sql.gz
   psql -U appt_user -d appt_production < appt_production_20260411_020000.sql
   ```

2. **Restore application code:**
   ```bash
   cd /home/appt/appt-yoga-scheduler
   git pull origin main  # Or restore from backup if git unavailable
   ```

3. **Restart services:**
   ```bash
   sudo systemctl restart appt-backend nginx
   ```

4. **Verify system health:**
   ```bash
   curl http://localhost/health
   curl http://localhost/api/v1/instructors | jq '.status'  # Should return "success"
   ```

---

## Troubleshooting

### Common Issues and Solutions

#### Issue: Backend service won't start

**Symptoms:** `systemctl status appt-backend` shows error

**Solutions:**
```bash
# Check logs
sudo journalctl -u appt-backend -n 50 --no-pager

# Verify Python virtual environment
cd /home/appt/appt-yoga-scheduler/projects/appt/backend
source venv/bin/activate
python -c "import app.main"  # Should import without errors

# Check database connectivity
psql -U appt_user -d appt_production -c "SELECT 1;"

# Verify permissions
sudo chown -R appt:appt /home/appt/appt-yoga-scheduler/projects/appt/backend/logs/
```

#### Issue: CORS errors in browser console

**Symptoms:** Blocked by CORS policy when accessing API from frontend

**Solutions:**
```bash
# Check backend .env ALLOWED_ORIGINS setting matches frontend domain
grep ALLOWED_ORIGINS projects/appt/backend/.env

# Update configuration if needed
nano /home/appt/appt-yoga-scheduler/projects/appt/backend/.env
# Add your frontend domain: "https://your-domain.com"

# Restart backend service
sudo systemctl restart appt-backend

# Verify CORS headers are set correctly
curl -I -H 'Origin: https://your-domain.com' http://localhost:8000/api/v1/instructors | grep -i access-control
```

#### Issue: Database connection pool exhausted

**Symptoms:** "Could not obtain a connection from the pool" errors in logs

**Solutions:**
```bash
# Check current pool status
sudo journalctl -u appt-backend | grep -i pool

# Increase pool size in .env
nano /home/appt/appt-yoga-scheduler/projects/appt/backend/.env
DATABASE_POOL_SIZE=20  # Increase from default 10
DATABASE_MAX_OVERFLOW=40  # Increase from default 20

# Restart backend to apply changes
sudo systemctl restart appt-backend

# Monitor connection usage over time
watch -n 5 'psql -U appt_user -d appt_production -c "SELECT count(*) FROM pg_stat_activity;"'
```

#### Issue: Slow API responses (>300ms)

**Symptoms:** Users report laggy booking experience, logs show slow queries

**Solutions:**
```bash
# Check slow query logs
sudo journalctl -u appt-backend | grep "Slow"

# Verify indexes are created
psql -U appt_user -d appt_production << EOF
\di
EOF

# Run performance analysis on specific endpoint
curl http://localhost:8000/api/v1/instructors \
  -w "@curl-format.txt" -o /dev/null -s

# Check for N+1 query issues in logs
sudo journalctl -u appt-backend | grep "N+1\|SELECT.*WHERE"
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] All unit tests passing (`pytest tests/test_api_v1.py`)
- [ ] Integration tests passing (`pytest tests/test_integration.py`)
- [ ] Security tests passed (`./tests/run_security_tests.sh`)
- [ ] Performance targets met (API <200ms average)
- [ ] Environment variables configured correctly
- [ ] Database migrations applied (`alembic upgrade head`)
- [ ] SSL certificate obtained and configured

### Post-Deployment Verification

- [ ] Backend API accessible at `https://your-domain.com/api/`
- [ ] Frontend loads without errors at `https://your-domain.com`
- [ ] CORS headers properly set (check browser console)
- [ ] Database queries execute successfully
- [ ] User registration/login works end-to-end
- [ ] Booking creation and management functional
- [ ] Admin dashboard accessible with proper authentication
- [ ] Health check endpoint responds (`/health`)

### Monitoring Setup

- [ ] Application logs being written to `/var/log/appt-backend/`
- [ ] System monitoring (CPU, memory, disk) in place
- [ ] Database backup automation configured
- [ ] Alerting rules defined for critical errors
- [ ] SSL certificate auto-renewal tested

---

## Quick Deployment Commands Reference

```bash
# === Development Setup ===
git clone https://github.com/your-org/appt-yoga-scheduler.git
cd appt-yoga-scheduler/projects/appt/backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
cd ../frontend && npm install && npm run dev

# === Production Deployment (VPS) ===
ssh root@your-server-ip
apt update && apt upgrade -y && apt install -y python3-pip nodejs nginx postgresql git
# Follow steps in "Option A: Direct VPS Deployment" above

# === Docker Deployment ===
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
docker logs -f appt-backend  # Monitor logs
```

---

## Support & Resources

### Documentation References
- **FastAPI Official Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy ORM Guide**: https://docs.sqlalchemy.org/en/20/orm/quickstart.html
- **Nginx Configuration Guide**: https://nginx.org/en/docs/
- **Let's Encrypt Setup**: https://letsencrypt.org/getting-started/

### Project-Specific Resources
- **Performance Optimization Guide**: `projects/appt/backend/docs/PERFORMANCE_OPTIMIZATION.md`
- **Security Best Practices**: `projects/appt/backend/docs/SECURITY_GUIDE.md`
- **API Documentation** (auto-generated): `http://localhost:8000/docs` (Swagger UI)

### Monitoring Dashboards
- Prometheus + Grafana setup guide available on request
- Sentry error tracking integration documentation available
- Custom metrics endpoints documented in `app/api/v1/monitoring.py`

---

*Last Updated: 2026-04-11*  
*Maintained by: Rogers (罗杰斯) 🤖*  
*Task 88 Status: ✅ Complete - Comprehensive deployment documentation created*
