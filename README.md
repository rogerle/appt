# 🧘 Appt - Yoga Studio Scheduler

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Vue3](https://img.shields.io/badge/Vue.js-3.4-blue.svg)](https://vuejs.org/)
[![Docker](https://img.shields.io/badge/Docker-20+-orange.svg)](https://www.docker.com/)

**Professional Yoga Studio Scheduling System with PWA Support**

A complete yoga studio management solution featuring client booking, instructor scheduling, admin dashboard, and production-ready Docker deployment.

---

## ✨ Features

### For Clients
- 📅 **Browse Instructors**: View all yoga instructors with specializations and availability
- 🕐 **Schedule Booking**: Book classes by date and time slot (real-time conflict detection)
- 👤 **My Bookings**: Manage personal reservation history with easy cancellation
- 📱 **PWA Support**: Add to home screen, offline-capable, push notifications ready

### For Instructors
- 📋 **Schedule Management**: View weekly schedule at a glance
- ⏰ **Availability Control**: Set working hours and time slots
- 📊 **Booking Overview**: Track upcoming reservations per session

### For Administrators
- 👥 **Staff Management**: Add/edit/delete instructors, manage studio locations
- 🗓️ **Schedule Builder**: Create single sessions or bulk weekly schedules
- 💼 **Booking Oversight**: Monitor all bookings, handle cancellations
- 📈 **Dashboard Analytics**: Key metrics and operational insights

---

## 🚀 Quick Start (Docker Deployment)

### Prerequisites
- Docker 20+ and Docker Compose installed
- Port 80/443 available on server
- Domain name configured for SSL certificate

### One-Command Deploy
```bash
# Clone repository
git clone https://github.com/rogerle/appt.git
cd appt

# Configure environment (required)
cp .env.example .env
nano .env  # Edit with your settings

# Start all services
docker-compose -f docker-compose.prod.yml up -d --build

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f backend
```

### Access Application
- Frontend: `http://your-server-ip` (or `https://your-domain.com` with SSL)
- Backend API: `http://your-server-ip/api/docs` (Swagger UI)
- Health Check: `http://your-server-ip/health`

---

## 🔧 Environment Configuration

### Required Variables (.env)

```bash
# Database Settings
DATABASE_URL=postgresql://appt_user:your_secure_password@db:5432/appt_production

# Security (Generate with: python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
SECRET_KEY=<your-secure-secret-key-here>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15

# Application Mode (Development/Production)
DEBUG=False
ENVIRONMENT=production

# CORS Configuration (Comma-separated list of allowed origins)
ALLOWED_ORIGINS=["https://your-domain.com","https://www.your-domain.com"]

# Performance Tuning
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
DATABASE_POOL_RECYCLE=3600
```

### Development Environment (Optional Override)

For local development testing:
```bash
export DATABASE_URL=sqlite:///./dev.db
export DEBUG=True
export ALLOWED_ORIGINS=["http://localhost:5173"]
```

---

## 📦 Installation Guide

### Option 1: Docker Production Deployment (Recommended)

#### Step 1: Prepare Server
```bash
# SSH into your VPS
ssh root@your-server-ip

# Update system and install dependencies
apt update && apt upgrade -y
apt install -y docker.io docker-compose git curl ufw

# Install Node.js for frontend builds (optional, already in Docker image)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
apt install -y nodejs

# Enable firewall
ufw allow ssh
ufw allow 'Nginx Full'  # HTTP + HTTPS if using reverse proxy
ufw enable
```

#### Step 2: Deploy Application
```bash
# Create application directory
mkdir -p /opt/appt && cd /opt/appt

# Clone repository
git clone https://github.com/rogerle/appt.git .

# Configure environment variables
cp .env.example .env
nano .env  # Edit as needed

# Build and start containers
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# Verify deployment
docker-compose ps  # Should show all services running
curl http://localhost/health  # Should return {"status":"ok"}
```

#### Step 3: Configure SSL Certificate (Let's Encrypt)
```bash
# Install Certbot and Nginx plugin
apt install -y certbot python3-certbot-nginx

# Obtain certificate for your domain
certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal configured automatically at 0 0 * * *
```

#### Step 4: Configure Nginx Reverse Proxy (If not using Docker Compose nginx)
Create `/etc/nginx/sites-available/appt`:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    
    # Backend API proxy
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # Timeouts for booking operations
        proxy_connect_timeout 60s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }

    # Frontend static files (if serving from host)
    location / {
        root /var/www/appt-frontend;
        index index.html;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/appt /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### Option 2: Local Development Setup

#### Backend (FastAPI)
```bash
cd projects/appt/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# OR: venv\Scripts\activate  # Windows

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Set DATABASE_URL=sqlite:///./dev.db, DEBUG=True

# Initialize database (if using PostgreSQL)
alembic upgrade head

# Start development server with hot-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend (Vue3 + Vite)
```bash
cd projects/appt/frontend

# Install dependencies
npm install

# Configure environment (optional)
cp .env.example .env.local
nano .env.local  # Set API_BASE_URL=http://localhost:8000/api/v1 if needed

# Start development server
npm run dev
```

#### Access Application Locally
- Frontend: `http://localhost:5173`
- Backend API Docs: `http://localhost:8000/docs` (Swagger UI)
- Health Check: `http://localhost:8000/health`

---

## 🧪 Testing & Quality Assurance

### Run Test Suite
```bash
cd projects/appt/backend

# Unit tests (Fastest, <10s)
pytest tests/test_api_v1.py -v

# Integration tests (<30s)
pytest tests/test_integration.py -xvs

# Security tests (SQL injection, XSS, CORS)
./tests/run_security_tests.sh

# Performance/load testing (requires server running)
locust -f tests/performance_test.py --host http://localhost:8000
```

### Coverage Report
```bash
# Generate HTML coverage report
pytest tests/ --cov=app --cov-report=html --cov-report=term-missing

# View in browser
xdg-open htmlcov/index.html  # Linux
open htmlcov/index.html      # macOS
start htmlcov/index.html     # Windows
```

---

## 📊 Performance Targets (Apple Design System)

| Metric | Target | Status |
|--------|--------|--------|
| Average Response Time | <200ms | ✅ Measured per test run |
| P95 Response Time | <300ms | ✅ Enforced in k6 thresholds |
| Failure Rate | <1% | ✅ Monitored across all phases |
| Concurrent Users Support | 50+ | ✅ Tested with stress scenarios |

### Performance Monitoring
```bash
# Real-time API performance tracking (check response headers)
curl -I http://localhost:8000/api/v1/instructors

# Look for X-Response-Time header in output
# Example: X-Response-Time: 45.23ms
```

---

## 🔒 Security Features

### Implemented Protections ✅
- **SQL Injection Prevention**: SQLAlchemy ORM parameterized queries + middleware pattern detection
- **XSS Protection**: Input sanitization middleware + HTML escaping + Content-Security-Policy headers
- **CORS Misconfiguration Prevention**: Production-safe origin whitelist (never use `["*"]` with credentials)
- **Input Validation**: Pydantic models enforce strict type checking across all endpoints
- **Password Security**: bcrypt hashing with automatic cost factor determination
- **JWT Authentication**: HS256 algorithm + configurable expiration enforcement

### Pre-Deployment Checklist
```bash
# Run automated security test suite
cd projects/appt/backend && ./tests/run_security_tests.sh

# Verify no critical vulnerabilities detected:
✅ SQL Injection Vulnerabilities: 0 (ORM protection)
✅ XSS Vulnerabilities: 0 (Sanitization + escaping)
✅ CORS Misconfigurations: 0 (Production-safe settings)
```

---

## 📚 API Documentation

### Interactive Swagger UI
Access the full API documentation at: `http://your-domain.com/api/docs`

Features:
- Try it out directly from browser
- View request/response schemas
- Authentication token management
- Real-time validation feedback

### OpenAPI Specification
The API follows OpenAPI 3.0 standard, generated automatically by FastAPI.

```bash
# Download OpenAPI spec JSON
curl http://localhost:8000/openapi.json > openapi-spec.json

# Generate client SDK (example using openapi-generator)
openapi-generator generate -i openapi-spec.json -g typescript-axios -o ./generated-client
```

---

## 🛠️ Troubleshooting

### Common Issues & Solutions

#### Issue: "Could not obtain a connection from the pool"
**Symptoms**: Database errors in logs, 503 Service Unavailable

**Solution**: Increase database pool size in `.env`
```bash
DATABASE_POOL_SIZE=20  # Default is 10
DATABASE_MAX_OVERFLOW=40  # Default is 20

# Restart containers to apply changes
docker-compose restart backend
```

#### Issue: CORS errors in browser console
**Symptoms**: "Access-Control-Allow-Origin" error when accessing API from frontend

**Solution**: Verify ALLOWED_ORIGINS matches frontend domain
```bash
# Check .env configuration
grep ALLOWED_ORIGINS .env

# Update if needed (include both http and https variants)
ALLOWED_ORIGINS=["http://localhost:5173","https://your-domain.com"]

# Restart backend service
docker-compose restart backend
```

#### Issue: Frontend not loading after deployment
**Symptoms**: 404 Not Found when accessing root URL

**Solution**: Check Nginx configuration or frontend build output
```bash
# Verify frontend dist files exist (if using direct VPS deployment)
ls -la /home/appt/appt-yoga-scheduler/projects/appt/frontend/dist/

# If missing, rebuild frontend
cd projects/appt/frontend && npm run build

# Or use Docker Compose to serve frontend via nginx container
docker-compose up -d --build
```

#### Issue: SSL certificate not working
**Symptoms**: Browser shows "Not Secure" or connection refused on port 443

**Solution**: Verify certificate installation and Nginx configuration
```bash
# Check if Let's Encrypt certificates exist
ls -la /etc/letsencrypt/live/your-domain.com/

# Test Nginx SSL configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx

# Force HTTPS redirect (if not already configured)
certbot --nginx -d your-domain.com
```

---

## 📦 Docker Compose Architecture

### Services Overview
| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| `backend` | Custom Python 3.10 | 8000 | FastAPI REST API server |
| `frontend` | Custom Node.js + Nginx | 80 (host) / 5173 (internal) | Vue3 PWA static files |
| `db` | postgres:14-alpine | 5432 | PostgreSQL database |
| `nginx` | nginx:alpine | 80/443 | Reverse proxy + SSL termination |

### Volume Mounts
- `pgdata`: Persistent PostgreSQL data (survives container restarts)
- Backend: Read-only application code mount for development hot-reload

### Network Configuration
```yaml
networks:
  appt-network:
    driver: bridge  # Isolated internal network between containers
```

---

## 🔄 Deployment Workflow

### CI/CD Integration (GitHub Actions Example)

Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test-and-build:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          
      - name: Install backend dependencies
        run: |
          cd projects/appt/backend
          pip install -r requirements.txt
          pytest tests/ --cov=app --cov-report=xml
      
      - name: Upload coverage reports
        uses: codecov/codecov-action@v3
        
      - name: Build Docker images
        run: docker-compose -f docker-compose.prod.yml build --no-cache
        
  deploy:
    needs: test-and-build
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to server via SSH
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_IP }}
          username: root
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /opt/appt
            docker-compose -f docker-compose.prod.yml pull
            docker-compose -f docker-compose.prod.yml up -d --build
```

---

## 📈 Monitoring & Logging

### Application Logs
```bash
# View backend logs (last 100 lines)
docker-compose logs --tail=100 backend

# Follow live logs
docker-compose logs -f backend

# View specific time range
docker-compose logs --since="2026-04-11T00:00:00" backend
```

### Health Check Endpoints
```bash
# Basic health status
curl http://localhost/health  # Returns {"status":"ok"}

# Detailed system metrics (if monitoring enabled)
curl http://localhost/api/v1/monitoring/status | jq .
```

### Database Backup Automation
```bash
# Create backup script (saved as /opt/appt/scripts/backup.sh)
cat > scripts/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups/appt"
DATE=$(date +%Y%m%d_%H%M%S)
docker exec appt-db pg_dump -U appt_user appt_production > $BACKUP_DIR/backup_${DATE}.sql
gzip $BACKUP_DIR/backup_${DATE}.sql
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
EOF

chmod +x scripts/backup.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/appt/scripts/backup.sh") | crontab -
```

---

## 🎯 Production Checklist

### Pre-Launch Verification
- [ ] All tests passing (`pytest tests/`)
- [ ] Security scan completed (no vulnerabilities detected)
- [ ] SSL certificate obtained and configured (HTTPS working)
- [ ] Database migrations applied (`alembic upgrade head`)
- [ ] Environment variables set correctly in production `.env`
- [ ] CORS origins whitelisted with specific domains (not wildcards)
- [ ] Firewall rules configured (UFW active, only necessary ports open)
- [ ] Automated backup script installed and tested
- [ ] Monitoring/health checks accessible (`/health` endpoint responding)
- [ ] Admin accounts created and credentials secured

### Post-Launch Monitoring
- [ ] Application logs being written to files (check `docker-compose logs`)
- [ ] Database performance within acceptable ranges (<200ms average response)
- [ ] Error rate below 1% threshold
- [ ] Memory/CPU usage monitored (watch for leaks or spikes)
- [ ] SSL certificate auto-renewal tested (`certbot renew --dry-run`)

---

## 👨‍💻 Development Workflow

### Git Branch Strategy
```bash
# Main branches
git checkout main          # Production-ready code
git checkout develop       # Integration branch for next release

# Feature branches (create from develop)
git checkout -b feature/new-instructor-module develop

# After completing feature, merge to develop via pull request
git push origin feature/new-instructor-module

# When ready to release, merge develop → main with version tag
git checkout main && git merge develop
git tag -a v1.0.0 -m "Release 1.0.0"
git push origin main --tags
```

### Code Quality Tools (Recommended)
```bash
# Backend linting and formatting
pip install black flake8 mypy

black app/ tests/
flake8 app/ tests/
mypy app/

# Frontend linting
npm run lint  # ESLint + Prettier
```

---

## 📞 Support & Resources

### Documentation Links
- **FastAPI Official Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy ORM Guide**: https://docs.sqlalchemy.org/en/20/orm/quickstart.html
- **Vue3 Documentation**: https://vuejs.org/guide/introduction.html
- **Docker Best Practices**: https://docs.docker.com/build/building/best-practices/
- **Let's Encrypt Setup**: https://letsencrypt.org/getting-started/

### Project-Specific Guides
- **Performance Optimization**: `projects/appt/backend/docs/PERFORMANCE_OPTIMIZATION.md`
- **Security Best Practices**: `projects/appt/backend/docs/SECURITY_GUIDE.md`
- **Deployment Instructions**: `DEPLOYMENT.md` (this file)

### Community & Issues
- GitHub Issues: https://github.com/rogerle/appt/issues
- License: MIT (free for commercial and non-commercial use)

---

## 📜 License

This project is licensed under the MIT License - see below for details.

```text
MIT License

Copyright (c) 2026 Rogers (罗杰斯) / Appt Project Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 Acknowledgments

- **FastAPI Team**: For the excellent web framework and documentation
- **Vue.js Community**: For the intuitive frontend framework
- **PostgreSQL Team**: For the powerful open-source database
- **Docker Team**: For simplifying containerization
- **Apple Design System**: Performance targets inspired by Apple Human Interface Guidelines

---

**Version**: 1.0.0  
**Last Updated**: 2026-04-12  
**Maintained by**: Rogers (罗杰斯) 🤖  
**Phase 9 Status**: ✅ Complete (All Testing & Security Tasks Finished)  
**Ready for Production Deployment**: ✅ Yes
