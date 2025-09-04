#!/bin/bash
set -euo pipefail

# LiteTTS Production Deployment Script
# Comprehensive deployment with zero-downtime and rollback capability

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="docker-compose.production.yml"
BACKUP_DIR="./backups"
LOG_FILE="./logs/deployment.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        error "Docker is not running"
        exit 1
    fi
    
    # Check if Docker Compose is available
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check if required files exist
    if [[ ! -f "$PROJECT_ROOT/$COMPOSE_FILE" ]]; then
        error "Production compose file not found: $COMPOSE_FILE"
        exit 1
    fi
    
    if [[ ! -f "$PROJECT_ROOT/Dockerfile" ]]; then
        error "Dockerfile not found"
        exit 1
    fi
    
    success "Prerequisites check passed"
}

# Create necessary directories
setup_directories() {
    log "Setting up directories..."
    
    mkdir -p "$PROJECT_ROOT/data/voices"
    mkdir -p "$PROJECT_ROOT/data/cache"
    mkdir -p "$PROJECT_ROOT/data/letsencrypt"
    mkdir -p "$PROJECT_ROOT/logs"
    mkdir -p "$PROJECT_ROOT/config"
    mkdir -p "$BACKUP_DIR"
    
    # Set proper permissions
    chmod 755 "$PROJECT_ROOT/data"
    chmod 755 "$PROJECT_ROOT/logs"
    
    success "Directories setup completed"
}

# Backup current deployment
backup_current_deployment() {
    log "Creating backup of current deployment..."
    
    local backup_timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_path="$BACKUP_DIR/backup_$backup_timestamp"
    
    mkdir -p "$backup_path"
    
    # Backup configuration
    if [[ -d "$PROJECT_ROOT/config" ]]; then
        cp -r "$PROJECT_ROOT/config" "$backup_path/"
    fi
    
    # Backup data (voices and cache)
    if [[ -d "$PROJECT_ROOT/data" ]]; then
        cp -r "$PROJECT_ROOT/data" "$backup_path/"
    fi
    
    # Export current container state
    if docker ps | grep -q litetts-production; then
        docker commit litetts-production "litetts-backup:$backup_timestamp" || true
    fi
    
    echo "$backup_timestamp" > "$BACKUP_DIR/latest_backup"
    
    success "Backup created: $backup_path"
}

# Build production image
build_production_image() {
    log "Building production image..."
    
    cd "$PROJECT_ROOT"
    
    # Build with production target
    docker build \
        --target production \
        --tag litetts:latest \
        --tag litetts:$(date +%Y%m%d_%H%M%S) \
        --build-arg ENVIRONMENT=production \
        .
    
    success "Production image built successfully"
}

# Run pre-deployment tests
run_pre_deployment_tests() {
    log "Running pre-deployment tests..."
    
    # Test image can start
    local test_container="litetts-test-$(date +%s)"
    
    docker run -d \
        --name "$test_container" \
        --env ENVIRONMENT=test \
        --env MAX_MEMORY_MB=150 \
        --env TARGET_RTF=0.25 \
        litetts:latest
    
    # Wait for container to start
    sleep 10
    
    # Check if container is healthy
    if docker ps | grep -q "$test_container"; then
        success "Pre-deployment test passed"
        docker stop "$test_container" && docker rm "$test_container"
    else
        error "Pre-deployment test failed"
        docker logs "$test_container" || true
        docker rm "$test_container" || true
        exit 1
    fi
}

# Deploy with zero downtime
deploy_zero_downtime() {
    log "Starting zero-downtime deployment..."
    
    cd "$PROJECT_ROOT"
    
    # Check if services are already running
    if docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
        log "Existing services detected, performing rolling update..."
        
        # Scale up new instance
        docker-compose -f "$COMPOSE_FILE" up -d --scale litetts=2 --no-recreate
        
        # Wait for new instance to be healthy
        sleep 30
        
        # Check health of new instances
        local healthy_count=$(docker-compose -f "$COMPOSE_FILE" ps litetts | grep "healthy" | wc -l)
        
        if [[ $healthy_count -ge 1 ]]; then
            log "New instance is healthy, scaling down old instance..."
            docker-compose -f "$COMPOSE_FILE" up -d --scale litetts=1
        else
            error "New instance failed health check, rolling back..."
            docker-compose -f "$COMPOSE_FILE" up -d --scale litetts=1
            exit 1
        fi
    else
        log "No existing services, starting fresh deployment..."
        docker-compose -f "$COMPOSE_FILE" up -d
    fi
    
    success "Zero-downtime deployment completed"
}

