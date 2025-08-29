# LiteTTS Production Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying LiteTTS in production environments with optimal performance and security configurations.

## Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/TaskWizer/LiteTTS.git
cd LiteTTS

# Start with Docker Compose
docker-compose up -d

# Check status
docker-compose ps
```

### Manual Deployment

```bash
# Make startup script executable
chmod +x startup.sh

# Start LiteTTS
./startup.sh start

# Check status
./startup.sh status
```

## System Requirements

### Minimum Requirements
- **CPU**: 4 cores, 2.0 GHz
- **RAM**: 2GB available memory
- **Storage**: 5GB free space
- **OS**: Linux (Ubuntu 20.04+, CentOS 8+, Debian 11+)
- **Python**: 3.8 or higher

### Recommended for Production
- **CPU**: 8+ cores, 3.0 GHz (Intel/AMD with AVX2 support)
- **RAM**: 4GB+ available memory
- **Storage**: 10GB+ SSD storage
- **Network**: Stable internet connection for model downloads

## Configuration

### Environment Variables

```bash
# Production settings
export LITETTS_ENV=production
export LITETTS_LOG_LEVEL=INFO
export LITETTS_HOST=0.0.0.0
export LITETTS_PORT=8020

# Performance tuning
export OMP_NUM_THREADS=8
export ONNX_INTER_OP_THREADS=8
export ONNX_INTRA_OP_THREADS=18
```

### Configuration Files

1. **config/settings.json** - Main configuration
2. **config/production.json** - Production overrides
3. **config/override.json** - Local overrides (optional)

### Key Configuration Sections

#### Server Configuration
```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8020,
    "workers": 1,
    "timeout": 300,
    "max_request_size": 10485760
  }
}
```

#### Performance Configuration
```json
{
  "performance": {
    "memory_optimization": true,
    "cpu_optimization": true,
    "dynamic_cpu_allocation": {
      "enabled": true,
      "cpu_target": 80.0
    }
  }
}
```

## Docker Deployment

### Production Docker Compose

```yaml
version: '3.8'
services:
  litetts:
    build: .
    ports:
      - "8020:8020"
    volumes:
      - ./data/voices:/app/LiteTTS/models:rw
      - ./data/cache:/app/data/cache:rw
    environment:
      - LITETTS_ENV=production
      - LITETTS_LOG_LEVEL=INFO
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8020/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
```

### Building the Image

```bash
# Build production image
docker build -t litetts:latest .

# Run with custom configuration
docker run -d \
  --name litetts \
  -p 8020:8020 \
  -v $(pwd)/data:/app/data \
  -e LITETTS_ENV=production \
  litetts:latest
```

## Performance Optimization

### Memory Optimization

Current optimizations reduce memory usage by ~21%:

- Lazy loading of phonetic dictionaries
- Reduced cache sizes
- Minimal preloading strategy

**Memory Targets:**
- Target: <150MB overhead
- Current: ~1348MB (requires further optimization)

### RTF Performance

Current RTF performance meets targets:

- **Overall RTF**: 0.229 (Target: <0.25) ✅
- **Short text**: 0.279 (slightly over target)
- **Medium/Long text**: 0.216-0.217 ✅

### CPU Optimization

- **ONNX Threads**: inter_op=8, intra_op=18
- **Dynamic CPU allocation**: Enabled
- **SIMD Support**: AVX2 detected and utilized
- **CPU Affinity**: Automatic core pinning

## Security

### Production Security Checklist

- [ ] Run as non-root user
- [ ] Use reverse proxy (nginx/Apache)
- [ ] Enable HTTPS/TLS
- [ ] Configure firewall rules
- [ ] Regular security updates
- [ ] Monitor access logs

### Reverse Proxy Configuration (nginx)

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8020;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeout settings
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 300s;
    }
}
```

## Monitoring

### Health Checks

- **Health Endpoint**: `GET /health`
- **Metrics Endpoint**: `GET /metrics`
- **Performance Endpoint**: `GET /performance`

### Log Files

- **Main Log**: `docs/logs/main.log`
- **Performance Log**: `docs/logs/performance.log`
- **Error Log**: `docs/logs/errors.log`
- **Startup Log**: `docs/logs/startup.log`

### Monitoring Commands

```bash
# Check service status
./startup.sh status

# View logs
tail -f docs/logs/main.log

# Health check
curl http://localhost:8020/health

# Performance metrics
curl http://localhost:8020/metrics
```

## Troubleshooting

### Common Issues

1. **High Memory Usage**
   - Check cache configurations
   - Monitor for memory leaks
   - Consider reducing voice preloading

2. **Slow RTF Performance**
   - Verify CPU optimization settings
   - Check ONNX thread configuration
   - Monitor CPU utilization

3. **AudioSegment Errors**
   - Ensure proper import paths
   - Check for circular dependencies
   - Verify model compatibility

### Debug Mode

```bash
# Enable debug logging
export LITETTS_LOG_LEVEL=DEBUG

# Run with verbose output
python3 app.py --debug
```

### Performance Profiling

```bash
# Memory profiling
python3 -c "
import psutil
import os
process = psutil.Process(os.getpid())
print(f'Memory: {process.memory_info().rss / 1024 / 1024:.1f}MB')
"

# RTF testing
python3 -c "
from app import tts_app
tts_app.initialize_model()
# Test synthesis and measure RTF
"
```

## Scaling

### Horizontal Scaling

- Use load balancer (nginx, HAProxy)
- Deploy multiple instances
- Implement session affinity if needed

### Vertical Scaling

- Increase CPU cores and memory
- Optimize ONNX thread settings
- Use faster storage (NVMe SSD)

## Backup and Recovery

### Data to Backup

- Configuration files (`config/`)
- Voice models (`LiteTTS/voices/`)
- Cache data (`data/cache/`)
- Log files (`docs/logs/`)

### Backup Script

```bash
#!/bin/bash
BACKUP_DIR="/backup/litetts-$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

cp -r config/ "$BACKUP_DIR/"
cp -r LiteTTS/voices/ "$BACKUP_DIR/"
cp -r data/ "$BACKUP_DIR/"
cp -r docs/logs/ "$BACKUP_DIR/"

tar -czf "${BACKUP_DIR}.tar.gz" "$BACKUP_DIR"
rm -rf "$BACKUP_DIR"
```

## Support

For issues and support:

1. Check the troubleshooting section
2. Review log files for errors
3. Consult the GitHub repository
4. Submit issues with detailed logs

## Version Information

- **LiteTTS Version**: Latest
- **ONNX Runtime**: Optimized for CPU
- **Python**: 3.8+
- **Docker**: 20.10+
