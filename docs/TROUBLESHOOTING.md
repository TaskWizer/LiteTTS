# 🔧 Troubleshooting Guide

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](FEATURES.md) | [Configuration](CONFIGURATION.md) | [Performance](PERFORMANCE.md) | [Monitoring](MONITORING.md) | [Testing](TESTING.md) | [Troubleshooting](TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](DEPENDENCIES.md) | [Quick Start](usage/QUICK_START_COMMANDS.md) | [Docker Deployment](usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](api/API_REFERENCE.md) | [Development](development/README.md) | [Voice System](voices/README.md) | [Watermarking](WATERMARKING.md)

**Project:** [Changelog](CHANGELOG.md) | [Roadmap](ROADMAP.md) | [Contributing](CONTRIBUTIONS.md) | [Beta Features](BETA_FEATURES.md)

---

This guide covers common issues and their solutions for the Kokoro ONNX TTS API.

## Common Configuration Issues

### Port Configuration
**Problem**: Server starts on port 8000 instead of 8080
**Solution**: Ensure `./config/settings.json` exists and contains:
```json
{
  "port": 8080,
  "host": "0.0.0.0"
}
```

### OpenWebUI Connection Issues
**Problem**: OpenWebUI can't connect to TTS API
**Solutions**:
- Use your actual IP address instead of `localhost` (e.g., `http://192.168.1.139:8354/v1`)
- Ensure firewall allows connections on port 8354
- Check that the server is running: `curl http://YOUR_IP:8354/v1/voices`

### Voice Loading Errors
**Problem**: "Voice not found" errors
**Solutions**:
- Check available voices: `curl http://localhost:8354/v1/voices`
- Use full voice names (e.g., `af_heart`) or short names (e.g., `heart`)
- Ensure voice files are downloaded: check `kokoro/voices/` directory

## Performance Issues

### Slow Response Times
**Problem**: TTS generation takes too long
**Solutions**:
- Check RTF metrics in dashboard: `http://localhost:8354/dashboard`
- Clear cache if corrupted: restart server or delete cache files
- Monitor system resources (CPU, memory)
- Use shorter text inputs for testing

### Memory Usage
**Problem**: High memory consumption
**Solutions**:
- Adjust cache settings in `config.json`
- Monitor cache hit rates in dashboard
- Restart server periodically in high-load environments

## Audio Quality Issues

### Silent or Truncated Audio
**Problem**: Generated audio is silent or cut off
**Solutions**:
- Check text preprocessing: avoid special characters that might cause issues
- Test with simple text first: "Hello world"
- Check server logs for preprocessing errors
- Verify audio format compatibility

### Pronunciation Issues
**Problem**: Words pronounced incorrectly
**Solutions**:
- Use SSML for specific pronunciation control
- Check pronunciation dictionary updates
- Report specific issues for improvement
- Use alternative voice if pronunciation varies by voice

## SSML Issues

### Background Noise Not Working
**Problem**: SSML background tags don't add ambient sound
**Solutions**:
- Ensure proper SSML syntax: `<speak><background type="rain" volume="20">text</background></speak>`
- Check supported background types: `nature`, `rain`, `coffee_shop`, `office`, `wind`
- Verify volume levels (1-100)
- Test with simple SSML first

## Development Issues

### Import Errors
**Problem**: Module import errors when running
**Solutions**:
- Ensure virtual environment is activated
- Install dependencies: `pip install -r REQUIREMENTS.txt`
- Check Python version compatibility (3.8+)

### Model Download Issues
**Problem**: Models fail to download automatically
**Solutions**:
- Check internet connection
- Manually download models if needed
- Verify disk space availability
- Check firewall/proxy settings

## Decision Trees

### 🔍 Audio Generation Not Working

```
Is the server running?
├── No → Start server: `uvicorn app:app --port 8354`
└── Yes → Check health: `curl http://localhost:8354/health`
    ├── Error → Check logs, verify models downloaded
    └── OK → Is audio silent or truncated?
        ├── Silent → Test with simple text "Hello world"
        │   ├── Still silent → Check server logs
        │   └── Works → Issue with input text, check SSML
        └── Truncated → Text too long (>510 phonemes)
            ├── Yes → Text chunking should handle automatically
            └── No → Check for special characters causing issues
```

### 🔍 Slow Audio Generation

```
Is RTF > 1.0? (slower than real-time)
├── Yes → Check system resources
│   ├── CPU throttling → Thermal issue, check temps
│   ├── Low memory → Increase RAM or reduce cache
│   └── OK → Enable optimizations
│       ├── Set TARGET_RTF=0.25
│       ├── Enable CACHE_ENABLED=true
│       └── Try shorter text
└── No (RTF < 1.0) → Performance is acceptable
```

### 🔍 Voice Not Found

```
Is the voice name correct?
├── No → Check available: `curl http://localhost:8354/v1/voices`
└── Yes → Is voice downloaded?
    ├── No → Trigger download or set DOWNLOAD_ALL_VOICES=true
    └── Yes → Check voice files in voices/ directory
        ├── Files exist → Permission issue or cache problem
        └── Files missing → Redownload voice
```

### 🔍 Connection Issues

```
Can you ping the server?
├── No → Server not running or firewall blocking
│   ├── Check: `systemctl status litetts`
│   └── Fix: Start server or open port
└── Yes → Can you reach the API?
    ├── No → Wrong port or host
    │   ├── Check: curl localhost:8354/health
    │   └── Fix: Use correct PORT in API URL
    └── Yes → Authentication/Network issue
        ├── Check API key if required
        └── Check CORS settings
```

### 🔍 Memory Leaks

```
Is memory usage growing over time?
├── No → Normal behavior
└── Yes → Cache growing unbounded?
    ├── Yes → Check cache size limits
    │   └── Set MAX_CACHE_SIZE environment variable
    └── No → Memory in ONNX/Model
        ├── Restart server periodically
        └── Check for memory leaks in logs
```

---

## Getting Help

If you encounter issues not covered here:

1. **Check the logs**: Look for error messages in the console output
2. **Test with curl**: Use the API examples to isolate issues
3. **Check the dashboard**: Monitor performance metrics at `/dashboard`
4. **Review configuration**: Ensure `config.json` settings are correct
5. **Create an issue**: Report bugs with detailed reproduction steps

## Additional Resources

- [Quick Start Guide](QUICK_START_COMMANDS.md) - Setup and basic usage
- [API Documentation](FEATURES.md) - Complete endpoint reference
- [Performance Guide](performance.md) - Optimization and benchmarks
- [Configuration Guide](../config.json) - All configuration options
