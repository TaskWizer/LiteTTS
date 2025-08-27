# 🐳 Docker Deployment Guide - Kokoro ONNX TTS API

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../FEATURES.md) | [Configuration](../CONFIGURATION.md) | [Performance](../PERFORMANCE.md) | [Monitoring](../MONITORING.md) | [Testing](../TESTING.md) | [Troubleshooting](../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../DEPENDENCIES.md) | [Quick Start](QUICK_START_COMMANDS.md) | [Docker Deployment](DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../api/API_REFERENCE.md) | [Development](../development/README.md) | [Voice System](../voices/README.md) | [Watermarking](../WATERMARKING.md)

**Project:** [Changelog](../CHANGELOG.md) | [Roadmap](../ROADMAP.md) | [Contributing](../CONTRIBUTIONS.md) | [Beta Features](../BETA_FEATURES.md)

---

**Unified Docker configuration supporting both development and production environments**

## 🎯 Overview

This guide covers deploying the Kokoro ONNX TTS API using the new unified Docker configuration. The setup supports both development and production environments through a single `docker-compose.yml` file with environment-specific configurations and service profiles.

## 🚀 Quick Docker Start

### **Production Deployment (Recommended)**
```bash
# Clone and deploy with standard Docker Compose
git clone https://github.com/aliasfoxkde/LiteTTS.git && \
cd LiteTTS && \
docker-compose up -d
```

### **Development Deployment**
```bash
# Start development environment with hot reload and dev tools
ENVIRONMENT=development docker-compose up -d
```

### **Verify Deployment**
```bash
# Check container status
docker-compose ps

# Test the API
curl http://localhost:8354/health

# Test TTS functionality
curl -X POST "http://localhost:8354/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello from Docker!", "voice": "af_heart"}' \
  --output test_docker.mp3
```

## 📋 Unified Docker Configuration

### **Environment-Specific Deployments**

The new unified configuration uses environment files and service profiles to support different deployment scenarios:

**Production Environment:**
```bash
# Standard production deployment
docker-compose up -d

# Or with explicit environment
ENVIRONMENT=production docker-compose up -d
```

**Development Environment:**
```bash
# Development with hot reload
ENVIRONMENT=development docker-compose up -d

# Or with explicit environment file (if available)
docker-compose --env-file .env.development up -d
```

**Custom Profiles:**
```bash
# Production with monitoring only
docker-compose --profile production --profile monitoring up -d

# Development with OpenWebUI only
ENVIRONMENT=development docker-compose --profile openwebui up -d
```

## 🏗️ Service Profiles

The unified configuration uses Docker Compose profiles to enable different service combinations:

### **Available Profiles**

| Profile | Services | Use Case |
|---------|----------|----------|
| `development` | Core TTS service with dev settings | Development work |
| `dev-tools` | Redis, Portainer | Development debugging |
| `openwebui` | OpenWebUI integration | Web interface |
| `production` | Core TTS service with prod settings | Production deployment |
| `monitoring` | Prometheus, Grafana | Production monitoring |
| `nginx` | Nginx reverse proxy | Production load balancing |

### **Profile Combinations**

**Development Setup:**
- Profiles: `development,dev-tools,openwebui`
- Services: TTS + Redis + Portainer + OpenWebUI
- Features: Hot reload, debugging tools, web interface

**Production Setup:**
- Profiles: `production,monitoring,nginx`
- Services: TTS + Prometheus + Grafana + Nginx
- Features: Monitoring, reverse proxy, security hardening

**Minimal Production:**
- Profiles: `production`
- Services: TTS only
- Features: Basic production deployment

### **Environment Files**

The configuration uses environment files to set deployment-specific variables:

**`.env.production`** - Production settings:
```bash
ENVIRONMENT=production
LOG_LEVEL=INFO
KOKORO_WORKERS=4
MEM_LIMIT=4g
CPU_LIMIT=4.0
COMPOSE_PROFILES=production,monitoring
```

