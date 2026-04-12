#!/bin/bash

# 🧘 Appt Yoga Studio Scheduler - One-Click Start Script
# =====================================================
# Usage: ./start.sh [command]
# Commands: dev, prod, test, status, logs, restart, clean
# Default command: status (check current deployment state)

set -e  # Exit on error

# =============================================================================
# CONFIGURATION & COLORS
# =============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Docker Compose file selection based on environment
DOCKER_COMPOSE_FILE="docker-compose.prod.yml"

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

print_header() {
    echo -e "${CYAN}================================================${NC}"
    echo -e "${CYAN}  🧘 Appt Yoga Studio Scheduler                ${NC}"
    echo -e "${CYAN}================================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ Error: $1${NC}" >&2
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        print_error "$1 is not installed. Please install it first."
        exit 1
    fi
}

# =============================================================================
# DEPLOYMENT COMMANDS
# =============================================================================

start_production() {
    print_header
    
    echo ""
    print_info "Starting Appt in Production Mode..."
    
    # Check for Docker installation
    check_command docker
    check_command docker-compose
    
    echo ""
    print_info "Checking environment configuration..."
    
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating from .env.example..."
        cp .env.example .env
        echo ""
        print_error "Please edit .env file with your configuration and run this script again."
        exit 1
    fi
    
    # Verify required environment variables exist
    if grep -q "<generate-with-secrets-token" ".env"; then
        print_error "SECRET_KEY is not configured. Please generate a secure value using:"
        echo ""
        echo "  python3 -c 'import secrets; print(secrets.token_urlsafe(32))'"
        echo ""
        print_error "Edit .env file and set SECRET_KEY to the generated value."
        exit 1
    fi
    
    if grep -q '"*"'" ".env"; then
        print_warning "⚠️  WARNING: ALLOWED_ORIGINS contains wildcard ['*']!"
        echo ""
        print_error "This is a critical security vulnerability. Please update .env with specific domains."
        exit 1
    fi
    
    if grep -q 'your_secure_password' ".env"; then
        print_warning "⚠️  Database password appears to be default. Please change it!"
    fi
    
    echo ""
    print_info "Building Docker images..."
    
    # Build all services (with cache)
    docker-compose -f "$DOCKER_COMPOSE_FILE" build --no-cache
    
    echo ""
    print_info "Starting containers in detached mode..."
    
    # Start all services
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
    
    echo ""
    print_success "Appt services are now running!"
    
    echo ""
    print_info "Service Status:"
    docker-compose -f "$DOCKER_COMPOSE_FILE" ps
    
    echo ""
    print_info "Access Points:"
    echo "  🌐 Frontend: http://localhost (or https://your-domain.com with SSL)"
    echo "  🔧 API Docs: http://localhost/api/docs (Swagger UI)"
    echo "  ✅ Health Check: http://localhost/health"
    
    echo ""
    print_info "View Logs:"
    echo "  docker-compose -f $DOCKER_COMPOSE_FILE logs -f backend"
    echo "  docker-compose -f $DOCKER_COMPOSE_FILE logs -f frontend"
    
    echo ""
    print_success "Deployment complete! 🎉"
}

