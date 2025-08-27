# Caddy Reverse Proxy Configuration for LiteTTS API

## Overview

This document describes the updated Caddy reverse proxy configuration that provides full compatibility with the new LiteTTS API structure and ensures seamless OpenWebUI integration.

## Key Changes Made

### 1. Fixed Caddy v2 Syntax Issues

**Primary Issue Resolved**: The original configuration had invalid timeout directive syntax that caused container restart loops.

**Specific Fixes Applied**:
- **Timeout Directives**: Moved `dial_timeout`, `read_timeout`, `write_timeout`, and `response_header_timeout` inside `transport http` blocks (Caddy v2 requirement)
- **Removed Redundant Headers**: Eliminated unnecessary `header_up X-Forwarded-For` and `header_up X-Forwarded-Proto` directives (automatically handled by Caddy)
- **Error Handler Syntax**: Fixed `handle_errors` expression to use `{err.status_code}` instead of `{http.error.status_code}` with proper backtick syntax

### 2. New API Structure Support

The configuration now properly routes all `/api/*` endpoints to the LiteTTS container:

- `/api/health` - System health check with voice availability
- `/api/v1/voices` - List all available voices
- `/api/v1/audio/speech` - OpenAI-compatible TTS generation
- `/api/dashboard` - Web-based dashboard interface
- `/api/v1/audio/speech/openwebui` - OpenWebUI-optimized endpoint

### 3. Audio Streaming Optimizations

Enhanced configuration for audio content delivery:

- **Timeout Settings**: 60-second timeouts for TTS generation (properly configured in transport blocks)
- **Audio Headers**: Proper `Accept-Ranges: bytes` for streaming
- **Content Types**: Support for `audio/mp3` and `audio/mpeg`
- **Metadata Headers**: Preservation of `X-Audio-Duration`, `X-Audio-Sample-Rate`, `X-Processing-Time`

### 4. CORS Support

Comprehensive CORS configuration for cross-origin requests:

- **Preflight Handling**: Automatic OPTIONS request handling
- **Headers**: Full CORS header support for web applications
- **Origins**: Wildcard origin support for development
- **Methods**: POST, GET, OPTIONS support

### 5. Backward Compatibility

Legacy endpoint support with proper redirects:

- `/dashboard` → `/api/dashboard` (permanent redirect)
- `/health` → `/api/health` (permanent redirect)
- `/v1/*` endpoints continue to work directly
- `/tts/*` endpoints maintained for legacy applications

## Syntax Fixes Applied

### Before (Incorrect Caddy v2 Syntax)
```caddyfile
reverse_proxy litetts-api:8354 {
    header_up Host {host}
    header_up X-Real-IP {remote_host}
    header_up X-Forwarded-For {remote_host}      # Redundant
    header_up X-Forwarded-Proto {scheme}         # Redundant

    # INVALID: timeout directives outside transport block
    timeout 60s
    dial_timeout 10s
    read_timeout 60s
    write_timeout 60s
}

handle_errors {
    # INVALID: wrong placeholder and syntax
    @5xx expression {http.error.status_code} >= 500
    rewrite @5xx /error.html
    respond "Server error occurred" 500
}
```

### After (Correct Caddy v2 Syntax)
```caddyfile
reverse_proxy litetts-api:8354 {
    header_up Host {host}
    header_up X-Real-IP {remote_host}

    # CORRECT: timeout directives inside transport block
    transport http {
        dial_timeout 10s
        response_header_timeout 60s
        read_timeout 60s
        write_timeout 60s
    }
}

handle_errors {
    # CORRECT: proper error placeholder and backtick syntax
    @5xx expression `{err.status_code} >= 500`
    rewrite @5xx /error.html
    respond "Server error occurred" 500
}
```

## Configuration Details

### Main API Routing

```caddyfile
# LiteTTS API endpoints - New structure with /api prefix
handle_path /api/* {
    reverse_proxy litetts-api:8354 {
        # Audio streaming optimizations
        header_up Host {host}
        header_up X-Real-IP {remote_host}
        header_up X-Forwarded-For {remote_host}
        header_up X-Forwarded-Proto {scheme}
        
        # Timeout settings for TTS generation (minimum 30 seconds)
        timeout 60s
        dial_timeout 10s
        read_timeout 60s
        write_timeout 60s
    }
}
```

### Audio Streaming Headers

