#!/bin/bash
# Docker deployment script for Kokoro ONNX TTS API

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
PORT=8080
ENVIRONMENT="production"
BUILD_ARGS=""
COMPOSE_FILE="docker-compose.yml"

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
    cat << EOF
Docker Deployment Script for Kokoro ONNX TTS API

Usage: $0 [OPTIONS] COMMAND

Commands:
    build       Build Docker image
    deploy      Deploy with Docker Compose
    start       Start existing containers
    stop        Stop containers
    restart     Restart containers
    logs        Show container logs
    status      Show container status
    clean       Clean up containers and images
    validate    Validate deployment

Options:
    -p, --port PORT         Set port (default: 8080)
    -e, --env ENV          Set environment (default: production)
    -f, --file FILE        Docker Compose file (default: docker-compose.yml)
    -d, --detach           Run in detached mode
    -h, --help             Show this help

Examples:
    $0 build                    # Build Docker image
    $0 deploy -p 9001          # Deploy on port 9001
    $0 start -d                # Start in detached mode
    $0 logs -f                 # Follow logs
    $0 validate -p 9001        # Validate deployment on port 9001
EOF
}

# Function to check if Docker is available
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running"
        exit 1
    fi
    
    print_success "Docker is available"
}

# Function to check if Docker Compose is available
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    
    print_success "Docker Compose is available"
}

# Function to build Docker image
build_image() {
    print_status "Building Docker image..."
    
    # Build with performance optimizations
    docker build \
        --build-arg ENVIRONMENT="$ENVIRONMENT" \
        --tag kokoro-tts-api:latest \
        --tag kokoro-tts-api:$(date +%Y%m%d-%H%M%S) \
        $BUILD_ARGS \
        .
    
    print_success "Docker image built successfully"
}

# Function to deploy with Docker Compose
deploy_compose() {
    print_status "Deploying with Docker Compose..."
    
    # Set environment variables
    export PORT="$PORT"
    export ENVIRONMENT="$ENVIRONMENT"
    
    # Deploy
    if [[ "$DETACHED" == "true" ]]; then
        docker-compose -f "$COMPOSE_FILE" up -d
    else
        docker-compose -f "$COMPOSE_FILE" up
    fi
    
    print_success "Deployment completed"
}

# Function to start containers
start_containers() {
    print_status "Starting containers..."
    docker-compose -f "$COMPOSE_FILE" start
    print_success "Containers started"
}

# Function to stop containers
stop_containers() {
    print_status "Stopping containers..."
    docker-compose -f "$COMPOSE_FILE" stop
    print_success "Containers stopped"
}

# Function to restart containers
restart_containers() {
    print_status "Restarting containers..."
    docker-compose -f "$COMPOSE_FILE" restart
    print_success "Containers restarted"
}

# Function to show logs
show_logs() {
    if [[ "$FOLLOW_LOGS" == "true" ]]; then
        docker-compose -f "$COMPOSE_FILE" logs -f
    else
        docker-compose -f "$COMPOSE_FILE" logs
    fi
}

# Function to show status
show_status() {
    print_status "Container status:"
    docker-compose -f "$COMPOSE_FILE" ps
    
    print_status "Image information:"
    docker images kokoro-tts-api
}

# Function to clean up
cleanup() {
    print_status "Cleaning up containers and images..."
    
    # Stop and remove containers
    docker-compose -f "$COMPOSE_FILE" down --remove-orphans
    
    # Remove images (ask for confirmation)
    read -p "Remove Docker images? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker rmi kokoro-tts-api:latest || true
        docker image prune -f
        print_success "Images removed"
    fi
    
    print_success "Cleanup completed"
}

# Function to validate deployment
validate_deployment() {
    print_status "Validating deployment..."
    
    # Wait for service to be ready
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -s "http://localhost:$PORT/" > /dev/null 2>&1; then
            print_success "Service is responding"
            break
        fi
        
        print_status "Waiting for service... ($attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done
    
    if [[ $attempt -gt $max_attempts ]]; then
        print_error "Service failed to start within timeout"
        return 1
    fi
    
    # Test endpoints
    local endpoints=(
        "/ (Root)"
        "/v1/health (Health Check)"
        "/v1/voices (Voices List)"
    )
    
    for endpoint_info in "${endpoints[@]}"; do
        local endpoint=$(echo "$endpoint_info" | cut -d' ' -f1)
        local name=$(echo "$endpoint_info" | cut -d' ' -f2-)
        
        if curl -s "http://localhost:$PORT$endpoint" > /dev/null 2>&1; then
            print_success "✅ $name: OK"
        else
            print_error "❌ $name: Failed"
        fi
    done
    
    # Test TTS endpoint
    print_status "Testing TTS endpoint..."
    local tts_response=$(curl -s -w "%{http_code}" -o /tmp/test_audio.mp3 \
        -X POST "http://localhost:$PORT/v1/audio/speech" \
        -H "Content-Type: application/json" \
        -d '{"input": "Hello, Docker deployment test!", "voice": "af_heart", "response_format": "mp3"}')
    
    if [[ "$tts_response" == "200" ]] && [[ -s /tmp/test_audio.mp3 ]]; then
        print_success "✅ TTS Endpoint: OK"
        rm -f /tmp/test_audio.mp3
    else
        print_error "❌ TTS Endpoint: Failed (HTTP $tts_response)"
    fi
    
    print_success "Validation completed"
    print_status "🌐 Service URL: http://localhost:$PORT"
    print_status "📊 Dashboard: http://localhost:$PORT/dashboard"
    print_status "📚 API Docs: http://localhost:$PORT/docs"
}

# Parse command line arguments
DETACHED="false"
FOLLOW_LOGS="false"

while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -e|--env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -f|--file)
            COMPOSE_FILE="$2"
            shift 2
            ;;
        -d|--detach)
            DETACHED="true"
            shift
            ;;
        -f|--follow)
            FOLLOW_LOGS="true"
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        build|deploy|start|stop|restart|logs|status|clean|validate)
            COMMAND="$1"
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Check if command was provided
if [[ -z "$COMMAND" ]]; then
    print_error "No command specified"
    show_usage
    exit 1
fi

# Main execution
print_status "🚀 Kokoro ONNX TTS API Docker Deployment"
print_status "Port: $PORT | Environment: $ENVIRONMENT"
print_status "================================================"

# Check prerequisites
check_docker
if [[ "$COMMAND" != "build" ]]; then
    check_docker_compose
fi

# Execute command
case $COMMAND in
    build)
        build_image
        ;;
    deploy)
        build_image
        deploy_compose
        ;;
    start)
        start_containers
        ;;
    stop)
        stop_containers
        ;;
    restart)
        restart_containers
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    clean)
        cleanup
        ;;
    validate)
        validate_deployment
        ;;
    *)
        print_error "Unknown command: $COMMAND"
        show_usage
        exit 1
        ;;
esac

print_success "Operation completed successfully!"