# Verify deployment
verify_deployment() {
    log "Verifying deployment..."
    
    # Wait for services to be fully ready
    sleep 30
    
    # Check if all services are running
    local running_services=$(docker-compose -f "$COMPOSE_FILE" ps --services --filter "status=running" | wc -l)
    local total_services=$(docker-compose -f "$COMPOSE_FILE" config --services | wc -l)
    
    if [[ $running_services -eq $total_services ]]; then
        success "All services are running"
    else
        warning "Some services may not be running properly"
    fi
    
    # Test health endpoint
    local max_attempts=10
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -f http://localhost:8355/health &> /dev/null; then
            success "Health check passed"
            break
        else
            log "Health check attempt $attempt/$max_attempts failed, retrying..."
            sleep 10
            ((attempt++))
        fi
    done
    
    if [[ $attempt -gt $max_attempts ]]; then
        error "Health check failed after $max_attempts attempts"
        return 1
    fi
    
    # Test TTS functionality
    log "Testing TTS functionality..."
    local test_response=$(curl -s -X POST http://localhost:8355/v1/audio/speech \
        -H "Content-Type: application/json" \
        -d '{"input": "Hello world", "voice": "af_heart"}' \
        --max-time 30)
    
    if [[ $? -eq 0 ]] && [[ -n "$test_response" ]]; then
        success "TTS functionality test passed"
    else
        warning "TTS functionality test failed"
    fi
    
    # Check performance metrics
    log "Checking performance metrics..."
    local perf_response=$(curl -s http://localhost:8355/performance --max-time 10)
    
    if [[ $? -eq 0 ]] && [[ -n "$perf_response" ]]; then
        success "Performance metrics accessible"
        echo "$perf_response" | jq '.' 2>/dev/null || echo "$perf_response"
    else
        warning "Performance metrics not accessible"
    fi
}

# Rollback function
rollback_deployment() {
    log "Rolling back deployment..."
    
    if [[ -f "$BACKUP_DIR/latest_backup" ]]; then
        local backup_timestamp=$(cat "$BACKUP_DIR/latest_backup")
        local backup_path="$BACKUP_DIR/backup_$backup_timestamp"
        
        if [[ -d "$backup_path" ]]; then
            # Stop current services
            docker-compose -f "$COMPOSE_FILE" down
            
            # Restore backup
            if [[ -d "$backup_path/config" ]]; then
                cp -r "$backup_path/config" "$PROJECT_ROOT/"
            fi
            
            if [[ -d "$backup_path/data" ]]; then
                cp -r "$backup_path/data" "$PROJECT_ROOT/"
            fi
            
            # Restore container if available
            if docker images | grep -q "litetts-backup:$backup_timestamp"; then
                docker tag "litetts-backup:$backup_timestamp" litetts:latest
            fi
            
            # Start services
            docker-compose -f "$COMPOSE_FILE" up -d
            
            success "Rollback completed"
        else
            error "Backup not found: $backup_path"
            exit 1
        fi
    else
        error "No backup information found"
        exit 1
    fi
}

# Cleanup old images and containers
cleanup() {
    log "Cleaning up old images and containers..."
    
    # Remove old images (keep last 3)
    docker images litetts --format "table {{.Tag}}" | grep -E '^[0-9]{8}_[0-9]{6}$' | sort -r | tail -n +4 | xargs -r docker rmi litetts: 2>/dev/null || true
    
    # Remove old backup images (keep last 3)
    docker images litetts-backup --format "table {{.Tag}}" | sort -r | tail -n +4 | xargs -r docker rmi litetts-backup: 2>/dev/null || true
    
    # Clean up old backups (keep last 5)
    find "$BACKUP_DIR" -name "backup_*" -type d | sort -r | tail -n +6 | xargs -r rm -rf
    
    # Docker system cleanup
    docker system prune -f
    
    success "Cleanup completed"
}

# Main deployment function
main() {
    log "Starting LiteTTS production deployment..."
    
    # Parse command line arguments
    local action="${1:-deploy}"
    
    case "$action" in
        "deploy")
            check_prerequisites
            setup_directories
            backup_current_deployment
            build_production_image
            run_pre_deployment_tests
            deploy_zero_downtime
            verify_deployment
            cleanup
            success "Production deployment completed successfully!"
            ;;
        "rollback")
            rollback_deployment
            ;;
        "verify")
            verify_deployment
            ;;
        "cleanup")
            cleanup
            ;;
        *)
            echo "Usage: $0 {deploy|rollback|verify|cleanup}"
            echo "  deploy   - Full production deployment (default)"
            echo "  rollback - Rollback to previous deployment"
            echo "  verify   - Verify current deployment"
            echo "  cleanup  - Clean up old images and backups"
            exit 1
            ;;
    esac
}

# Trap errors and provide rollback option
trap 'error "Deployment failed! Run with \"rollback\" to restore previous version."' ERR

# Run main function
main "$@"
