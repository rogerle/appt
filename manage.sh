#!/bin/bash

# ============================================================================
# Appt Yoga Booking System - Docker Service Manager
# ============================================================================
# Usage: ./manage.sh [command]
# Commands: start, stop, restart, status, logs, clean, shell
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m]'
GREEN='\033[0;32m]'
YELLOW='\033[1;33m]'
BLUE='\033[0;34m]'
CYAN='\033[0;36m]'
NC='\033[0m]' # No Color

# Project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$PROJECT_DIR/docker-compose.yml"

# Service names
SERVICES="appt-db appt-backend appt-frontend"

# ============================================================================
# Helper Functions
# ============================================================================

print_header() {
    echo -e "${CYAN}=============================================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}=============================================================${NC}"

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
}

check_compose_file() {
    if [ ! -f "$COMPOSE_FILE" ]; then
        print_error "Docker Compose file not found at: $COMPOSE_FILE"
        exit 1
    fi
}

# Use 'docker compose' (v2) if available, otherwise fall back to 'docker-compose' (v1)
run_compose() {
    if docker compose version &> /dev/null; then
        docker compose -f "$COMPOSE_FILE" "$@"
    else
        docker-compose -f "$COMPOSE_FILE" "$@"
    fi
}

# ============================================================================
# Command Functions
# ============================================================================

cmd_start() {
    print_header "Starting Appt Services (Production Ready)"
    
    cd "$PROJECT_DIR"
    
    echo ""
    echo -e "${GREEN}ℹ️  Production Deployment Mode${NC}"
    echo -e "   • Using Docker Compose with production configuration"
    echo -e "   • Auto-building latest code from git repository"
    echo -e "   • Initializing database and creating admin user"
    echo ""
    
    # Copy admin initialization script to backend container
    if [ -f "$PROJECT_DIR/scripts/init_admin_user.py" ]; then
        print_info "Copying admin initialization script to backend..."
        docker cp "$PROJECT_DIR/scripts/init_admin_user.py" appt-backend:/app/scripts/ 2>/dev/null || {
            echo "⚠️  Could not copy init script - will create it in container if needed"
            # Create directory and file inside container
            docker exec appt-backend mkdir -p /app/scripts 2>/dev/null || true
        }
    fi
    
    print_info "Building and starting all services..."
    run_compose up -d --build
    
    if [ $? -eq 0 ]; then
        print_success "All services started successfully!"
        
        # Wait for services to be healthy
        print_info "Waiting for services to become healthy (this may take ~30 seconds)..."
        sleep 15
        
        # Check if admin user exists, create if not
        print_info "Checking database initialization..."
        check_and_create_admin_user
        
        # Show status
        cmd_status
        
        echo ""
        print_info "Access URLs:"
        echo -e "  ${CYAN}Frontend:${NC} http://localhost:8080"
        echo -e "  ${CYAN}Backend API:${NC} http://localhost:8000"
        echo -e "  ${CYAN}Swagger Docs:${NC} http://localhost:8000/docs"
        echo ""
        
    else
        print_error "Failed to start services. Check the error messages above."
        exit 1
    fi
}