**`.env.development`** - Development settings:
```bash
ENVIRONMENT=development
LOG_LEVEL=DEBUG
KOKORO_WORKERS=1
MEM_LIMIT=2g
CPU_LIMIT=2.0
COMPOSE_PROFILES=development,dev-tools,openwebui
```

volumes:
  kokoro-cache:
  kokoro-logs:
  openwebui-data:
```

## 🔧 Docker Configuration Fixes

### **Critical Issues Resolved**

**1. Port Conflicts Fixed:**
- ✅ Updated main API port from 8000/8080 to 8354 (consistent across all files)
- ✅ Changed OpenWebUI port from 3000 to 3001 to avoid conflicts
- ✅ Aligned Dockerfile EXPOSE and CMD port configurations

**2. Python Version Updated:**
- ✅ Upgraded from Python 3.11-slim to Python 3.12-slim
- ✅ Ensures compatibility with project requirements (Python 3.12+)

**3. Docker Warnings Resolved:**
- ✅ Fixed FromAsCasing warning: `FROM python:3.12-slim AS builder`
- ✅ Replaced deprecated `deploy.resources.reservations` with `mem_reservation` and `cpus`
- ✅ Updated health check endpoints to use correct paths

**4. Production Optimizations:**
- ✅ Multi-stage build for smaller image size
- ✅ Non-root user for security
- ✅ Proper volume mounts with read-only flags
- ✅ Enhanced logging and monitoring configuration

## 🏗️ Multi-Environment Support

### **Development Configuration (docker-compose.dev.yml)**

Features:
- Hot reload for development
- Debug port exposure (5678)
- Verbose logging
- Development tools (Redis, Portainer)
- Source code mounting

```bash
# Start development environment
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Access development tools
# - API: http://localhost:8354
# - Portainer: http://localhost:9000
# - Redis: localhost:6379
```

### **Production Configuration (docker-compose.prod.yml)**

Features:
- Enhanced security (read-only filesystem, no-new-privileges)
- Monitoring stack (Prometheus, Grafana)
- Nginx reverse proxy with rate limiting
- Production logging and resource limits

```bash
# Start production environment
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Access production services
# - API: http://localhost:80 (via Nginx)
# - Grafana: http://localhost:3000
# - Prometheus: http://localhost:9090
# - OpenWebUI: http://localhost:3001
```

## 🔍 Troubleshooting Docker Issues

### **Common Issues and Solutions**

**1. Port Conflicts:**
```bash
# Check if ports are in use
netstat -tulpn | grep :8354
netstat -tulpn | grep :3001

# Kill processes using the ports
sudo lsof -ti:8354 | xargs kill -9
sudo lsof -ti:3001 | xargs kill -9
```

**2. Docker Build Issues:**
```bash
# Clear Docker cache and rebuild
docker system prune -a
docker-compose build --no-cache

# Check Docker logs
docker-compose logs kokoro-tts
```

**3. Health Check Failures:**
```bash
# Check container health
docker-compose ps
docker inspect kokoro-tts-api | grep Health

# Manual health check
docker exec kokoro-tts-api curl -f http://localhost:8354/health
```

**4. Volume Permission Issues:**
```bash
# Fix volume permissions
sudo chown -R 1000:1000 ./kokoro/models ./kokoro/voices
sudo chmod -R 755 ./kokoro/models ./kokoro/voices
```

## 📊 Monitoring and Logging

### **Container Monitoring**
```bash
# View real-time container stats
docker stats

# Check container logs
docker-compose logs -f kokoro-tts
docker-compose logs -f openwebui

# Monitor resource usage
docker exec kokoro-tts-api top
docker exec kokoro-tts-api df -h
```

### **Production Monitoring Stack**
When using the production configuration, you get:

- **Prometheus**: Metrics collection at http://localhost:9090
- **Grafana**: Visualization dashboard at http://localhost:3000
- **Nginx**: Reverse proxy with rate limiting
- **Structured Logging**: JSON logs with correlation IDs

## 🚀 Performance Optimization

### **Resource Tuning**
```yaml
# Adjust resources based on your system
services:
  kokoro-tts:
    mem_limit: 4g        # Increase for better performance
    mem_reservation: 1g  # Minimum guaranteed memory
    cpus: 4.0           # Number of CPU cores
