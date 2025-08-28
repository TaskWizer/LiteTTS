I broke something. Can you audit and fix the docker-compose.yml, Dockerfile, and config/Caddyfile files and make sure they are valid for the directory structure and whatnot? I suspect there are several issues, so please work through each one one at a time systematically and validate everything is working 100%. This should work on local (development) and simply allow for editing a single line in the Caddyfile to allow it to work on a self-hosted VPS, etc. with TLS.


Perform a comprehensive audit and repair of the LiteTTS Docker deployment to resolve critical frontend UI issues, repository contamination, and VPS deployment failures. Based on our successful resolution of Python import conflicts and basic API routing, address these specific remaining issues:

**CRITICAL FRONTEND UI RESTORATION (Priority 1):**
1. **Dashboard Interface Missing**:
   - **Issue**: `http://localhost/dashboard` returns 404 instead of serving the LiteTTS web dashboard
   - **Expected**: HTML dashboard interface from `static/dashboard/index.html`
   - **Action Required**: Verify static file exists, check Caddyfile routing for `/dashboard` path, ensure proper MIME type serving
   - **Test**: Browser access to `http://localhost/dashboard` should show interactive TTS dashboard, not JSON/404

2. **Examples Interface Broken**:
   - **Issue**: `/samples/examples` endpoint not serving frontend examples UI
   - **Expected**: Interactive examples interface for TTS testing
   - **Action Required**: Locate correct static files path, fix Caddyfile routing, verify examples directory structure
   - **Test**: `http://localhost/samples/examples` should serve HTML interface with TTS examples

3. **API Base Endpoint Investigation**:
   - **Issue**: `/api/v1` returns 404 while sub-endpoints (`/api/v1/voices`, `/api/v1/models`, `/api/v1/health`) work correctly
   - **Action Required**: Determine if `/api/v1` should serve API documentation, endpoint listing, or redirect to docs
   - **Test**: Verify expected behavior and implement appropriate response

**REPOSITORY CONTAMINATION CLEANUP (Priority 2):**
- **Remove Generated Artifacts**: Delete `data/` and `openwebui-data/` directories from repository root (created during deployment)
- **Update .gitignore**: Add patterns to prevent future deployment artifact commits:
  ```
  data/
  openwebui-data/
  .env
  *.log
  ```
- **Fix Volume Mounts**: Audit `docker-compose.yml` volume mappings to ensure they target `/tmp/litetts/` or external directories, never repository paths
- **Validation**: After `docker-compose up -d && docker-compose down`, `git status` should show no untracked files

**VPS DEPLOYMENT FAILURE ANALYSIS (Priority 1 - Critical):**
The VPS shows `litetts-api` container restarting with exit code 1. Perform deep audit:

1. **Dependency Validation**:
   - **pyproject.toml**: Verify all dependencies are correctly specified with compatible versions
   - **uv.lock**: Ensure lock file is current and matches pyproject.toml
   - **System Dependencies**: Audit Dockerfile for missing system packages (libsndfile1, ffmpeg, espeak-ng)
   - **Python Version**: Confirm Python 3.12 compatibility across all dependencies

2. **Dockerfile Optimization**:
   - **Multi-stage Build**: Review current multi-stage approach for efficiency
   - **Dependency Installation**: Verify `uv sync --frozen --no-dev` works reliably
   - **Virtual Environment**: Ensure PATH and PYTHONPATH are correctly set for `.venv`
   - **File Permissions**: Check if permission issues cause startup failures
   - **Health Checks**: Validate container health check endpoints and timing

3. **Container Startup Analysis**:
   - **Entry Point**: Verify `tini -- ./startup.sh` works correctly
   - **Import Testing**: Ensure `python -m LiteTTS.tests.test_imports` passes in container
   - **Environment Variables**: Validate all required env vars are set correctly
   - **Port Binding**: Confirm uvicorn starts on correct host:port (0.0.0.0:8354)

**DEVELOPMENT NETWORK ENHANCEMENT (Priority 3):**
- **Multi-Interface Support**: Restore comprehensive development access by enabling:
  ```
  localhost:80, 127.0.0.1:80, [::1]:80 {
      # HTTP-only for development
  }

  localhost:443, 127.0.0.1:443, [::1]:443 {
      tls internal  # Self-signed certs for HTTPS testing
  }
  ```