# ============================================================================
# Helper Function: Create Admin User if Not Exists
# ============================================================================
check_and_create_admin_user() {
    # Wait for backend to be fully ready
    print_info "Waiting for backend API to be ready..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            print_success "Backend API is ready!"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            print_error "Backend API not responding after $max_attempts attempts"
            return 1
        fi
        
        attempt=$((attempt + 1))
        sleep 2
    done
    
    # Check if admin user exists via API (try to login)
    local response=$(curl -s http://localhost:8000/api/v1/auth/login \  
      -H "Content-Type: application/json" \  
      -d '{"email":"admin@appt.com","password":"admin123"}' 2>/dev/null)
    
    if echo "$response" | grep -q '"detail":'; then
        # Login failed (user doesn't exist or wrong password)
        print_info "Creating initial admin account..."
        
        # Create admin user via registration API
        local register_response=$(curl -s -X POST http://localhost:8000/api/v1/auth/register \  
          -H 'Content-Type: application/json' \  
          -d '{"email":"admin@appt.com","username":"Administrator","password":"admin123", "is_active":true}' 2>/dev/null)
        
        if echo "$register_response" | grep -q '"detail":'; then
            # User might already exist (duplicate email), try to get token anyway
            print_warning "User may already exist. Verifying..."
        else
            print_success "Admin user created successfully!"
        fi
    fi
    
    # Run the admin initialization script via database connection
    print_info "Checking and initializing admin user in database..."
    
    docker exec appt-backend python /app/scripts/init_admin_user.py 2>&1 || {
        echo "⚠️  Admin init script failed - manual setup may be needed"
        return 0  # Don't fail the whole startup
    }
}

cmd_stop() {
    print_header "Stopping Appt Services"
    
    cd "$PROJECT_DIR"
    
    print_info "Stopping all services..."
    run_compose down
    
    if [ $? -eq 0 ]; then
        print_success "All services stopped successfully!"
    else
        print_error "Failed to stop some services."
        exit 1
    fi
}

cmd_restart() {
    print_header "Restarting Appt Services"
    
    cd "$PROJECT_DIR"
    
    print_info "Stopping existing services..."
    run_compose down
    
    print_info "Building latest code and restarting..."
    run_compose up -d --build
    
    if [ $? -eq 0 ]; then
        print_success "All services restarted successfully!"
        
        # Wait for services to be healthy
        print_info "Waiting for services to become healthy..."
        sleep 15
        
        cmd_status
    else
        print_error "Failed to restart services."
        exit 1
    fi
}

cmd_status() {
    print_header "Service Status"
    
    cd "$PROJECT_DIR"
    
    echo ""
    printf "%-20s %-25s %-30s\n" "SERVICE" "STATUS" "PORTS"
    printf "%-20s %-25s %-30s\n" "-------" "------" "-----"
    
    for service in $SERVICES; do
        status=$(docker inspect -f '{{.State.Status}}' "$service" 2>/dev/null || echo "Not Found")
        health=$(docker inspect -f '{{range .State.Health}}{{.Status}}{{end}}' "$service" 2>/dev/null || echo "")
        ports=$(docker port "$service" 2>/dev/null | head -1 | cut -d: -f2-3 || echo "N/A")
        
        if [ "$status" = "Not Found" ]; then
            printf "%-20s %-25s %-30s\n" "$service" "${RED}$status${NC}" "-"
        elif [ "$status" = "running" ] && [ -n "$health" ] && [ "$health" != "unhealthy" ]; then
            printf "%-20s %-25s %-30s\n" "$service" "${GREEN}$status ($health)${NC}" "$ports"
        elif [ "$status" = "running" ]; then
            if [ -n "$health" ]; then
                printf "%-20s %-25s %-30s\n" "$service" "${YELLOW}$status ($health)${NC}" "$ports"
            else
                printf "%-20s %-25s %-30s\n" "$service" "${GREEN}$status${NC}" "$ports"
            fi
        else
            printf "%-20s %-25s %-30s\n" "$service" "${RED}$status${NC}" "-"
        fi
    done
    
    echo ""
    
    # Check if services are accessible
    print_info "Checking service accessibility..."
    
    # Frontend check
    if curl -s http://localhost:8080 > /dev/null 2>&1; then
        print_success "Frontend (port 8080) is responding"
    else
        print_warning "Frontend (port 8080) may not be ready yet"
    fi
    
    # Backend health check
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Backend API (port 8000) is healthy"
    else
        print_warning "Backend API (port 8000) may not be ready yet"
    fi
    
    echo ""
}