start_development() {
    print_header
    
    echo ""
    print_info "Starting Appt in Development Mode..."
    
    # Check Python installation
    check_command python3
    
    # Backend setup
    print_info "Setting up backend development environment..."
    
    if [ ! -d "projects/appt/backend/venv" ]; then
        print_warning "Python virtual environment not found. Creating it now..."
        cd projects/appt/backend
        
        # Check if venv module exists, use ensurepip if needed
        python3 -m ensurepip --upgrade 2>/dev/null || true
        python3 -m venv venv
        
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        
        # Initialize database migrations (if using PostgreSQL)
        if grep -q "postgresql://" .env; then
            print_info "Initializing database migrations..."
            alembic upgrade head
        fi
        
        cd ../..
    else
        print_success "Backend virtual environment already exists"
    fi
    
    # Start backend server
    echo ""
    print_info "Starting FastAPI development server (with hot-reload)..."
    
    cd projects/appt/backend
    
    # Source venv and start uvicorn in background mode with monitoring
    source venv/bin/activate
    
    # Kill any existing uvicorn process on port 8000
    pkill -f "uvicorn app.main:app" 2>/dev/null || true
    
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    
    cd ../..
    
    # Wait for backend to start (check health endpoint)
    print_info "Waiting for backend server to be ready..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo ""
            print_success "Backend API is running at http://localhost:8000"
            break
        fi
        sleep 1
    done
    
    # Frontend setup
    print_info "Setting up frontend development environment..."
    
    cd projects/appt/frontend
    
    if [ ! -d "node_modules" ]; then
        print_warning "Node dependencies not found. Installing now (this may take a few minutes)..."
        npm install
        
        # Install PWA plugin dependencies if needed
        if grep -q "@vitejs/plugin-pwa" package.json; then
            print_info "Installing PWA build tools..."
            npm run build  # Trigger PWA icon generation
        fi
    else
        print_success "Frontend dependencies already installed"
    fi
    
    cd ../..
    
    # Start frontend dev server
    echo ""
    print_info "Starting Vue3 development server..."
    
    cd projects/appt/frontend
    
    # Kill any existing vite process on port 5173
    pkill -f "vite" 2>/dev/null || true
    
    npm run dev &
    FRONTEND_PID=$!
    
    cd ../..
    
    # Wait for frontend to start (check if port is listening)
    print_info "Waiting for frontend server to be ready..."
    for i in {1..30}; do
        if lsof -i :5173 > /dev/null 2>&1 || netstat -an | grep ":5173.*LISTEN" > /dev/null 2>&1; then
            echo ""
            print_success "Frontend is running at http://localhost:5173"
            break
        fi
        sleep 1
    done
    
    # Summary
    echo ""
    print_header
    
    echo ""
    print_success "🎉 Development environment started successfully!"
    
    echo ""
    echo -e "${CYAN}================================================${NC}"
    echo -e "${BLUE}Active Services:${NC}"
    echo "  🔧 Backend API: http://localhost:8000"
    echo "     Swagger UI: http://localhost:8000/docs"
    echo ""
    echo "  🌐 Frontend App: http://localhost:5173"
    echo ""
    echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
    echo -e "${CYAN}================================================${NC}"
    
    # Wait for user interrupt
    wait
    
    echo ""
    print_info "Stopping development servers..."
    
    # Kill processes gracefully
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    
    pkill -f "uvicorn app.main:app" 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true
    
    print_success "All development services stopped."
}

start_test() {
    print_header
    
    echo ""
    print_info "Running comprehensive test suite..."
    
    # Check pytest installation
    check_command python3
    
    cd projects/appt/backend
    
    if [ ! -f "venv" ]; then
        print_warning "Backend virtual environment not found. Creating it now..."
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
    else
        source venv/bin/activate
    fi
    
    # Run all tests with verbose output
    echo ""
    print_info "🧪 Running Unit Tests..."
    
    pytest tests/test_api_v1.py -v --tb=short || {
        print_error "Unit tests failed. Please fix the errors above."
        exit 1
    }
    
    echo ""
    print_success "✅ Unit tests passed!"
    
    echo ""
    print_info "🧪 Running Integration Tests..."
    
    pytest tests/test_integration.py -xvs --tb=short || {
        print_error "Integration tests failed. Please fix the errors above."
        exit 1
    }
    
    print_success "✅ Integration tests passed!"
    
    echo ""
    print_info "🧪 Running Security Tests..."
    
    # Start backend server in background for security tests
    uvicorn app.main:app --host 0.0.0.0 --port 8001 &
    SERVER_PID=$!
    
    sleep 5
    
    ./tests/run_security_tests.sh || {
        print_error "Security tests failed. Please review the output above."
        kill $SERVER_PID 2>/dev/null || true
        exit 1
    }
    
    # Kill test server
    kill $SERVER_PID 2>/dev/null || true
    
    print_success "✅ Security tests passed!"
    
    echo ""
    print_header
    print_success "🎉 All tests completed successfully!"
}

show_status() {
    print_header
    
    echo ""
    print_info "Checking Appt deployment status..."
    
    # Check if Docker Compose is being used
    if docker-compose -f "$DOCKER_COMPOSE_FILE" ps > /dev/null 2>&1; then
        echo ""
        print_success "Docker containers are running:"
        docker-compose -f "$DOCKER_COMPOSE_FILE" ps
        
        echo ""
        print_info "Service Health Checks:"
        
        # Check backend health
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            print_success "Backend API is healthy (http://localhost:8000)"
        else
            print_warning "Backend API is not responding"
        fi
        
        # Check frontend accessibility
        if curl -s http://localhost/ > /dev/null 2>&1 || lsof -i :5173 > /dev/null 2>&1; then
            print_success "Frontend is accessible (http://localhost or http://localhost:5173)"
        else
            print_warning "Frontend is not currently running"
        fi
        
    # Check for development mode processes
    elif lsof -i :8000 > /dev/null 2>&1 && lsof -i :5173 > /dev/null 2>&1; then
        echo ""
        print_success "Development servers are running:"
        
        print_info "Backend (FastAPI):"
        lsof -i :8000
        
        echo ""
        print_info "Frontend (Vite):"
        lsof -i :5173
        
    else
        echo ""
        print_warning "No active Appt services detected."
        
        # Suggest next steps
        echo ""
        print_info "Available commands:"
        echo "  ./start.sh prod     - Start production deployment (Docker)"
        echo "  ./start.sh dev      - Start development servers (Python + Node.js)"
        echo "  ./start.sh test     - Run comprehensive test suite"
    fi
    
    # Show recent logs if available
    echo ""
    print_info "Recent Activity (last 20 lines):"
    
    if docker-compose -f "$DOCKER_COMPOSE_FILE" logs --tail=20 backend > /dev/null 2>&1; then
        docker-compose -f "$DOCKER_COMPOSE_FILE" logs --tail=20 backend | tail -n 20
    fi
}