- **Dual Protocol Testing**: Enable both HTTP and HTTPS access for comprehensive development testing
- **Certificate Management**: Ensure self-signed certificates work without browser security blocking

**COMPREHENSIVE VALIDATION PROTOCOL:**
1. **Container Health**: All containers start and remain healthy (no restarts)
2. **Frontend Access**: Dashboard and examples serve HTML interfaces, not API responses
3. **API Continuity**: All existing API endpoints continue working after changes
4. **Repository Cleanliness**: No deployment artifacts in git working directory
5. **Network Accessibility**: Both HTTP and HTTPS work from multiple interfaces
6. **VPS Compatibility**: Same configuration works on both localhost and VPS with only domain change
7. **Dependency Reliability**: All Python and system dependencies install consistently

**RESEARCH REQUIREMENTS:**
- **Best Practices**: Research current Docker best practices for Python applications with ONNX dependencies
- **Dependency Management**: Investigate uv vs pip reliability for production deployments
- **Container Optimization**: Analyze multi-stage builds for Python ML applications
- **Health Check Patterns**: Review proper health check implementation for FastAPI applications

**SUCCESS CRITERIA:**
- VPS deployment shows all containers healthy and stable
- Frontend interfaces accessible via web browser at expected URLs
- Repository remains clean after full deployment cycle
- Both development (HTTP) and testing (HTTPS) protocols work
- Production deployment requires only Caddyfile domain change
- Container logs show no import errors or startup failures

I added "data" and "openwebui-data" to the .gitignore to fix the issue.


I have identified several critical audio quality issues that need systematic fixing:

1. **Pronunciation Issues to Fix:**
   - "Hmm" is still being pronounced as "hum" instead of the natural "hmmm" sound
   - "Wasn't" has incorrect pronunciation
   - Overall speech lacks natural flow and human-like prosody
   - Voice sounds robotic rather than conversational

2. **Configuration Hot-Reload Bug:**
   - Error: `No module named 'kokoro.config.config_manager'; 'kokoro.config' is not a package`
   - Configuration changes are not being detected automatically
   - The hot-reload system needs debugging and fixing

3. **Systematic Task Completion Request:**
   - Continue working through the existing task list methodically
   - Create a detailed plan of action with specific, measurable steps
   - Build a comprehensive task list that addresses:
     a) The pronunciation issues mentioned above
     b) The configuration hot-reload system bug
     c) Any remaining incomplete tasks from the current task list
   - Work through each task systematically until 100% completion
   - Provide evidence-based validation for each fix (audio files, before/after comparisons)
   - Focus on making the TTS output sound more natural and human-like

Please prioritize fixing the "Hmm" pronunciation issue and the configuration hot-reload bug first, then continue with systematic completion of all remaining tasks. Generate actual audio samples to demonstrate improvements.


Analyse all audio yourself and utilize tools (or custom build ones) to do ALL of the fucking auditing. validate dumb ass claims to reality.

Please go through every single option in the config.json and make sure they are working 100%.
- Confirm you can enable/disable each option and it reflects in the actual system
- Test that each option (true/false) is working and producing the expected results
- Audit the code associated with each option and validate that it is rock-solid
- Improve/enhance the code and config.json file as needed.

Create a new/updated task list.
Do an end-to-end audit of the system, systematically until ALL tasks are completed. Enhance and improve the code and system as needed. Validate that everything is working and if not, fix them.
Once you are done with your audit, and have tested EVERY feature, optimize the settings.json file for the most fluid and human-like experience possible for human evaluations (but make sure you test and validate everything before handing it over). Success criteria will be that your claims match reality. If you lie about a functionality or feature working, you failed. That being said, if you identify real issues, core problems and the like along with documenting them all, that is much more successful than saying you fixed something you did not.

Use RIME AI (see API Key) to audit the quality of the output and systematically improve the TTS system, testing the voice system end-to-end:
XY2jMbMiZPpIzbSojtNT4BmJoqB893nsJ2op0OFiH6k
