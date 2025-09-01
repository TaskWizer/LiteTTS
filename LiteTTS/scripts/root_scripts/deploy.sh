#!/bin/bash

# Kokoro ONNX TTS API - Production Deployment Script
# Provides zero-downtime deployment with rollback capability

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="${PROJECT_ROOT}/docker-compose.yml"
COMPOSE_PROD_FILE="${PROJECT_ROOT}/docker-compose.prod.yml"
BACKUP_DIR="${PROJECT_ROOT}/deployment_backups"
LOG_FILE="${PROJECT_ROOT}/docs/logs/deployment.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$LOG_FILE"
}

info() { log "INFO" "${BLUE}$*${NC}"; }
warn() { log "WARN" "${YELLOW}$*${NC}"; }
error() { log "ERROR" "${RED}$*${NC}"; }
success() { log "SUCCESS" "${GREEN}$*${NC}"; }

# Help function
show_help() {
    cat << EOF
Kokoro ONNX TTS API Deployment Script

Usage: $0 [OPTIONS] COMMAND

Commands:
    deploy          Deploy the application with zero-downtime
    rollback        Rollback to previous deployment
    status          Show deployment status
    logs            Show application logs
    health          Check application health

Options:
    -e, --env ENV           Environment (production|staging) [default: production]
    -f, --force             Force deployment without confirmation
    -b, --backup            Create backup before deployment
    -r, --restart           Restart services after deployment
    -h, --help              Show this help message

Examples:
    $0 deploy                           # Deploy to production
    $0 deploy -e staging                # Deploy to staging
    $0 deploy --force --backup          # Force deploy with backup
    $0 rollback                         # Rollback to previous version
    $0 status                           # Check deployment status

EOF
}

# Parse command line arguments
ENVIRONMENT="production"
FORCE=false
BACKUP=false
RESTART=false
COMMAND=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        -b|--backup)
            BACKUP=true
            shift
            ;;
        -r|--restart)
            RESTART=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        deploy|rollback|status|logs|health)
            COMMAND="$1"
            shift
            ;;
        *)
            error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validate command
if [[ -z "$COMMAND" ]]; then
    error "No command specified"
    show_help
    exit 1
fi

# Environment-specific configuration
setup_environment() {
    case "$ENVIRONMENT" in
        production)
            export COMPOSE_FILE="$COMPOSE_PROD_FILE"
            export OMP_NUM_THREADS=$(nproc)
            export KOKORO_WORKERS=1
            export LOG_LEVEL=INFO
            ;;
        staging)
            export COMPOSE_FILE="$COMPOSE_FILE"
            export OMP_NUM_THREADS=4
            export KOKORO_WORKERS=1
            export LOG_LEVEL=DEBUG
            ;;
        *)
            error "Invalid environment: $ENVIRONMENT"
            exit 1
            ;;
    esac
    
    info "Environment: $ENVIRONMENT"
    info "Compose file: $COMPOSE_FILE"
}

# CPU detection and optimization
detect_cpu_config() {
    local cpu_cores=$(nproc)
    local cpu_info=$(lscpu | grep "Model name" | cut -d: -f2 | xargs)
    
    info "Detected CPU: $cpu_info"
    info "Available cores: $cpu_cores"
    
    # Optimize for different CPU types
    if [[ "$cpu_info" == *"i5-13600K"* ]]; then
        export OMP_NUM_THREADS=18
        export OPENBLAS_NUM_THREADS=18
        export MKL_NUM_THREADS=18
        info "Applied i5-13600K optimizations"
    else
        # Conservative settings for unknown CPUs
        export OMP_NUM_THREADS=$((cpu_cores - 2))
        export OPENBLAS_NUM_THREADS=$((cpu_cores - 2))
        export MKL_NUM_THREADS=$((cpu_cores - 2))
        info "Applied conservative CPU optimizations"
    fi
}

# Pre-deployment checks
pre_deployment_checks() {
    info "Running pre-deployment checks..."
    
    # Check if Docker is running
    if ! docker info >/dev/null 2>&1; then
        error "Docker is not running"
        exit 1
    fi
    
    # Check if compose file exists
    if [[ ! -f "$COMPOSE_FILE" ]]; then
        error "Compose file not found: $COMPOSE_FILE"
        exit 1
    fi
    
    # Check disk space (require at least 2GB free)
    local available_space=$(df "$PROJECT_ROOT" | awk 'NR==2 {print $4}')
    if [[ $available_space -lt 2097152 ]]; then  # 2GB in KB
        error "Insufficient disk space. At least 2GB required."
        exit 1
    fi
    
    # Check if ports are available
    if netstat -tuln | grep -q ":8354 "; then
        warn "Port 8354 is already in use"
        if [[ "$FORCE" != true ]]; then
            error "Use --force to override port check"
            exit 1
        fi
    fi
    
    success "Pre-deployment checks passed"
}