stop_services() {
    print_header
    
    echo ""
    print_info "Stopping all Appt services..."
    
    if docker-compose -f "$DOCKER_COMPOSE_FILE" ps > /dev/null 2>&1; then
        docker-compose -f "$DOCKER_COMPOSE_FILE" down
        
        # Optional: Remove volumes (comment out to preserve data)
        # docker-compose -f "$DOCKER_COMPOSE_FILE" down -v
        
        print_success "Docker containers stopped successfully."
    else
        # Stop development servers
        pkill -f "uvicorn app.main:app" 2>/dev/null || true
        pkill -f "vite" 2>/dev/null || true
        
        if [ $? -eq 0 ]; then
            print_success "Development servers stopped."
        else
            print_warning "No development servers found to stop."
        fi
    fi
    
    echo ""
    print_info "Run ./start.sh status to verify services are stopped."
}

restart_services() {
    print_header
    
    echo ""
    print_info "Restarting Appt services..."
    
    # Stop existing services first
    docker-compose -f "$DOCKER_COMPOSE_FILE" down 2>/dev/null || true
    
    # Wait a moment for cleanup
    sleep 3
    
    # Start fresh with rebuild (optional --no-cache flag)
    print_info "Starting containers in detached mode..."
    
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Copying from .env.example..."
        cp .env.example .env
        print_error "Please edit .env with your configuration and run again."
        exit 1
    fi
    
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d --build
    
    echo ""
    print_success "Services restarted successfully!"
    
    echo ""
    print_info "Service Status:"
    docker-compose -f "$DOCKER_COMPOSE_FILE" ps
}

clean_artifacts() {
    print_header
    
    echo ""
    print_warning "This will remove Docker images, containers, and volumes."
    echo "⚠️  WARNING: This action cannot be undone!"
    
    read -p "Are you sure? Type 'yes' to continue: " CONFIRM
    
    if [ "$CONFIRM" != "yes" ]; then
        print_info "Operation cancelled."
        exit 0
    fi
    
    echo ""
    print_info "Cleaning up Docker artifacts..."
    
    # Stop and remove containers
    docker-compose -f "$DOCKER_COMPOSE_FILE" down -v || true
    
    # Remove images (optional, can be slow)
    # docker rmi $(docker images -q appt*) 2>/dev/null || true
    
    echo ""
    print_success "Cleanup complete!"
    
    echo ""
    print_info "You can now start fresh with ./start.sh prod"
}

# =============================================================================
# MAIN EXECUTION LOGIC
# =============================================================================

show_help() {
    cat << EOF
🧘 Appt Yoga Studio Scheduler - Start Script

Usage: $0 [command]

Commands:
  dev       Start development environment (Python + Node.js)
  prod      Start production deployment (Docker Compose)
  test      Run comprehensive test suite
  status    Show current service status and health checks
  restart   Restart all services (stop + start fresh)
  stop      Stop all running services
  clean     Remove Docker containers, images, and volumes (⚠️ destructive!)
  help      Show this help message

Examples:
  $0 prod          # Deploy to production with Docker
  $0 dev           # Start local development servers
  $0 test          # Run unit + integration + security tests
  $0 status        # Check what's currently running

Environment Setup Required:
  - Copy .env.example to .env and configure your settings
  - Generate secure SECRET_KEY: python3 -c 'import secrets; print(secrets.token_urlsafe(32))'
  - Update ALLOWED_ORIGINS with your actual domain(s)

For more information, see README.md or DEPLOYMENT.md
EOF
}

# =============================================================================
# SCRIPT ENTRY POINT
# =============================================================================

COMMAND="${1:-status}"

case "$COMMAND" in
    dev|development)
        start_development
        ;;
    
    prod|production)
        start_production
        ;;
    
    test|testing)
        start_test
        ;;
    
    status|check)
        show_status
        ;;
    
    restart)
        restart_services
        ;;
    
    stop|shutdown)
        stop_services
        ;;
    
    clean|purge)
        clean_artifacts
        ;;
    
    help|--help|-h)
        show_help
        ;;
    
    *)
        print_error "Unknown command: $COMMAND"
        echo ""
        show_help
        exit 1
        ;;
esac

exit 0