cmd_logs() {
    print_header "Service Logs"
    
    cd "$PROJECT_DIR"
    
    # Check if user specified a service
    if [ -n "$1" ]; then
        print_info "Showing logs for: $1"
        run_compose logs --tail=50 "$1"
    else
        print_info "Showing last 50 lines of all services (use Ctrl+C to stop)"
        echo ""
        echo -e "${YELLOW}Tip:${NC} Run './manage.sh logs <service-name>' for a specific service"
        echo -e "${YELLOW}Services:${NC} $SERVICES"
        echo ""
        
        # Follow mode by default if no arguments
        run_compose logs --tail=50 -f "$@"
    fi
}

cmd_clean() {
    print_header "Clean Docker Artifacts"
    
    cd "$PROJECT_DIR"
    
    print_warning "This will remove:"
    echo "  • All stopped containers"
    echo "  • All volumes (⚠️ THIS WILL DELETE DATABASE DATA!)"
    echo "  • All networks created by docker-compose"
    echo ""
    
    read -p "Are you sure? Type 'yes' to continue: " confirm
    
    if [ "$confirm" = "yes" ]; then
        print_info "Cleaning up..."
        
        # Stop services first
        run_compose down -v --remove-orphans
        
        if [ $? -eq 0 ]; then
            print_success "Cleanup completed successfully!"
            echo ""
            print_warning "⚠️ Database has been deleted. Run './manage.sh start' to rebuild with fresh data."
        else
            print_error "Cleanup failed or was interrupted."
            exit 1
        fi
    else
        print_info "Cleanup cancelled."
    fi
}

cmd_shell() {
    print_header "Service Shell Access"
    
    echo ""
    printf "%-20s %-40s\n" "SERVICE" "COMMAND"
    printf "%-20s %-40s\n" "-------" "-------"
    printf "%-20s %-40s\n" "appt-db" "docker exec -it appt-db psql -U appt -d appt_db"
    printf "%-20s %-40s\n" "appt-backend" "docker exec -it appt-backend bash"
    printf "%-20s %-40s\n" "appt-frontend" "docker exec -it appt-frontend sh"
    echo ""
    
    read -p "Enter service name (or 'all' for all services): " target
    
    cd "$PROJECT_DIR"
    
    if [ "$target" = "all" ]; then
        print_warning "Opening separate terminals for each service is recommended."
        echo ""
        echo "Run these commands in separate terminal windows:"
        echo -e "  ${GREEN}docker exec -it appt-db psql -U appt -d appt_db${NC}"
        echo -e "  ${GREEN}docker exec -it appt-backend bash${NC}"
        echo -e "  ${GREEN}docker exec -it appt-frontend sh${NC}"
    else
        case $target in
            appt-db)
                docker exec -it appt-db psql -U appt -d appt_db
                ;;
            appt-backend)
                docker exec -it appt-backend bash
                ;;
            appt-frontend)
                docker exec -it appt-frontend sh
                ;;
            *)
                print_error "Unknown service: $target"
                echo "Available services: $SERVICES"
                exit 1
                ;;
        esac
    fi
}