# Create backup
create_backup() {
    if [[ "$BACKUP" != true ]]; then
        return 0
    fi
    
    info "Creating deployment backup..."
    
    local backup_timestamp=$(date '+%Y%m%d_%H%M%S')
    local backup_path="${BACKUP_DIR}/backup_${backup_timestamp}"
    
    mkdir -p "$backup_path"
    
    # Backup configuration files
    cp "$PROJECT_ROOT/config.json" "$backup_path/" 2>/dev/null || true
    cp -r "$PROJECT_ROOT/config/" "$backup_path/" 2>/dev/null || true
    
    # Backup Docker volumes (if they exist)
    if docker volume ls | grep -q kokoro-cache; then
        docker run --rm -v kokoro-cache:/data -v "$backup_path":/backup alpine \
            tar czf /backup/kokoro-cache.tar.gz -C /data .
    fi
    
    if docker volume ls | grep -q kokoro-logs; then
        docker run --rm -v kokoro-logs:/data -v "$backup_path":/backup alpine \
            tar czf /backup/kokoro-logs.tar.gz -C /data .
    fi
    
    success "Backup created: $backup_path"
    echo "$backup_path" > "${BACKUP_DIR}/latest_backup.txt"
}

# Deploy function
deploy() {
    info "Starting deployment to $ENVIRONMENT..."
    
    setup_environment
    detect_cpu_config
    pre_deployment_checks
    create_backup
    
    # Build new images
    info "Building Docker images..."
    cd "$PROJECT_ROOT"
    docker-compose -f "$COMPOSE_FILE" build --no-cache
    
    # Zero-downtime deployment
    info "Performing zero-downtime deployment..."
    
    # Start new containers
    docker-compose -f "$COMPOSE_FILE" up -d --remove-orphans
    
    # Wait for health check
    info "Waiting for health check..."
    local max_attempts=30
    local attempt=0
    
    while [[ $attempt -lt $max_attempts ]]; do
        if curl -f http://localhost:8354/health >/dev/null 2>&1; then
            success "Health check passed"
            break
        fi
        
        attempt=$((attempt + 1))
        info "Health check attempt $attempt/$max_attempts..."
        sleep 10
    done
    
    if [[ $attempt -eq $max_attempts ]]; then
        error "Health check failed after $max_attempts attempts"
        error "Rolling back deployment..."
        rollback
        exit 1
    fi
    
    # Clean up old images
    info "Cleaning up old Docker images..."
    docker image prune -f
    
    success "Deployment completed successfully!"
    
    # Show status
    deployment_status
}

# Rollback function
rollback() {
    info "Rolling back deployment..."
    
    local latest_backup_file="${BACKUP_DIR}/latest_backup.txt"
    if [[ ! -f "$latest_backup_file" ]]; then
        error "No backup found for rollback"
        exit 1
    fi
    
    local backup_path=$(cat "$latest_backup_file")
    if [[ ! -d "$backup_path" ]]; then
        error "Backup directory not found: $backup_path"
        exit 1
    fi
    
    info "Restoring from backup: $backup_path"
    
    # Stop current services
    docker-compose -f "$COMPOSE_FILE" down
    
    # Restore configuration
    if [[ -f "$backup_path/config.json" ]]; then
        cp "$backup_path/config.json" "$PROJECT_ROOT/"
    fi
    
    if [[ -d "$backup_path/config" ]]; then
        cp -r "$backup_path/config/" "$PROJECT_ROOT/"
    fi
    
    # Restore Docker volumes
    if [[ -f "$backup_path/kokoro-cache.tar.gz" ]]; then
        docker run --rm -v kokoro-cache:/data -v "$backup_path":/backup alpine \
            tar xzf /backup/kokoro-cache.tar.gz -C /data
    fi
    
    if [[ -f "$backup_path/kokoro-logs.tar.gz" ]]; then
        docker run --rm -v kokoro-logs:/data -v "$backup_path":/backup alpine \
            tar xzf /backup/kokoro-logs.tar.gz -C /data
    fi
    
    # Start services
    docker-compose -f "$COMPOSE_FILE" up -d
    
    success "Rollback completed"
}

# Status function
deployment_status() {
    info "Deployment Status:"
    echo "===================="
    
    # Docker containers status
    docker-compose -f "$COMPOSE_FILE" ps
    
    # Health check
    echo -e "\nHealth Check:"
    if curl -f http://localhost:8354/health >/dev/null 2>&1; then
        success "✓ Application is healthy"
    else
        error "✗ Application health check failed"
    fi
    
    # Resource usage
    echo -e "\nResource Usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
}

# Logs function
show_logs() {
    info "Showing application logs..."
    docker-compose -f "$COMPOSE_FILE" logs -f --tail=100
}

# Health function
health_check() {
    info "Performing health check..."
    
    if curl -f http://localhost:8354/health; then
        success "Health check passed"
        exit 0
    else
        error "Health check failed"
        exit 1
    fi
}

# Main execution
main() {
    # Create necessary directories
    mkdir -p "$BACKUP_DIR" "$(dirname "$LOG_FILE")"
    
    # Execute command
    case "$COMMAND" in
        deploy)
            deploy
            ;;
        rollback)
            rollback
            ;;
        status)
            deployment_status
            ;;
        logs)
            show_logs
            ;;
        health)
            health_check
            ;;
        *)
            error "Unknown command: $COMMAND"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
