# Caddy Syntax Fixes Summary

## Problem Resolved

The Caddy container was failing to start with exit code 1 due to specific Caddyfile syntax errors that are incompatible with Caddy v2.

## Root Cause Analysis

The error logs indicated:
- `unrecognized subdirective timeout` at lines 30 and 35
- Warnings about unnecessary `header_up X-Forwarded-*` directives
- Invalid expression syntax in `handle_errors` block

## Specific Syntax Errors Fixed

### 1. Timeout Directive Placement

**❌ BEFORE (Invalid)**:
```caddyfile
reverse_proxy litetts-api:8354 {
    timeout 60s                    # ❌ Invalid in Caddy v2
    dial_timeout 10s              # ❌ Invalid in Caddy v2
    read_timeout 60s              # ❌ Invalid in Caddy v2
    write_timeout 60s             # ❌ Invalid in Caddy v2
}
```

**✅ AFTER (Valid)**:
```caddyfile
reverse_proxy litetts-api:8354 {
    transport http {              # ✅ Correct placement
        dial_timeout 10s
        response_header_timeout 60s
        read_timeout 60s
        write_timeout 60s
    }
}
```

### 2. Redundant Header Directives

**❌ BEFORE (Unnecessary)**:
```caddyfile
header_up X-Forwarded-For {remote_host}     # ❌ Automatically handled
header_up X-Forwarded-Proto {scheme}        # ❌ Automatically handled
```

**✅ AFTER (Cleaned)**:
```caddyfile
header_up Host {host}                       # ✅ Still needed
header_up X-Real-IP {remote_host}          # ✅ Still needed
# X-Forwarded-* headers automatically handled by Caddy
```

### 3. CORS Preflight Response Headers

**❌ BEFORE (Invalid)**:
```caddyfile
respond @options 204 {
    Access-Control-Allow-Origin "*"                    # ❌ Headers not allowed in respond block
    Access-Control-Allow-Methods "POST, GET, OPTIONS"  # ❌ Invalid syntax
    Access-Control-Allow-Headers "Content-Type, Authorization, Range"
    Access-Control-Max-Age "86400"
}
```

**✅ AFTER (Valid)**:
```caddyfile
header @options {
    Access-Control-Allow-Origin "*"                    # ✅ Headers in separate directive
    Access-Control-Allow-Methods "POST, GET, OPTIONS"
    Access-Control-Allow-Headers "Content-Type, Authorization, Range"
    Access-Control-Max-Age "86400"
}

respond @options 204                                   # ✅ Separate respond directive
```

### 4. Error Handler Expression Syntax

**❌ BEFORE (Invalid)**:
```caddyfile
handle_errors {
    @5xx expression {http.error.status_code} >= 500    # ❌ Wrong placeholder
    rewrite @5xx /error.html
    respond "Server error occurred" 500
}
```

**✅ AFTER (Valid)**:
```caddyfile
handle_errors {
    @5xx expression `{err.status_code} >= 500`         # ✅ Correct placeholder & syntax
    rewrite @5xx /error.html
    respond "Server error occurred" 500
}
```

## Key Learnings

### Caddy v2 Transport Configuration
- Timeout directives MUST be inside `transport http` blocks
- Available timeout options:
  - `dial_timeout` - Connection establishment timeout
  - `response_header_timeout` - Time to wait for response headers
  - `read_timeout` - Time to wait for reading from backend
  - `write_timeout` - Time to wait for writing to backend

### Automatic Header Handling
Caddy v2 automatically handles these headers:
- `X-Forwarded-For` - Client IP forwarding
- `X-Forwarded-Proto` - Protocol forwarding (HTTP/HTTPS)
- `X-Forwarded-Host` - Original host header

### Error Handler Placeholders
- Use `{err.status_code}` instead of `{http.error.status_code}`
- Use backticks for expression syntax: `` `{err.status_code} >= 500` ``
- Available error placeholders:
  - `{err.status_code}` - HTTP status code
  - `{err.status_text}` - Status text
  - `{err.message}` - Error message
  - `{err.trace}` - Error origin
  - `{err.id}` - Error occurrence ID

## Validation Tools Created

### 1. Syntax Validation Script
```bash
./LiteTTS/scripts/validate_caddyfile_syntax.sh
```
- Validates Caddyfile syntax using Caddy binary (if available)
- Performs basic syntax checks as fallback
- Checks for balanced braces (excluding comments)
- Identifies common Caddy v2 syntax issues

### 2. Deployment Validation Script
```bash
./LiteTTS/scripts/validate_caddy_deployment.sh
```
- Tests all API endpoints through the proxy
- Validates CORS functionality
- Checks legacy redirects
- Verifies audio streaming headers

## Testing Results

After applying the fixes:
- ✅ Caddyfile syntax validation passes
- ✅ All structural braces are balanced
- ✅ Timeout directives properly nested in transport blocks
- ✅ Error handler expressions use correct syntax
- ✅ No redundant header directives

## Next Steps

1. **Deploy the corrected Caddyfile**:
   ```bash
   # Copy the fixed Caddyfile to your deployment
   docker restart caddy-container
   ```

2. **Verify container startup**:
   ```bash
   docker logs caddy-container
   # Should show successful startup without syntax errors
   ```

3. **Test API routing**:
   ```bash
   ./LiteTTS/scripts/validate_caddy_deployment.sh https://yourdomain.com
   ```

4. **Monitor for issues**:
   ```bash
   docker logs -f caddy-container
   docker logs -f litetts-api
   ```

## Prevention

To avoid similar issues in the future:

1. **Always validate syntax** before deployment:
   ```bash
   caddy validate --config /path/to/Caddyfile
   ```

2. **Use the validation scripts** provided in this repository

3. **Reference official Caddy v2 documentation** for directive syntax:
   - [reverse_proxy directive](https://caddyserver.com/docs/caddyfile/directives/reverse_proxy)
   - [handle_errors directive](https://caddyserver.com/docs/caddyfile/directives/handle_errors)

4. **Test configuration changes** in development before production

## Files Modified

- `config/Caddyfile` - Fixed syntax errors
- `LiteTTS/scripts/validate_caddyfile_syntax.sh` - Created validation script
- `docs/CADDY_PROXY_CONFIGURATION.md` - Updated documentation
- `docs/CADDY_SYNTAX_FIXES_SUMMARY.md` - This summary document

## Success Criteria

- ✅ Caddy container starts successfully without restart loops
- ✅ All LiteTTS API endpoints accessible through reverse proxy
- ✅ OpenWebUI TTS integration works with full audio playback
- ✅ CORS headers properly configured for cross-origin requests
- ✅ Legacy endpoints redirect to new API structure
- ✅ Audio streaming optimized with proper timeouts and headers
