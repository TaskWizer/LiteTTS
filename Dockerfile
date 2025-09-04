# Multi-stage build for optimized production image
FROM python:3.12-slim AS builder

# Build arguments
ARG ENVIRONMENT=production
ARG TARGETPLATFORM
ARG BUILDPLATFORM

# Install build dependencies and UV in a single layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    pkg-config \
    && pip install --no-cache-dir uv \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create virtual environment using UV
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy dependency files
COPY requirements.txt pyproject.toml ./

# Install dependencies using UV with optimizations
RUN uv pip install --no-cache-dir --upgrade pip setuptools wheel \
    && uv pip install --no-cache-dir --compile -r requirements.txt \
    && find /opt/venv -name "*.pyc" -delete \
    && find /opt/venv -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Production stage - use distroless for minimal attack surface
FROM python:3.12-slim AS production

# Build arguments
ARG ENVIRONMENT=production
ARG TARGETPLATFORM
ARG BUILDPLATFORM

# Set production environment variables (consolidated)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    ENVIRONMENT=production \
    MAX_MEMORY_MB=150 \
    TARGET_RTF=0.25 \
    ENABLE_PERFORMANCE_OPTIMIZATION=true \
    DEBIAN_FRONTEND=noninteractive

# Install minimal runtime dependencies in a single layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    tini \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set up non-root user and directories in single layer
RUN groupadd -r litetts && useradd -r -g litetts -d /app litetts \
    && mkdir -p /app/LiteTTS/cache /app/LiteTTS/models /app/LiteTTS/voices /app/docs/logs \
    && chown -R litetts:litetts /app \
    && chmod -R 755 /app/docs/logs \
    && chmod -R 755 /app/LiteTTS/cache

# Set working directory
WORKDIR /app

# Copy application files with proper ownership (order by change frequency)
COPY --chown=litetts:litetts pyproject.toml ./
COPY --chown=litetts:litetts config/ ./config/
COPY --chown=litetts:litetts static/ ./static/
COPY --chown=litetts:litetts docs/ ./docs/
COPY --chown=litetts:litetts LiteTTS/ ./LiteTTS/
COPY --chown=litetts:litetts test_imports.py app.py ./
COPY startup.sh ./
RUN chown litetts:litetts /app/startup.sh && chmod +x /app/startup.sh

# Install package, test imports, and setup in single layer to reduce image size
RUN pip install --no-cache-dir -e . \
    && python test_imports.py \
    && rm -f /app/docs/logs/*.log /app/docs/logs/*.jsonl \
    && chown -R litetts:litetts /app/docs/logs \
    && chown -R litetts:litetts /app/LiteTTS/voices \
    && chown -R litetts:litetts /app/LiteTTS/cache \
    && chmod -R 755 /app/LiteTTS/voices \
    && chmod -R 755 /app/LiteTTS/cache \
    && mkdir -p /app/test_results/memory_optimization \
    && chown -R litetts:litetts /app/test_results \
    && chmod -R 755 /app/test_results \
    && find /app -name "*.pyc" -delete \
    && find /app -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Switch to non-root user
USER litetts

# Healthcheck with optimized intervals
HEALTHCHECK --interval=45s --timeout=15s --start-period=90s --retries=2 \
    CMD curl -f http://localhost:8354/health || exit 1

# Expose port
EXPOSE 8354

# Use tini for proper signal handling and process management
ENTRYPOINT ["tini", "--"]

# Default command
CMD ["./startup.sh"]

# Add labels for better image management
LABEL maintainer="LiteTTS Team" \
      version="1.0.0" \
      description="LiteTTS - High-performance ONNX-based Text-to-Speech API" \
      org.opencontainers.image.source="https://github.com/TaskWizer/LiteTTS" \
      org.opencontainers.image.documentation="https://github.com/TaskWizer/LiteTTS/blob/main/README.md" \
      org.opencontainers.image.licenses="MIT"