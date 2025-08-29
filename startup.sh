#!/bin/bash

# LiteTTS Production Startup Script
# This script provides a production-ready startup sequence with proper error handling

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${SCRIPT_DIR}/docs/logs"
PID_FILE="${SCRIPT_DIR}/litetts.pid"
CONFIG_FILE="${SCRIPT_DIR}/config/settings.json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if running as root
check_user() {
    if [[ $EUID -eq 0 ]]; then
        error "Do not run LiteTTS as root for security reasons"
        exit 1
    fi
}

# Check system requirements
check_requirements() {
    log "Checking system requirements..."
    
    # Check Python version
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is required but not installed"
        exit 1
    fi
    
    local python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    log "Python version: $python_version"
    
    # Check virtual environment
    if [[ -z "${VIRTUAL_ENV:-}" ]]; then
        warning "No virtual environment detected. Consider using a virtual environment."
    else
        log "Virtual environment: $VIRTUAL_ENV"
    fi
    
    # Check required files
    if [[ ! -f "$CONFIG_FILE" ]]; then
        error "Configuration file not found: $CONFIG_FILE"
        exit 1
    fi
    
    success "System requirements check passed"
}

# Create necessary directories
setup_directories() {
    log "Setting up directories..."
    
    mkdir -p "$LOG_DIR"
    mkdir -p "${SCRIPT_DIR}/LiteTTS/models"
    mkdir -p "${SCRIPT_DIR}/LiteTTS/voices"
    mkdir -p "${SCRIPT_DIR}/data/cache"
    
    success "Directories created"
}

# Check if already running
check_running() {
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            error "LiteTTS is already running (PID: $pid)"
            exit 1
        else
            warning "Stale PID file found, removing..."
            rm -f "$PID_FILE"
        fi
    fi
}

# Install dependencies
install_dependencies() {
    log "Installing/updating dependencies..."
    
    if [[ -f "requirements.txt" ]]; then
        python3 -m pip install --upgrade pip
        python3 -m pip install -r requirements.txt
        success "Dependencies installed"
    else
        warning "requirements.txt not found, skipping dependency installation"
    fi
}

# Validate configuration
validate_config() {
    log "Validating configuration..."
    
    python3 -c "
import json
import sys
try:
    with open('$CONFIG_FILE', 'r') as f:
        config = json.load(f)
    print('✅ Configuration file is valid JSON')
    
    # Check critical settings
    required_sections = ['server', 'tts', 'voice', 'performance']
    for section in required_sections:
        if section not in config:
            print(f'❌ Missing required section: {section}')
            sys.exit(1)
        else:
            print(f'✅ Found section: {section}')
    
    print('✅ Configuration validation passed')
except Exception as e:
    print(f'❌ Configuration validation failed: {e}')
    sys.exit(1)
"
    
    if [[ $? -ne 0 ]]; then
        error "Configuration validation failed"
        exit 1
    fi
    
    success "Configuration validation passed"
}

# Start LiteTTS
start_litetts() {
    log "Starting LiteTTS..."
    
    # Set environment variables for production
    export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH:-}"
    export LITETTS_ENV="production"
    export LITETTS_LOG_LEVEL="INFO"
    
    # Start the application
    nohup python3 app.py > "${LOG_DIR}/startup.log" 2>&1 &
    local pid=$!
    
    # Save PID
    echo "$pid" > "$PID_FILE"
    
    # Wait a moment and check if it's still running
    sleep 3
    if kill -0 "$pid" 2>/dev/null; then
        success "LiteTTS started successfully (PID: $pid)"
        log "Logs: ${LOG_DIR}/startup.log"
        log "To stop: kill $pid && rm $PID_FILE"
    else
        error "LiteTTS failed to start. Check logs: ${LOG_DIR}/startup.log"
        rm -f "$PID_FILE"
        exit 1
    fi
}

# Health check
health_check() {
    log "Performing health check..."
    
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -s -f http://localhost:8020/health > /dev/null 2>&1; then
            success "Health check passed"
            return 0
        fi
        
        log "Health check attempt $attempt/$max_attempts..."
        sleep 2
        ((attempt++))
    done
    
    error "Health check failed after $max_attempts attempts"
    return 1
}

# Main execution
main() {
    log "🚀 Starting LiteTTS Production Deployment"
    log "========================================"
    
    check_user
    check_requirements
    setup_directories
    check_running
    install_dependencies
    validate_config
    start_litetts
    
    if health_check; then
        success "🎉 LiteTTS is running and healthy!"
        log "Access the API at: http://localhost:8020"
        log "Health endpoint: http://localhost:8020/health"
        log "Metrics endpoint: http://localhost:8020/metrics"
    else
        error "🚨 LiteTTS started but health check failed"
        exit 1
    fi
}

# Handle script arguments
case "${1:-start}" in
    start)
        main
        ;;
    stop)
        if [[ -f "$PID_FILE" ]]; then
            local pid=$(cat "$PID_FILE")
            if kill -0 "$pid" 2>/dev/null; then
                log "Stopping LiteTTS (PID: $pid)..."
                kill "$pid"
                rm -f "$PID_FILE"
                success "LiteTTS stopped"
            else
                warning "LiteTTS is not running"
                rm -f "$PID_FILE"
            fi
        else
            warning "PID file not found, LiteTTS may not be running"
        fi
        ;;
    restart)
        $0 stop
        sleep 2
        $0 start
        ;;
    status)
        if [[ -f "$PID_FILE" ]]; then
            local pid=$(cat "$PID_FILE")
            if kill -0 "$pid" 2>/dev/null; then
                success "LiteTTS is running (PID: $pid)"
            else
                error "LiteTTS is not running (stale PID file)"
            fi
        else
            error "LiteTTS is not running"
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
