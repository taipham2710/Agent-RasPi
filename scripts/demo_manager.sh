#!/bin/bash

# Demo Manager Script for IoT Device Management System
# This script helps manage the 20-agent demo scenario

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker/docker-compose.demo.yml"
BACKEND_URL="http://localhost:8000"
DEMO_SCRIPT="demo/demo_script.py"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Function to check if backend is running
check_backend() {
    print_status "Checking backend connectivity..."
    if curl -s "$BACKEND_URL/health" > /dev/null; then
        print_status "Backend is running and accessible"
        return 0
    else
        print_error "Backend is not accessible at $BACKEND_URL"
        return 1
    fi
}

# Function to start demo agents
start_demo() {
    print_header "Starting IoT Device Management Demo"
    
    if ! check_backend; then
        print_error "Cannot start demo without backend. Please start the backend first."
        exit 1
    fi
    
    print_status "Building and starting 20 demo agents..."
    docker-compose -f $COMPOSE_FILE up -d --build
    
    print_status "Waiting for agents to initialize..."
    sleep 10
    
    print_status "Checking agent status..."
    docker-compose -f $COMPOSE_FILE ps
    
    print_status "Demo started successfully!"
    print_status "You can now:"
    echo "  - View dashboard at: http://localhost:5173"
    echo "  - Check backend API at: $BACKEND_URL/docs"
    echo "  - Monitor logs with: scripts/demo_manager.sh logs"
    echo "  - Run demo scenarios with: scripts/demo_manager.sh run-demo"
}

# Function to stop demo agents
stop_demo() {
    print_header "Stopping IoT Device Management Demo"
    
    print_status "Stopping all demo agents..."
    docker-compose -f $COMPOSE_FILE down
    
    print_status "Cleaning up..."
    docker system prune -f
    
    print_status "Demo stopped successfully!"
}

# Function to show demo status
status_demo() {
    print_header "Demo Status"
    
    print_status "Agent containers:"
    docker-compose -f $COMPOSE_FILE ps
    
    print_status "System resources:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
    
    if check_backend; then
        print_status "Backend API status:"
        curl -s "$BACKEND_URL/health" | jq . 2>/dev/null || curl -s "$BACKEND_URL/health"
    fi
}

# Function to show logs
logs_demo() {
    print_header "Demo Logs"
    
    if [ -z "$1" ]; then
        print_status "Showing logs for all agents..."
        docker-compose -f $COMPOSE_FILE logs -f
    else
        print_status "Showing logs for agent $1..."
        docker-compose -f $COMPOSE_FILE logs -f "agent-demo-$1"
    fi
}

# Function to run demo scenarios
run_demo_scenarios() {
    print_header "Running Demo Scenarios"
    
    if ! check_backend; then
        print_error "Backend is not accessible. Cannot run demo scenarios."
        exit 1
    fi
    
    print_status "Starting demo scenarios..."
    
    if [ -f "$DEMO_SCRIPT" ]; then
        source venv/bin/activate && python demo/demo_script.py

    else
        print_error "Demo script not found at $DEMO_SCRIPT"
        print_status "You can run individual scenarios:"
        echo "  - Scenario 1: Basic IoT Operations"
        echo "  - Scenario 2: Deployment Operations"
        echo "  - Scenario 3: Bulk Operations"
        echo "  - Scenario 4: Failure and Recovery"
        echo "  - Scenario 5: Real-time Monitoring"
    fi
}

# Function to scale demo
scale_demo() {
    local count=$1
    if [ -z "$count" ]; then
        print_error "Please specify number of agents to scale to (1-20)"
        exit 1
    fi
    
    if [ "$count" -lt 1 ] || [ "$count" -gt 20 ]; then
        print_error "Scale count must be between 1 and 20"
        exit 1
    fi
    
    print_header "Scaling Demo to $count Agents"
    
    print_status "Scaling agents to $count..."
    docker-compose -f $COMPOSE_FILE up -d --scale agent-demo-01=$count
    
    print_status "Scaled successfully! Current status:"
    docker-compose -f $COMPOSE_FILE ps
}

# Function to restart specific agent
restart_agent() {
    local agent_id=$1
    if [ -z "$agent_id" ]; then
        print_error "Please specify agent ID (1-20)"
        exit 1
    fi
    
    if [ "$agent_id" -lt 1 ] || [ "$agent_id" -gt 20 ]; then
        print_error "Agent ID must be between 1 and 20"
        exit 1
    fi
    
    print_status "Restarting agent $agent_id..."
    docker-compose -f $COMPOSE_FILE restart "agent-demo-$(printf "%02d" $agent_id)"
    print_status "Agent $agent_id restarted successfully!"
}

# Function to show help
show_help() {
    print_header "IoT Device Management Demo Manager"
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  start           Start the 20-agent demo"
    echo "  stop            Stop all demo agents"
    echo "  restart         Restart all demo agents"
    echo "  status          Show demo status and system resources"
    echo "  logs [AGENT]    Show logs (all agents or specific agent 1-20)"
    echo "  run-demo        Run demo scenarios"
    echo "  scale N         Scale to N agents (1-20)"
    echo "  restart-agent N Restart specific agent N (1-20)"
    echo "  clean           Clean up all containers and images"
    echo "  help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start                    # Start 20-agent demo"
    echo "  $0 logs                     # Show all logs"
    echo "  $0 logs 5                   # Show logs for agent 5"
    echo "  $0 scale 10                 # Scale to 10 agents"
    echo "  $0 restart-agent 3          # Restart agent 3"
    echo ""
    echo "Demo Scenarios:"
    echo "  The demo includes 5 scenarios:"
    echo "  1. Basic IoT Operations"
    echo "  2. Deployment Operations"
    echo "  3. Bulk Operations"
    echo "  4. Failure and Recovery"
    echo "  5. Real-time Monitoring"
}

# Function to clean up
clean_demo() {
    print_header "Cleaning Up Demo Environment"
    
    print_warning "This will remove all containers, images, and volumes!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Stopping all containers..."
        docker-compose -f $COMPOSE_FILE down -v
        
        print_status "Removing all containers..."
        docker container prune -f
        
        print_status "Removing all images..."
        docker image prune -a -f
        
        print_status "Removing all volumes..."
        docker volume prune -f
        
        print_status "Removing all networks..."
        docker network prune -f
        
        print_status "Cleanup completed!"
    else
        print_status "Cleanup cancelled."
    fi
}

# Main script logic
case "${1:-help}" in
    start)
        start_demo
        ;;
    stop)
        stop_demo
        ;;
    restart)
        print_status "Restarting all demo agents..."
        docker-compose -f $COMPOSE_FILE restart
        print_status "All agents restarted!"
        ;;
    status)
        status_demo
        ;;
    logs)
        logs_demo "$2"
        ;;
    run-demo)
        run_demo_scenarios
        ;;
    scale)
        scale_demo "$2"
        ;;
    restart-agent)
        restart_agent "$2"
        ;;
    clean)
        clean_demo
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