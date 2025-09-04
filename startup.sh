#!/bin/bash
set -e

# LiteTTS Docker Container Startup Script
# This script initializes and starts the LiteTTS API server in a Docker container

echo "🚀 Starting LiteTTS API Server..."

# Set default environment variables if not provided
export PYTHONPATH="${PYTHONPATH:-/app}"
export PYTHONUNBUFFERED="${PYTHONUNBUFFERED:-1}"
export PYTHONDONTWRITEBYTECODE="${PYTHONDONTWRITEBYTECODE:-1}"

# Performance optimizations for containerized environment
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-4}"
export ONNX_DISABLE_SPARSE_TENSORS="${ONNX_DISABLE_SPARSE_TENSORS:-1}"

# LiteTTS specific environment variables
export ENVIRONMENT="${ENVIRONMENT:-production}"
export LOG_LEVEL="${LOG_LEVEL:-INFO}"
export CACHE_ENABLED="${CACHE_ENABLED:-true}"

# Server configuration
export HOST="${HOST:-0.0.0.0}"
export PORT="${PORT:-8354}"
export WORKERS="${LITETTS_WORKERS:-4}"

# Create necessary directories
mkdir -p /app/LiteTTS/cache
mkdir -p /app/LiteTTS/models  
mkdir -p /app/LiteTTS/voices
mkdir -p /app/docs/logs

# Ensure proper permissions
chown -R litetts:litetts /app/LiteTTS/cache /app/LiteTTS/models /app/LiteTTS/voices /app/docs/logs 2>/dev/null || true

echo "📋 Environment Configuration:"
echo "  - Python Path: $PYTHONPATH"
echo "  - Environment: $ENVIRONMENT"
echo "  - Log Level: $LOG_LEVEL"
echo "  - Host: $HOST"
echo "  - Port: $PORT"
echo "  - Workers: $WORKERS"
echo "  - Cache Enabled: $CACHE_ENABLED"

# Validate Python installation and imports
echo "🔍 Validating Python environment..."
python -c "import sys; print(f'Python version: {sys.version}')"

# Test critical imports
echo "🧪 Testing critical imports..."
python -c "
try:
    import fastapi
    import uvicorn
    import numpy
    import onnxruntime
    import pydantic
    print('✅ All critical dependencies imported successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

# Run startup validation if available
if [ -f "/app/LiteTTS/startup.py" ]; then
    echo "🔧 Running startup validation..."
    python -c "
import asyncio
import sys
sys.path.insert(0, '/app')
from LiteTTS.startup import initialize_system

async def validate():
    try:
        await initialize_system()
        print('✅ Startup validation completed successfully')
        return True
    except Exception as e:
        print(f'⚠️  Startup validation warning: {e}')
        return True  # Continue anyway for production

if not asyncio.run(validate()):
    exit(1)
"
fi

echo "🌐 Starting LiteTTS API server..."
echo "📊 Dashboard will be available at: http://$HOST:$PORT/dashboard"
echo "📚 API documentation will be available at: http://$HOST:$PORT/docs"

# Start the application
exec python app.py \
    --host "$HOST" \
    --port "$PORT" \
    --workers "$WORKERS" \
    --log-level "${LOG_LEVEL,,}"
