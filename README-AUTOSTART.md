# LiteTTS Automatic Background Service Setup

This guide explains how to run LiteTTS automatically in the background and configure it to start on system boot/login.

## ✅ Current Setup Status

Your LiteTTS service is now configured for automatic background execution and startup!

### 🚀 Service Status
- **Status**: ✅ Running
- **PID**: 116618
- **Port**: 8354
- **API URL**: http://localhost:8354
- **Dashboard**: http://localhost:8354/dashboard
- **API Documentation**: http://localhost:8354/docs

## 🛠️ What Was Set Up

### 1. Background Service Script (`run-background.sh`)
- Manages starting/stopping the LiteTTS app in background
- Provides status monitoring and log management
- Includes all necessary environment variables for optimal performance

### 2. Autostart Configuration
- **Desktop Autostart**: `~/.config/autostart/litetts.desktop`
- **Crontab Entry**: Runs `@reboot` with 30-second delay for reliability

## 📋 Service Control Commands

All commands should be run from the LiteTTS project directory:

```bash
# Start the service
./run-background.sh start

# Stop the service  
./run-background.sh stop

# Restart the service
./run-background.sh restart

# Check current status
./run-background.sh status

# Follow logs in real-time
./run-background.sh logs

# Show recent log entries
./run-background.sh recent
```

## 🌐 Access Points

Once running, you can access LiteTTS at:

- **Main API**: http://localhost:8354
- **Interactive Dashboard**: http://localhost:8354/dashboard  
- **API Documentation**: http://localhost:8354/docs
- **Health Check**: http://localhost:8354/v1/health
- **Voice List**: http://localhost:8354/v1/voices

## 📊 Quick Test

Test the API with curl:

```bash
# Generate speech
curl -X POST "http://localhost:8354/v1/audio/speech" \
     -H "Content-Type: application/json" \
     -d '{"input": "Hello world!", "voice": "af_heart"}' \
     --output hello.mp3

# Check health
curl http://localhost:8354/v1/health
```

## 🔧 Configuration

The service runs with optimized settings:

- **Memory Limit**: 4GB
- **CPU Target**: 75% utilization with dynamic allocation
- **Performance Optimizations**: Enabled
- **Cache**: Intelligent preloading and warming
- **Monitoring**: Performance and health tracking enabled

## 📝 Log Files

- **Main Log**: `/home/mkinney/repos/LiteTTS/litetts.log`
- **PID File**: `/home/mkinney/repos/LiteTTS/litetts.pid`
- **App Logs**: `/home/mkinney/repos/LiteTTS/docs/logs/`

## 🔄 Troubleshooting

### Service won't start
```bash
# Check logs for errors
./run-background.sh recent

# Ensure Python environment is working
./.venv/bin/python --version

# Test app directly (debug mode)
./.venv/bin/python app.py --host 127.0.0.1 --port 8355
```

### Port already in use
```bash
# Check what's using port 8354
netstat -tlnp | grep 8354

# Stop any existing service
./run-background.sh stop
```

### Service crashes on startup
```bash
# Check system resources
free -h
df -h

# Reset and restart
./run-background.sh stop
sleep 5
./run-background.sh start
```

## 🎯 Performance Tuning

The service includes automatic performance optimization:

- **Dynamic CPU Allocation**: Adjusts cores based on utilization
- **Memory Optimization**: Intelligent caching and garbage collection
- **SIMD Optimizations**: Uses AVX2 when available
- **Cache Warming**: Preloads common voices for fast response

## 🚀 Usage Examples

### Python Requests
```python
import requests

response = requests.post(
    "http://localhost:8354/v1/audio/speech",
    json={"input": "Hello world!", "voice": "af_heart"}
)
with open("hello.mp3", "wb") as f:
    f.write(response.content)
```

### JavaScript/Fetch
```javascript
fetch('http://localhost:8354/v1/audio/speech', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({input: 'Hello world!', voice: 'af_heart'})
}).then(response => response.blob())
  .then(blob => {
    const audio = new Audio(URL.createObjectURL(blob));
    audio.play();
  });
```

## 📈 Monitoring

Access the dashboard at http://localhost:8354/dashboard to monitor:
- Performance metrics (RTF, latency, cache hit rate)
- Request statistics
- Resource usage
- Voice performance

---

🎉 **Setup Complete!** Your LiteTTS service is now running automatically in the background and will start on boot/login.