```

### **Environment Variables for Performance**
```bash
# CPU optimization
OMP_NUM_THREADS=4
ONNX_DISABLE_SPARSE_TENSORS=1

# Application tuning
KOKORO_WORKERS=4
KOKORO_CACHE_SIZE=2000

# GPU support (if available)
USE_CUDA=true
```

## 🔒 Security Best Practices

### **Production Security**
- ✅ Non-root user in containers
- ✅ Read-only filesystem where possible
- ✅ No new privileges security option
- ✅ Network isolation with custom bridge
- ✅ Resource limits to prevent DoS
- ✅ Health checks for reliability

### **Additional Security Measures**
```bash
# Use secrets for sensitive data
echo "your-secret-key" | docker secret create api_key -

# Scan images for vulnerabilities
docker scan kokoro-tts-api

# Update base images regularly
docker-compose pull
docker-compose up -d
```

## 📋 Maintenance Commands

### **Regular Maintenance**
```bash
# Update containers
docker-compose pull
docker-compose up -d

# Clean up unused resources
docker system prune -f

# Backup volumes
docker run --rm -v kokoro-cache:/data -v $(pwd):/backup alpine tar czf /backup/kokoro-cache-backup.tar.gz -C /data .

# Restore volumes
docker run --rm -v kokoro-cache:/data -v $(pwd):/backup alpine tar xzf /backup/kokoro-cache-backup.tar.gz -C /data
```

### **Log Management**
```bash
# Rotate logs
docker-compose exec kokoro-tts logrotate /etc/logrotate.conf

# View structured logs
docker-compose logs kokoro-tts | jq '.'

# Export logs for analysis
docker-compose logs --since 24h kokoro-tts > kokoro-logs-$(date +%Y%m%d).log
```

## ✅ Deployment Checklist

### **Pre-Deployment**
- [ ] Verify Docker and Docker Compose versions
- [ ] Check available system resources (CPU, RAM, disk)
- [ ] Ensure required ports are available
- [ ] Review and customize environment variables
- [ ] Set up monitoring and logging

### **Post-Deployment**
- [ ] Verify all containers are healthy
- [ ] Test API endpoints
- [ ] Check monitoring dashboards
- [ ] Validate log output
- [ ] Perform load testing
- [ ] Set up backup procedures

## 🆘 Support

For Docker-related issues:

1. Check the [Troubleshooting Guide](../TROUBLESHOOTING.md)
2. Review [Configuration Guide](../CONFIGURATION.md)
3. Open an issue on [GitHub](https://github.com/TaskWizer/LiteTTS/issues)

---

**Docker deployment is now production-ready with comprehensive monitoring, security, and scalability features!**
      timeout: 10s
      retries: 3
      start_period: 40s
```

### **2. Production docker-compose.yml**
```yaml
version: '3.8'

services:
  kokoro-tts:
    build: .
    ports:
      - "8354:8354"
    volumes:
      - kokoro_models:/app/kokoro/models
      - kokoro_voices:/app/kokoro/voices
      - kokoro_cache:/app/cache
      - ./config.json:/app/config.json:ro
    environment:
      - KOKORO_HOST=0.0.0.0
      - KOKORO_PORT=8354
      - KOKORO_WORKERS=1
      - KOKORO_LOG_LEVEL=INFO
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8354/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 512M
          cpus: '0.5'

volumes:
  kokoro_models:
  kokoro_voices:
  kokoro_cache:
```

## 🔧 Manual Docker Build

### **Build Image**
```bash
# Build the Docker image
docker build -t kokoro-tts:latest .

# Build with specific tag
docker build -t kokoro-tts:v1.0.0 .
```