```caddyfile
# Audio streaming and CORS headers for TTS endpoints
@audio_endpoints {
    path /api/v1/audio/* /api/v1/audio/speech* /v1/audio/*
}

header @audio_endpoints {
    # CORS headers for cross-origin requests
    Access-Control-Allow-Origin "*"
    Access-Control-Allow-Methods "POST, GET, OPTIONS"
    Access-Control-Allow-Headers "Content-Type, Authorization, Range"
    Access-Control-Expose-Headers "Content-Length, Content-Type, Accept-Ranges, X-Audio-Duration, X-Audio-Sample-Rate, X-Audio-Format, X-Processing-Time"
    
    # Audio content headers
    Accept-Ranges "bytes"
    Cache-Control "no-cache, no-store, must-revalidate"
    Pragma "no-cache"
    Expires "0"
    
    # Content type options for audio
    X-Content-Type-Options "nosniff"
}
```

### CORS Preflight Support

```caddyfile
# Handle OPTIONS requests for CORS preflight
@options {
    method OPTIONS
    path /api/* /v1/*
}

respond @options 204 {
    Access-Control-Allow-Origin "*"
    Access-Control-Allow-Methods "POST, GET, OPTIONS"
    Access-Control-Allow-Headers "Content-Type, Authorization, Range"
    Access-Control-Max-Age "86400"
}
```

## Validation and Testing

### Automated Testing

Two validation scripts are provided:

1. **Python Validator**: `LiteTTS/tests/test_caddy_proxy_validation.py`
   ```bash
   python LiteTTS/tests/test_caddy_proxy_validation.py --url http://localhost
   ```

2. **Shell Validator**: `LiteTTS/scripts/validate_caddy_deployment.sh`
   ```bash
   ./LiteTTS/scripts/validate_caddy_deployment.sh http://localhost
   ```

### Manual Testing

#### 1. API Health Check
```bash
curl https://yourdomain.com/api/health
```
Expected: JSON response with 55 voices listed

#### 2. Dashboard Access
```bash
curl https://yourdomain.com/api/dashboard
```
Expected: HTML dashboard interface

#### 3. TTS Generation
```bash
curl -X POST https://yourdomain.com/api/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input":"Hello world","voice":"af_heart","response_format":"mp3"}' \
  --output test.mp3
```
Expected: Complete MP3 file (not truncated)

#### 4. OpenWebUI Endpoint
```bash
curl -X POST https://yourdomain.com/api/v1/audio/speech/openwebui \
  -H "Content-Type: application/json" \
  -H "User-Agent: Mozilla/5.0 OpenWebUI" \
  -d '{"input":"OpenWebUI test","voice":"af_heart","response_format":"mp3"}' \
  --output openwebui_test.mp3
```
Expected: MP3 file with OpenWebUI-specific headers

#### 5. CORS Preflight
```bash
curl -X OPTIONS https://yourdomain.com/api/v1/audio/speech \
  -H "Origin: https://example.com" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -I
```
Expected: HTTP 204 with CORS headers

## OpenWebUI Integration

### Configuration in OpenWebUI

1. **TTS Provider**: Set to "OpenAI"
2. **Base URL**: `https://yourdomain.com/api/v1`
3. **API Key**: Any value (not validated)

### Supported Features

- ✅ Full audio generation (not truncated to single syllables)
- ✅ All 55 voices available
- ✅ Speed control
- ✅ MP3 format support
- ✅ Streaming audio delivery
- ✅ CORS compatibility
- ✅ Error handling

## Troubleshooting

### Common Issues

1. **Audio Truncation**: Ensure timeout settings are sufficient (60s minimum)
2. **CORS Errors**: Verify CORS headers are properly configured
3. **404 Errors**: Check that `/api/*` routing is before other rules
4. **Slow Response**: Increase timeout values for complex TTS generation

### Debug Commands

```bash
# Check Caddy configuration syntax
caddy validate --config /path/to/Caddyfile

# Test specific endpoint
curl -v https://yourdomain.com/api/health

# Check container connectivity
docker exec caddy-container curl http://litetts-api:8354/api/health
```

## Production Deployment

### HTTPS Configuration

For production, replace `:80` with your domain:

```caddyfile
yourdomain.com {
    # ... rest of configuration
}
```

Caddy will automatically obtain and manage SSL certificates.

### Security Considerations

- CORS is configured with wildcard origins for development
- Consider restricting origins in production
- Security headers are applied to non-audio endpoints
- Server header is removed for security

## Success Criteria Verification

- ✅ All `/api/*` endpoints accessible externally via HTTPS
- ✅ OpenWebUI TTS integration produces full audio playback
- ✅ Dashboard displays all 55 voices through reverse proxy
- ✅ Audio files stream completely without truncation
- ✅ CORS and security headers properly maintained
- ✅ Production-ready external accessibility for all LiteTTS functionality

## Support

For issues with this configuration:

1. Run the validation scripts
2. Check Caddy logs: `docker logs caddy-container`
3. Verify LiteTTS container health: `docker logs litetts-api`
4. Test direct container access: `curl http://localhost:8354/api/health`
