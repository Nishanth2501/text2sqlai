#!/bin/bash

# Text-to-SQL Assistant Docker Deployment Script

set -e

echo "🐳 Text-to-SQL Assistant Docker Deployment"
echo "=========================================="

# Colors for output
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

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker Desktop first."
    exit 1
fi

print_success "Docker is running"

# Navigate to project root
cd "$(dirname "$0")/.."

# Function to show help
show_help() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build       Build the Docker image"
    echo "  start       Start the application with Docker Compose"
    echo "  stop        Stop the application"
    echo "  restart     Restart the application"
    echo "  logs        Show application logs"
    echo "  status      Show container status"
    echo "  clean       Stop and remove containers, networks, and volumes"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 build    # Build the Docker image"
    echo "  $0 start    # Start the application"
    echo "  $0 logs     # View logs"
}

# Function to build the image
build_image() {
    print_status "Building Docker image..."
    docker build -f docker/Dockerfile -t text2sql-assistant:latest .
    print_success "Docker image built successfully"
}

# Function to start the application
start_app() {
    print_status "Starting Text-to-SQL Assistant..."
    docker-compose -f docker/docker-compose.yml up -d
    print_success "Application started successfully"
    print_status "Access the application at: http://localhost:8501"
}

# Function to stop the application
stop_app() {
    print_status "Stopping Text-to-SQL Assistant..."
    docker-compose -f docker/docker-compose.yml down
    print_success "Application stopped successfully"
}

# Function to restart the application
restart_app() {
    print_status "Restarting Text-to-SQL Assistant..."
    docker-compose -f docker/docker-compose.yml restart
    print_success "Application restarted successfully"
}

# Function to show logs
show_logs() {
    print_status "Showing application logs..."
    docker-compose -f docker/docker-compose.yml logs -f
}

# Function to show status
show_status() {
    print_status "Container status:"
    docker-compose -f docker/docker-compose.yml ps
    echo ""
    print_status "Health check:"
    if curl -f http://localhost:8501/_stcore/health > /dev/null 2>&1; then
        print_success "Application is healthy and responding"
    else
        print_warning "Application may not be fully ready yet"
    fi
}

# Function to clean up
clean_up() {
    print_warning "This will stop and remove all containers, networks, and volumes"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Cleaning up..."
        docker-compose -f docker/docker-compose.yml down -v --remove-orphans
        docker system prune -f
        print_success "Cleanup completed"
    else
        print_status "Cleanup cancelled"
    fi
}

# Main script logic
case "${1:-help}" in
    build)
        build_image
        ;;
    start)
        start_app
        ;;
    stop)
        stop_app
        ;;
    restart)
        restart_app
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    clean)
        clean_up
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
