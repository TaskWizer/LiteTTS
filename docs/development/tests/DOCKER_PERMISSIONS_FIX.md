# Docker Permissions Fix for LiteTTS

## Problem Description

The LiteTTS Docker container was experiencing "Permission denied" errors when trying to download and save model files and voice files. This was caused by a conflict between the container's read-only filesystem design and the volume mount configuration.

## Root Cause

1. **Container Design**: The Dockerfile creates symbolic links:
   - `/app/LiteTTS/models` → `/tmp/litetts/models`
   - `/app/LiteTTS/voices` → `/tmp/litetts/voices`
   - `/app/docs/logs` → `/tmp/litetts/logs`

2. **Volume Mount Conflict**: The original docker-compose.yml mounted host directories directly to `/app/LiteTTS/*` paths, which overwrote the symbolic links and caused permission issues.

## Solution

### 1. Updated Volume Mounts

The docker-compose.yml now mounts host directories to the `/tmp/litetts/*` paths instead:

```yaml
volumes:
  # Mount host directories to /tmp paths to work with symbolic links
  - ./LiteTTS/models:/tmp/litetts/models:rw
  - ./LiteTTS/voices:/tmp/litetts/voices:rw
  - ./docs/logs:/tmp/litetts/logs:rw
  # Optional: Mount cache directory for persistence
  - ./cache:/tmp/litetts/cache:rw
```

### 2. Universal Permission Handling

- Updated Dockerfile to use world-writable permissions (777) on `/tmp/litetts/*` directories
- Enhanced startup.sh to ensure proper permissions regardless of host user
- Removed complex user ID matching - now works with any host user (root, regular user, etc.)

## How to Use

### Simple Deployment (Works Everywhere)

Just use standard docker-compose commands:

```bash
# Stop any existing containers
docker compose down

# Build the container
docker compose build --no-cache litetts

# Start the container
docker compose up -d litetts
```

That's it! The container will automatically:
- Create required directories with proper permissions
- Set up symbolic links for read-only filesystem compatibility
- Handle permission issues regardless of host user (root, regular user, etc.)

### Optional: Create host directories first

If you want to pre-create the directories:
```bash
mkdir -p ./LiteTTS/models ./LiteTTS/voices ./docs/logs ./cache
```

## What This Fixes

✅ **Model Downloads**: Container can now download `model_q4.onnx` to `LiteTTS/models/`  
✅ **Voice Downloads**: Container can download voice files (e.g., `af.bin`, `af_alloy.bin`) to `LiteTTS/voices/`  
✅ **Cache Files**: Container can save cache files like `voice_mappings.json`  
✅ **Log Files**: Container can write logs to `docs/logs/`  
✅ **Read-only Compatibility**: Works with read-only filesystem restrictions  

## Technical Details

- The container runs as user `litetts` (non-root)
- Symbolic links redirect writes from `/app/LiteTTS/*` to writable `/tmp/litetts/*` directories
- Host directories are mounted to `/tmp/litetts/*` paths for data persistence
- Proper permissions are set during container startup

## Verification

After starting the container, you can verify the fix by:

1. Checking container logs:
   ```bash
   docker-compose logs -f litetts
   ```

2. Verifying file downloads:
   ```bash
   ls -la ./LiteTTS/models/
   ls -la ./LiteTTS/voices/
   ```

3. Testing the API:
   ```bash
   curl http://localhost:8354/health
   ```

## Troubleshooting

If you still encounter permission issues:

1. **Check host directory permissions**:
   ```bash
   ls -la ./LiteTTS/models ./LiteTTS/voices ./docs/logs ./cache
   ```

2. **Rebuild the container**:
   ```bash
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

3. **Check container logs for specific errors**:
   ```bash
   docker-compose logs litetts
   ```