### **Run Container**
```bash
# Basic run
docker run -d \
  --name kokoro-tts \
  -p 8080:8080 \
  kokoro-tts:latest

# Production run with volumes
docker run -d \
  --name kokoro-tts \
  -p 8080:8080 \
  -v $(pwd)/kokoro/models:/app/kokoro/models \
  -v $(pwd)/kokoro/voices:/app/kokoro/voices \
  -v $(pwd)/cache:/app/cache \
  -v $(pwd)/config.json:/app/config.json:ro \
  --restart unless-stopped \
  kokoro-tts:latest
```

## 🌐 Network Configuration

### **Expose to Network**
```bash
# Allow external access
docker run -d \
  --name kokoro-tts \
  -p 0.0.0.0:8080:8080 \
  kokoro-tts:latest
```

### **Custom Network**
```bash
# Create custom network
docker network create kokoro-network

# Run with custom network
docker run -d \
  --name kokoro-tts \
  --network kokoro-network \
  -p 8354:8354 \
  kokoro-tts:latest
```

### **Docker Compose with Network**
```yaml
version: '3.8'

networks:
  kokoro-network:
    driver: bridge

services:
  kokoro-tts:
    build: .
    networks:
      - kokoro-network
    ports:
      - "8354:8354"
    # ... other configuration
```

## 💾 Volume Management

### **Persistent Storage**
```bash
# Create named volumes
docker volume create kokoro_models
docker volume create kokoro_voices
docker volume create kokoro_cache

# Use named volumes
docker run -d \
  --name kokoro-tts \
  -v kokoro_models:/app/kokoro/models \
  -v kokoro_voices:/app/kokoro/voices \
  -v kokoro_cache:/app/cache \
  kokoro-tts:latest
```

### **Backup Volumes**
```bash
# Backup models
docker run --rm \
  -v kokoro_models:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/models_backup.tar.gz -C /data .

# Restore models
docker run --rm \
  -v kokoro_models:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/models_backup.tar.gz -C /data
```

## ⚙️ Environment Configuration

### **Environment Variables**
```bash
# Available environment variables
KOKORO_HOST=0.0.0.0          # Server host
KOKORO_PORT=8354             # Server port
KOKORO_WORKERS=1             # Number of workers
KOKORO_LOG_LEVEL=INFO        # Logging level
KOKORO_CACHE_ENABLED=true    # Enable caching
KOKORO_PRELOAD_MODELS=true   # Preload models
KOKORO_MAX_TEXT_LENGTH=3000  # Max text length
```

### **Configuration File**
```bash
# Mount custom config
docker run -d \
  --name kokoro-tts \
  -v $(pwd)/my_config.json:/app/config.json:ro \
  kokoro-tts:latest
```

## 🔄 Multi-Container Setup

### **With OpenWebUI**
```yaml
version: '3.8'

services:
  kokoro-tts:
    build: .
    ports:
      - "8354:8354"
    volumes:
      - kokoro_models:/app/kokoro/models
      - kokoro_voices:/app/kokoro/voices
    restart: unless-stopped

  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    ports:
      - "3000:8080"
    environment:
      - OPENAI_API_BASE_URL=http://kokoro-tts:8354/v1
    depends_on:
      - kokoro-tts
    restart: unless-stopped

volumes:
  kokoro_models:
  kokoro_voices:
```

### **With Reverse Proxy (Nginx)**
```yaml
version: '3.8'

services:
  kokoro-tts:
    build: .
    expose:
      - "8354"
    volumes:
      - kokoro_models:/app/kokoro/models
      - kokoro_voices:/app/kokoro/voices
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - kokoro-tts
    restart: unless-stopped

volumes:
  kokoro_models:
  kokoro_voices:
```

## 📊 Monitoring and Logging

### **Container Logs**
```bash
# View logs
docker logs kokoro-tts

# Follow logs
docker logs -f kokoro-tts

# With Docker Compose
docker-compose logs -f kokoro-tts
```

### **Health Monitoring**
```bash
# Check container health
docker ps

# Inspect health status
docker inspect kokoro-tts | grep Health -A 10
```

### **Resource Monitoring**
```bash
# Monitor resource usage
docker stats kokoro-tts

# Continuous monitoring
watch docker stats kokoro-tts
```

