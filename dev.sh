#!/bin/bash

# Beach Volleyball Simulator - Development Script
# This script helps you quickly start the application in different modes

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Function to check if docker-compose is available
check_docker_compose() {
    if ! command -v docker-compose >/dev/null 2>&1; then
        if ! docker compose version >/dev/null 2>&1; then
            print_error "Docker Compose is not available. Please install Docker Compose."
            exit 1
        else
            DOCKER_COMPOSE="docker compose"
        fi
    else
        DOCKER_COMPOSE="docker-compose"
    fi
    print_success "Docker Compose is available: $DOCKER_COMPOSE"
}

# Function to start the full application
start_full() {
    print_status "Starting Beach Volleyball Simulator (Full Stack)..."
    check_docker
    check_docker_compose
    
    print_status "Building and starting all services..."
    $DOCKER_COMPOSE up --build -d
    
    print_status "Waiting for services to be ready..."
    sleep 5
    
    # Check if services are running
    if $DOCKER_COMPOSE ps | grep -q "Up"; then
        print_success "Services are running!"
        echo ""
        echo "🚀 Beach Volleyball Simulator is ready!"
        echo ""
        echo "📊 Frontend (Analytics Dashboard): http://localhost:3000"
        echo "🔧 Backend API Documentation: http://localhost:8000/docs"
        echo "🔍 API Redoc Documentation: http://localhost:8000/redoc"
        echo "📈 Health Check: http://localhost:8000/health"
        echo ""
        echo "🛑 To stop all services: ./dev.sh stop"
        echo "📋 To view logs: ./dev.sh logs"
        echo "🔄 To restart: ./dev.sh restart"
    else
        print_error "Some services failed to start. Check logs with: $DOCKER_COMPOSE logs"
    fi
}

# Function to start only backend
start_backend() {
    print_status "Starting Backend Only..."
    check_docker
    check_docker_compose
    
    $DOCKER_COMPOSE up --build backend db redis -d
    
    print_success "Backend services started!"
    echo "🔧 API Documentation: http://localhost:8000/docs"
    echo "📈 Health Check: http://localhost:8000/health"
}

# Function to start only frontend (for frontend development)
start_frontend() {
    print_status "Starting Frontend Development Mode..."
    
    cd frontend
    if [ ! -d "node_modules" ]; then
        print_status "Installing frontend dependencies..."
        npm install
    fi
    
    print_status "Starting frontend development server..."
    npm run dev
}

# Function to stop all services
stop_services() {
    print_status "Stopping all services..."
    check_docker_compose
    $DOCKER_COMPOSE down
    print_success "All services stopped!"
}

# Function to restart services
restart_services() {
    print_status "Restarting services..."
    stop_services
    sleep 2
    start_full
}

# Function to view logs
show_logs() {
    check_docker_compose
    if [ -n "$2" ]; then
        print_status "Showing logs for $2..."
        $DOCKER_COMPOSE logs -f "$2"
    else
        print_status "Showing logs for all services..."
        $DOCKER_COMPOSE logs -f
    fi
}

# Function to run tests
run_tests() {
    print_status "Running tests..."
    check_docker_compose
    
    # Backend tests
    print_status "Running backend tests..."
    $DOCKER_COMPOSE exec backend python -m pytest tests/ -v
    
    # Frontend tests (if available)
    if [ -f "frontend/package.json" ] && grep -q "test" frontend/package.json; then
        print_status "Running frontend tests..."
        cd frontend && npm test
    fi
    
    print_success "All tests completed!"
}

# Function to clean up containers and volumes
cleanup() {
    print_warning "This will remove all containers, volumes, and images for this project."
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Cleaning up..."
        check_docker_compose
        $DOCKER_COMPOSE down -v --rmi all --remove-orphans
        print_success "Cleanup completed!"
    else
        print_status "Cleanup cancelled."
    fi
}

# Function to show help
show_help() {
    echo "Beach Volleyball Simulator - Development Helper"
    echo ""
    echo "Usage: ./dev.sh [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start, up       Start the full application (frontend + backend + databases)"
    echo "  backend         Start only backend services (API + databases)"
    echo "  frontend        Start only frontend in development mode"
    echo "  stop, down      Stop all running services"
    echo "  restart         Restart all services"
    echo "  logs [service]  Show logs (optionally for specific service)"
    echo "  test            Run all tests"
    echo "  clean           Clean up all containers and volumes"
    echo "  help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./dev.sh start          # Start everything"
    echo "  ./dev.sh backend        # Backend development"
    echo "  ./dev.sh frontend       # Frontend development"
    echo "  ./dev.sh logs backend   # Show backend logs only"
    echo "  ./dev.sh test           # Run tests"
    echo ""
    echo "Services:"
    echo "  - Frontend: http://localhost:3000 (Analytics Dashboard)"
    echo "  - Backend API: http://localhost:8000/docs (API Documentation)"
    echo "  - Database: PostgreSQL on port 5432"
    echo "  - Redis: Cache on port 6379"
}

# Main script logic
case "${1:-help}" in
    "start"|"up")
        start_full
        ;;
    "backend")
        start_backend
        ;;
    "frontend")
        start_frontend
        ;;
    "stop"|"down")
        stop_services
        ;;
    "restart")
        restart_services
        ;;
    "logs")
        show_logs "$@"
        ;;
    "test")
        run_tests
        ;;
    "clean")
        cleanup
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