cmd_help() {
    cat << 'EOF'
=============================================================================
Appt Yoga Booking System - Docker Service Manager (Production Ready)
=============================================================================

USAGE:
  ./manage.sh [command] [options]

COMMANDS:
  start       **一键启动**所有服务（生产环境推荐）
              • Builds latest code from git repository
              • Starts database, backend API, and frontend services
              • Waits for health checks to pass (automatic)
              • Initializes admin user if not exists (admin@appt.com / admin123)

  stop        优雅停止所有服务
              • Preserves database volumes (data not lost)
              - Removes containers but keeps Docker images

  restart     重启所有服务（自动重新构建镜像）
              • Useful after code changes or configuration updates
              • Rebuilds Docker images from latest git repository

  status      查看服务运行状态和健康检查
              • Displays container state (running/stopped) and health status
              • Checks if ports are accessible (8080, 8000)
              • Shows service URLs and access information

  logs        查看服务日志（实时跟踪）
              • ./manage.sh logs          → 所有服务的最近 50 行日志（实时跟踪模式）
              • ./manage.sh logs backend  → 仅查看特定服务（backend/db/frontend）
              • Use Ctrl+C to stop following

  clean       清理所有容器、卷和网络（⚠️ **删除数据库数据**！）
              • Removes ALL stopped containers, volumes (包括 PostgreSQL 数据!), and networks
              ⚠️ WARNING: THIS IS IRREVERSIBLE - Database will be completely wiped!
              • Requires explicit confirmation (type 'yes') before proceeding

  shell       进入服务 Shell（调试用）
              • ./manage.sh shell         → 显示可用的服务和命令
              • appt-db    → PostgreSQL SQL shell (psql)
              • appt-backend → Bash shell with FastAPI application code
              • appt-frontend → Alpine shell with Vue.js build artifacts

EXAMPLES:
  # 🎯 Start the application (first time or after changes)
  ./manage.sh start

  # 📊 Check if services are running and healthy
  ./manage.sh status

  # 🔍 View backend API logs in real-time
  ./manage.sh logs backend

  # 🔄 Restart after code changes (auto rebuilds Docker images)
  git pull origin main && ./manage.sh restart

  # 🐛 Access database to check data
  docker exec -it appt-db psql -U appt -d appt_db
  
  # 🧹 Clean everything and start fresh (⚠️ deletes all data!)
  ./manage.sh clean && ./manage.sh start

TROUBLESHOOTING & 常见问题:

🔧 If services fail to start (启动失败):
    1. Check if Docker daemon is running: systemctl status docker
    2. Verify ports are not in use: sudo lsof -i :8080,8000,5432
    3. Check logs for errors: ./manage.sh logs backend
    4. Try clean restart: ./manage.sh clean && ./manage.sh start

🔧 If database is empty after restart (数据库为空):
    - Run the seed script: docker exec appt-backend python scripts/seed_data.py
    
🔧 If admin user cannot login (管理员无法登录):
    - Default credentials: admin@appt.com / admin123
    - Check if init_admin_user.py ran successfully: ./manage.sh logs backend | grep "admin"
    - Reset password manually: docker exec appt-backend python scripts/init_admin_user.py --reset-password

🔧 If admin dashboard shows blank page (管理后台空白):
    - Force refresh browser: Ctrl+Shift+R (clear JS/CSS cache)
    - Check router configuration: frontend/src/router/index.ts should have /admin/* routes
    - Rebuild frontend: ./manage.sh restart

ACCESS URLs (when services are running):
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🌐 Frontend SPA:           http://localhost:8080
  🔧 Backend API:            http://localhost:8000
  📖 Swagger Docs:           http://localhost:8000/docs
  📘 ReDoc (API Reference):  http://localhost:8000/redoc
  
💡 Production Deployment:
   - Replace localhost with your VPS IP/domain
   - Configure SSL certificate (Let's Encrypt recommended)
   - Update ALLOWED_ORIGINS in backend/.env

=============================================================================
EOF
}

# ============================================================================
# Main Entry Point
# ============================================================================

main() {
    # Check prerequisites
    check_docker
    
    cd "$PROJECT_DIR" || exit 1
    check_compose_file
    
    case "${1:-help}" in
        start)
            cmd_start
            ;;
        stop)
            cmd_stop
            ;;
        restart)
            cmd_restart
            ;;
        status)
            cmd_status
            ;;
        logs|log)
            shift  # Remove 'logs' from arguments, pass remaining to func
            cmd_logs "$@"
            ;;
        clean)
            cmd_clean
            ;;
        shell)
            cmd_shell
            ;;
        help|--help|-h)
            cmd_help
            ;;
        *)
            print_error "Unknown command: $1"
            echo ""
            echo "Run './manage.sh help' for usage information."
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
