# Multi-stage build for optimized production image
FROM python:3.12-slim AS builder

# Build arguments
ARG ENVIRONMENT=production

# Install build dependencies and UV
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install UV package manager
RUN pip install --no-cache-dir uv

# Create virtual environment using UV
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy dependency files
COPY requirements.txt pyproject.toml ./

# Install dependencies using UV
RUN uv pip install --no-cache-dir --upgrade pip setuptools wheel
RUN uv pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.12-slim AS production

# Build arguments
ARG ENVIRONMENT=production

# Set production environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    ENVIRONMENT=production \
    MAX_MEMORY_MB=150 \
    TARGET_RTF=0.25 \
    ENABLE_PERFORMANCE_OPTIMIZATION=true

# Security and performance environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    ENVIRONMENT=${ENVIRONMENT}

# Install runtime dependencies (curl for healthcheck, tini for init)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    tini \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set up non-root user
RUN groupadd -r litetts && useradd -r -g litetts -d /app litetts

# Create necessary directories with proper permissions
RUN mkdir -p /app/LiteTTS/cache /app/LiteTTS/models /app/LiteTTS/voices /app/docs/logs \
    && chown -R litetts:litetts /app

# Set working directory
WORKDIR /app

# Copy application files with proper ownership
COPY --chown=litetts:litetts app.py pyproject.toml ./
COPY --chown=litetts:litetts LiteTTS/ ./LiteTTS/
COPY --chown=litetts:litetts config/ ./config/
COPY --chown=litetts:litetts static/ ./static/
COPY --chown=litetts:litetts docs/ ./docs/
COPY --chown=litetts:litetts startup.sh test_imports.py ./

# Install the package in development mode to ensure proper module resolution
RUN pip install --no-cache-dir -e .

# Test imports to catch issues early (run as root before switching user)
RUN python test_imports.py

# Make startup script executable
RUN chmod +x startup.sh

USER litetts

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8354/health || exit 1

EXPOSE 8354

# Use tini for proper signal handling
ENTRYPOINT ["tini", "--"]

# Default command
CMD ["./startup.sh"]