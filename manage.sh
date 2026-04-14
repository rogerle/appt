#!/bin/bash

# ============================================================================
# Appt Yoga Booking System - Docker Service Manager
# ============================================================================
# Usage: ./manage.sh [command]
# Commands: start, stop, restart, status, logs, clean, shell
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$PROJECT_DIR/docker-compose.yml"

# Service names
SERVICES="appt-db appt-backend appt-frontend"

# ============================================================================
# Helper Functions
# ============================================================================

print_header() {
    echo -e "${CYAN}================================================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}================================================================${NC}"
}

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
    print_header "Starting Appt Services"
    
    cd "$PROJECT_DIR"
    
    print_info "Building and starting all services..."
    run_compose up -d --build
    
    if [ $? -eq 0 ]; then
        print_success "All services started successfully!"
        
        # Wait for services to be healthy
        print_info "Waiting for services to become healthy (this may take ~30 seconds)..."
        sleep 15
        
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
Appt Yoga Booking System - Docker Service Manager
=============================================================================

USAGE:
  ./manage.sh [command] [options]

COMMANDS:
  start       Start all services (build + run in background)
              - Builds latest code from git
              - Starts database, backend API, and frontend
              - Waits for health checks to pass

  stop        Stop all running services gracefully
              - Preserves data in volumes
              - Removes containers but keeps images

  restart     Stop then start all services with rebuild
              - Useful after code changes
              - Rebuilds Docker images before starting

  status      Show current status of all services
              - Displays container state and health
              - Checks if ports are accessible
              - Shows service URLs

  logs        View service logs
              ./manage.sh logs          # All services (follow mode)
              ./manage.sh logs backend  # Specific service only
              Use Ctrl+C to stop following

  clean       Remove all containers, volumes, and networks
              ⚠️ WARNING: This will delete database data!
              Requires confirmation before proceeding

  shell       Access service shells for debugging
              ./manage.sh shell         # Show available services
              - appt-db: PostgreSQL SQL shell
              - appt-backend: Bash shell with FastAPI app
              - appt-frontend: Shell with Vue.js build artifacts

EXAMPLES:
  # Start the application (first time or after changes)
  ./manage.sh start

  # Check if services are running
  ./manage.sh status

  # View backend API logs in real-time
  ./manage.sh logs backend

  # Restart after code changes
  ./manage.sh restart

  # Access database to check data
  docker exec -it appt-db psql -U appt -d appt_db

TROUBLESHOOTING:
  If services fail to start:
    1. Check if Docker daemon is running: systemctl status docker
    2. Verify ports are not in use: sudo lsof -i :8080,8000,5432
    3. Check logs for errors: ./manage.sh logs
    4. Try clean restart: ./manage.sh clean && ./manage.sh start

  If database is empty after restart:
    - Run the seed script: docker exec appt-backend python scripts/seed_data.py

ACCESS URLs (when services are running):
  Frontend SPA:     http://localhost:8080
  Backend API:      http://localhost:8000
  Swagger Docs:     http://localhost:8000/docs
  ReDoc:            http://localhost:8000/redoc

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