## 🔧 Performance Optimization

### **Resource Limits**
```yaml
services:
  kokoro-tts:
    # ... other config
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 512M
          cpus: '0.5'
```

### **Multi-Worker Setup**
```yaml
services:
  kokoro-tts:
    # ... other config
    environment:
      - KOKORO_WORKERS=4  # Increase for high load
```

### **Caching Optimization**
```yaml
services:
  kokoro-tts:
    # ... other config
    environment:
      - KOKORO_CACHE_ENABLED=true
      - KOKORO_PRELOAD_MODELS=true
    volumes:
      - kokoro_cache:/app/cache  # Persistent cache
```

## 🛡️ Security Configuration

### **Non-Root User**
```dockerfile
# In Dockerfile
RUN adduser -D -s /bin/sh kokoro
USER kokoro
```

### **Read-Only Filesystem**
```bash
docker run -d \
  --name kokoro-tts \
  --read-only \
  --tmpfs /tmp \
  --tmpfs /app/cache \
  -v kokoro_models:/app/kokoro/models:ro \
  kokoro-tts:latest
```

### **Network Security**
```yaml
services:
  kokoro-tts:
    # ... other config
    networks:
      - internal
    # Don't expose ports directly in production
    # Use reverse proxy instead

networks:
  internal:
    internal: true
```

## 🚀 Production Deployment

### **Production Checklist**
- [ ] Use named volumes for persistence
- [ ] Configure resource limits
- [ ] Set up health checks
- [ ] Configure logging
- [ ] Use reverse proxy (Nginx/Traefik)
- [ ] Enable SSL/TLS
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Test disaster recovery

### **Production docker-compose.yml**
```yaml
version: '3.8'

services:
  kokoro-tts:
    build: .
    expose:
      - "8354"
    volumes:
      - kokoro_models:/app/kokoro/models
      - kokoro_voices:/app/kokoro/voices
      - kokoro_cache:/app/cache
      - ./config.json:/app/config.json:ro
    environment:
      - KOKORO_HOST=0.0.0.0
      - KOKORO_PORT=8354
      - KOKORO_WORKERS=2
      - KOKORO_LOG_LEVEL=INFO
      - KOKORO_CACHE_ENABLED=true
      - KOKORO_PRELOAD_MODELS=true
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8354/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 512M
          cpus: '0.5'
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

volumes:
  kokoro_models:
  kokoro_voices:
  kokoro_cache:
```

## 🛠️ Troubleshooting

### **Common Issues**

#### **Container Won't Start**
```bash
# Check logs
docker logs kokoro-tts

# Check Dockerfile
docker build --no-cache -t kokoro-tts .
```

#### **Port Already in Use**
```bash
# Find process using port
lsof -i :8354

# Use different port
docker run -p 8355:8354 kokoro-tts
```

#### **Volume Permission Issues**
```bash
# Fix permissions
sudo chown -R 1000:1000 ./kokoro/models
sudo chown -R 1000:1000 ./kokoro/voices
```

#### **Out of Memory**
```bash
# Increase memory limit
docker run --memory=2g kokoro-tts

# Or in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 2G
```

## 📈 Scaling

### **Horizontal Scaling**
```yaml
version: '3.8'

services:
  kokoro-tts:
    build: .
    deploy:
      replicas: 3
    # ... other config

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx-lb.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - kokoro-tts
```

### **Load Balancer Configuration**
```nginx
upstream kokoro_backend {
    server kokoro-tts_1:8354;
    server kokoro-tts_2:8354;
    server kokoro-tts_3:8354;
}

server {
    listen 80;
    location / {
        proxy_pass http://kokoro_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🔗 Related Resources

- [Quick Start Guide](../QUICK_START_COMMANDS.md)
- [OpenWebUI Integration](OPENWEBUI-INTEGRATION.md)
- [Performance Optimization](../performance.md)
- [API Reference](../FEATURES.md)

---

**🎉 Success!** Your Kokoro ONNX TTS API is now running in a production-ready Docker environment! 🐳🚀
