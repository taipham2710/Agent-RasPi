#!/bin/bash

# Script quản lý IoT Agents với Docker Compose

set -e

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

# Function to show usage
show_usage() {
    echo "Usage: $0 {start|stop|restart|status|logs|build|clean}"
    echo ""
    echo "Commands:"
    echo "  start     - Start all agents"
    echo "  stop      - Stop all agents"
    echo "  restart   - Restart all agents"
    echo "  status    - Show status of all agents"
    echo "  logs      - Show logs from all agents"
    echo "  build     - Build agent images"
    echo "  clean     - Remove all containers and images"
    echo ""
    echo "Examples:"
    echo "  $0 start          # Start production agents"
    echo "  $0 start dev      # Start development agents"
    echo "  $0 logs agent-01  # Show logs for specific agent"
}

# Function to start agents
start_agents() {
    local mode=${1:-prod}
    
    if [ "$mode" = "dev" ]; then
        print_status "Starting development agents..."
        docker-compose -f docker-compose.dev.yml up -d
        print_success "Development agents started!"
    else
        print_status "Starting production agents..."
        docker-compose up -d
        print_success "Production agents started!"
    fi
}

# Function to stop agents
stop_agents() {
    local mode=${1:-prod}
    
    if [ "$mode" = "dev" ]; then
        print_status "Stopping development agents..."
        docker-compose -f docker-compose.dev.yml down
        print_success "Development agents stopped!"
    else
        print_status "Stopping production agents..."
        docker-compose down
        print_success "Production agents stopped!"
    fi
}

# Function to restart agents
restart_agents() {
    local mode=${1:-prod}
    
    print_status "Restarting agents..."
    stop_agents "$mode"
    sleep 2
    start_agents "$mode"
    print_success "Agents restarted!"
}

# Function to show status
show_status() {
    local mode=${1:-prod}
    
    if [ "$mode" = "dev" ]; then
        print_status "Development agents status:"
        docker-compose -f docker-compose.dev.yml ps
    else
        print_status "Production agents status:"
        docker-compose ps
    fi
    
    echo ""
    print_status "System resources:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
}

# Function to show logs
show_logs() {
    local service=${1:-""}
    local mode=${2:-prod}
    
    if [ -n "$service" ]; then
        print_status "Showing logs for $service..."
        if [ "$mode" = "dev" ]; then
            docker-compose -f docker-compose.dev.yml logs -f "$service"
        else
            docker-compose logs -f "$service"
        fi
    else
        print_status "Showing logs for all agents..."
        if [ "$mode" = "dev" ]; then
            docker-compose -f docker-compose.dev.yml logs -f
        else
            docker-compose logs -f
        fi
    fi
}

# Function to build images
build_images() {
    print_status "Building agent images..."
    docker-compose build
    print_success "Images built successfully!"
}

# Function to clean up
clean_up() {
    print_warning "This will remove all containers and images. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_status "Cleaning up..."
        docker-compose down -v --rmi all
        docker-compose -f docker-compose.dev.yml down -v --rmi all
        docker system prune -f
        print_success "Cleanup completed!"
    else
        print_status "Cleanup cancelled."
    fi
}

# Main script logic
case "$1" in
    start)
        start_agents "$2"
        ;;
    stop)
        stop_agents "$2"
        ;;
    restart)
        restart_agents "$2"
        ;;
    status)
        show_status "$2"
        ;;
    logs)
        show_logs "$2" "$3"
        ;;
    build)
        build_images
        ;;
    clean)
        clean_up
        ;;
    *)
        show_usage
        exit 1
        ;;
esac 