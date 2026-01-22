#!/bin/bash
set -e

# LiteTTS Background Runner Script
# This script runs the LiteTTS app in the background with proper logging

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$PROJECT_DIR/litetts.pid"
LOG_FILE="$PROJECT_DIR/litetts.log"

# Function to check if the service is already running
is_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        else
            # PID file exists but process is dead
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1
}

# Function to start the service
start_service() {
    if is_running; then
        echo "✅ LiteTTS is already running (PID: $(cat $PID_FILE))"
        return 0
    fi

    echo "🚀 Starting LiteTTS in background..."
    cd "$PROJECT_DIR"
    
    # Set up environment
    export PYTHONPATH="$PROJECT_DIR"
    export PYTHONUNBUFFERED=1
    export PYTHONDONTWRITEBYTECODE=1
    export ENVIRONMENT=production
    export LOG_LEVEL=INFO
    export HOST=0.0.0.0
    export PORT=8354
    
    # Performance optimizations
    export OMP_NUM_THREADS=4
    export ONNX_DISABLE_SPARSE_TENSORS=1
    export ENABLE_PERFORMANCE_OPTIMIZATION=true
    export MAX_MEMORY_MB=4096
    export TARGET_RTF=0.25
    
    # Dynamic CPU allocation
    export DYNAMIC_CPU_ALLOCATION_ENABLED=true
    export CPU_TARGET=75.0
    export AGGRESSIVE_MODE=true
    export THERMAL_PROTECTION=true
    
    # ONNX Runtime settings
    export ORT_DISABLE_ALL_OPTIMIZATION=0
    export ORT_ENABLE_CPU_FP16_OPS=1
    export ORT_GRAPH_OPTIMIZATION_LEVEL=all
    export ORT_EXECUTION_MODE=parallel
    
    # Memory allocation optimizations
    export MALLOC_ARENA_MAX=4
    export MALLOC_MMAP_THRESHOLD_=131072
    export MALLOC_TRIM_THRESHOLD_=131072
    
    # Start the application in background
    nohup "$PROJECT_DIR/.venv/bin/python" "$PROJECT_DIR/app.py" \
        --host "$HOST" \
        --port "$PORT" \
        > "$LOG_FILE" 2>&1 &
    
    local pid=$!
    echo "$pid" > "$PID_FILE"
    
    # Wait a moment and check if it started successfully
    sleep 3
    if ps -p "$pid" > /dev/null 2>&1; then
        echo "✅ LiteTTS started successfully (PID: $pid)"
        echo "🌐 API will be available at: http://localhost:$PORT"
        echo "📊 Dashboard: http://localhost:$PORT/dashboard"
        echo "📚 API Documentation: http://localhost:$PORT/docs"
        echo "📝 Logs: $LOG_FILE"
        return 0
    else
        echo "❌ Failed to start LiteTTS"
        rm -f "$PID_FILE"
        return 1
    fi
}

# Function to stop the service
stop_service() {
    if ! is_running; then
        echo "⚠️ LiteTTS is not running"
        return 0
    fi

    local pid=$(cat "$PID_FILE")
    echo "🛑 Stopping LiteTTS (PID: $pid)..."
    
    # Send SIGTERM first
    kill -TERM "$pid" 2>/dev/null || true
    
    # Wait up to 10 seconds for graceful shutdown
    local count=0
    while ps -p "$pid" > /dev/null 2>&1 && [ $count -lt 10 ]; do
        sleep 1
        count=$((count + 1))
    done
    
    # Force kill if still running
    if ps -p "$pid" > /dev/null 2>&1; then
        echo "⚡ Force killing LiteTTS..."
        kill -KILL "$pid" 2>/dev/null || true
        sleep 1
    fi
    
    # Clean up PID file
    rm -f "$PID_FILE"
    echo "✅ LiteTTS stopped"
}

# Function to restart the service
restart_service() {
    echo "🔄 Restarting LiteTTS..."
    stop_service
    sleep 2
    start_service
}

# Function to show status
show_status() {
    if is_running; then
        local pid=$(cat "$PID_FILE")
        echo "✅ LiteTTS is running (PID: $pid)"
        echo "🌐 API: http://localhost:8354"
        echo "📊 Dashboard: http://localhost:8354/dashboard"
        echo "📚 API Docs: http://localhost:8354/docs"
        echo "📝 Logs: $LOG_FILE"
    else
        echo "❌ LiteTTS is not running"
        return 1
    fi
}

# Function to show logs
show_logs() {
    if [ -f "$LOG_FILE" ]; then
        tail -f "$LOG_FILE"
    else
        echo "📝 No log file found"
    fi
}

# Function to show recent logs
show_recent_logs() {
    if [ -f "$LOG_FILE" ]; then
        tail -n 50 "$LOG_FILE"
    else
        echo "📝 No log file found"
    fi
}

# Main script logic
case "${1:-status}" in
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        restart_service
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    recent)
        show_recent_logs
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|recent}"
        echo ""
        echo "Commands:"
        echo "  start   - Start LiteTTS in background"
        echo "  stop    - Stop LiteTTS"
        echo "  restart - Restart LiteTTS"
        echo "  status  - Show service status"
        echo "  logs    - Follow log output (tail -f)"
        echo "  recent  - Show recent log entries"
        exit 1
        ;;
esac
