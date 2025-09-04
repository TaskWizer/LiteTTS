#!/bin/bash
# LiteTTS Deployment Script
# Supports both CPU-only and GPU-enabled deployments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
MODE="cpu"
BUILD_ONLY=false
FORCE_REBUILD=false
VERBOSE=false

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
LiteTTS Deployment Script

Usage: $0 [OPTIONS]

OPTIONS:
    -m, --mode MODE         Deployment mode: 'cpu' or 'gpu' (default: cpu)
    -b, --build-only        Only build the image, don't start services
    -f, --force-rebuild     Force rebuild of Docker image
    -v, --verbose           Enable verbose output
    -h, --help              Show this help message

EXAMPLES:
    # Deploy with CPU-only optimization
    $0 --mode cpu

    # Deploy with GPU support
    $0 --mode gpu

    # Build GPU image without starting services
    $0 --mode gpu --build-only

    # Force rebuild CPU image
    $0 --mode cpu --force-rebuild

ENVIRONMENT FILES:
    .env.cpu    - CPU-only deployment configuration
    .env.gpu    - GPU-enabled deployment configuration

EOF
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running"
        exit 1
    fi
    
    # Check if docker-compose is available
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    
    # For GPU mode, check if nvidia-docker is available
    if [ "$MODE" = "gpu" ]; then
        if ! command -v nvidia-smi &> /dev/null; then
            print_warning "nvidia-smi not found. GPU support may not work."
        fi
        
        if ! docker run --rm --gpus all nvidia/cuda:11.8-base-ubuntu20.04 nvidia-smi &> /dev/null; then
            print_warning "GPU access test failed. Check nvidia-docker installation."
        fi
    fi
    
    print_success "Prerequisites check completed"
}

# Function to setup environment
setup_environment() {
    print_status "Setting up environment for $MODE mode..."
    
    # Copy appropriate environment file
    if [ "$MODE" = "gpu" ]; then
        if [ ! -f ".env.gpu" ]; then
            print_error ".env.gpu file not found"
            exit 1
        fi
        cp .env.gpu .env
        print_status "Using GPU configuration (.env.gpu)"
    else
        if [ ! -f ".env.cpu" ]; then
            print_error ".env.cpu file not found"
            exit 1
        fi
        cp .env.cpu .env
        print_status "Using CPU configuration (.env.cpu)"
    fi
    
    # Source the environment file
    set -a
    source .env
    set +a
    
    print_success "Environment configured for $MODE mode"
}

# Function to build Docker image
build_image() {
    print_status "Building Docker image for $MODE mode..."
    
    local build_args=""
    if [ "$MODE" = "gpu" ]; then
        build_args="--build-arg ENABLE_GPU=true"
        image_tag="litetts:gpu"
    else
        build_args="--build-arg ENABLE_GPU=false"
        image_tag="litetts:cpu"
    fi
    
    if [ "$FORCE_REBUILD" = true ]; then
        build_args="$build_args --no-cache"
        print_status "Force rebuilding image..."
    fi
    
    if [ "$VERBOSE" = true ]; then
        docker build $build_args -t $image_tag .
    else
        docker build $build_args -t $image_tag . > /dev/null 2>&1
    fi
    
    # Update docker-compose to use the correct image
    sed -i "s/image: litetts:.*/image: $image_tag/" docker-compose.yml
    
    print_success "Docker image built: $image_tag"
}

# Function to start services
start_services() {
    print_status "Starting LiteTTS services..."
    
    # Stop any existing services
    docker-compose down > /dev/null 2>&1 || true
    
    # Start services
    if [ "$VERBOSE" = true ]; then
        docker-compose up -d
    else
        docker-compose up -d > /dev/null 2>&1
    fi
    
    print_success "Services started successfully"
    
    # Show service status
    print_status "Service status:"
    docker-compose ps
    
    # Wait for health check
    print_status "Waiting for LiteTTS to be ready..."
    for i in {1..30}; do
        if curl -s http://localhost:8354/health > /dev/null 2>&1; then
            print_success "LiteTTS is ready!"
            break
        fi
        sleep 2
        if [ $i -eq 30 ]; then
            print_warning "Health check timeout. Check logs with: docker-compose logs litetts"
        fi
    done
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -m|--mode)
            MODE="$2"
            shift 2
            ;;
        -b|--build-only)
            BUILD_ONLY=true
            shift
            ;;
        -f|--force-rebuild)
            FORCE_REBUILD=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate mode
if [ "$MODE" != "cpu" ] && [ "$MODE" != "gpu" ]; then
    print_error "Invalid mode: $MODE. Must be 'cpu' or 'gpu'"
    exit 1
fi

# Main execution
print_status "Starting LiteTTS deployment in $MODE mode..."

check_prerequisites
setup_environment
build_image

if [ "$BUILD_ONLY" = false ]; then
    start_services
    
    print_success "Deployment completed!"
    echo ""
    print_status "Access points:"
    echo "  - LiteTTS API: http://localhost:8354"
    echo "  - API Documentation: http://localhost:8354/docs"
    echo "  - OpenWebUI: http://localhost:3000"
    echo "  - Health Check: http://localhost:8354/health"
    echo ""
    print_status "To view logs: docker-compose logs -f litetts"
    print_status "To stop services: docker-compose down"
else
    print_success "Build completed! Image: litetts:$MODE"
fi
