# Repository Cleanup Analysis

## Files Identified for Cleanup

### Test Files in Root Directory (TO BE REMOVED)
- `test_audio_gen.py` - GGUF testing script (14,490 bytes)
- `test_audio_gen (copy).py` - Duplicate copy (854 bytes)
- `test_audio_gen (another copy).py` - Duplicate copy (5,332 bytes)
- `test_audio_gen (3rd copy).py` - Duplicate copy (12,170 bytes)
- `test_gguf_fixes.py` - GGUF fixes testing (9,409 bytes)
- `test_litetts_integration.py` - Integration testing (14,500 bytes) **PRESERVE**
- `test_ttscpp_backend.py` - TTS.cpp backend testing (14,392 bytes) **PRESERVE**

### Audio Files in Root Directory (TO BE REMOVED)
- `test_litetts_integration_output.wav` - Test output file
- `test_am_adam.mp3` - Test audio file
- `final_fixed_hello.mp3` - Test audio file

### Temporary Directories (TO BE REMOVED)
- `__pycache__/` - Python cache directory
- `.pytest_cache/` - Pytest cache directory
- `test_results/` - Test results directory
- `test_audio_files/` - Test audio files directory

### Debug/Analysis Files (TO BE REMOVED)
- `audio_debug.py` - Audio debugging script (3,731 bytes)
- `audio_quality_analysis.py` - Audio quality analysis (7,397 bytes)
- `audio_quality_analysis_results.json` - Analysis results (3,052 bytes)

### Configuration Files (CONSOLIDATE)
- `config.json` - Root config file (1,935 bytes) **REMOVE** (duplicate of settings.json)
- `override.json` - Hardware optimization overrides (532 bytes) **REMOVE** (consolidate into settings.json)
- `config/settings.json` - Main configuration file **KEEP AS AUTHORITATIVE**

## Files to Preserve and Migrate

### Valuable Test Scripts (MIGRATE TO LiteTTS/tests/)
1. `test_ttscpp_backend.py` → `LiteTTS/tests/test_ttscpp_backend.py`
   - Comprehensive TTSCppBackend test suite
   - Contains valuable GGUF testing logic
   
2. `test_litetts_integration.py` → `LiteTTS/tests/test_integration.py`
   - End-to-end integration testing
   - Tests complete LiteTTS system with GGUF backend

### Configuration Consolidation Plan
1. Merge `override.json` hardware optimizations into `config/settings.json`
2. Remove duplicate `config.json` from root
3. Ensure all code references `config/settings.json` as single source of truth

## Cleanup Actions Summary
- **Remove**: 9 test files, 3 audio files, 4 directories, 3 debug files
- **Migrate**: 2 valuable test scripts to proper location
- **Consolidate**: 3 config files into 1 authoritative file
- **Total files to remove**: ~19 files/directories
- **Disk space to reclaim**: ~100MB+ (including cache directories)

## COMPLETED CLEANUP ACTIONS

### Files Successfully Removed (✓)
1. **Test Files**:
   - `test_audio_gen.py` (14,490 bytes)
   - `test_audio_gen (copy).py` (854 bytes)
   - `test_audio_gen (another copy).py` (5,332 bytes)
   - `test_audio_gen (3rd copy).py` (12,170 bytes)
   - `test_gguf_fixes.py` (9,409 bytes)
   - `test_litetts_integration.py` (14,500 bytes)
   - `test_ttscpp_backend.py` (14,392 bytes)

2. **Audio Files**:
   - `test_litetts_integration_output.wav`
   - `test_am_adam.mp3`
   - `final_fixed_hello.mp3`

3. **Debug/Analysis Files**:
   - `audio_debug.py` (3,731 bytes)
   - `audio_quality_analysis.py` (7,397 bytes)
   - `audio_quality_analysis_results.json` (3,052 bytes)

4. **Temporary Directories**:
   - `__pycache__/` (Python cache)
   - `.pytest_cache/` (Pytest cache)
   - `test_results/` (Test results)
   - `test_audio_files/` (Test audio files)

### Files Successfully Migrated (✓)
1. `test_ttscpp_backend.py` → `LiteTTS/tests/test_ttscpp_backend.py`
2. `test_litetts_integration.py` → `LiteTTS/tests/test_litetts_integration.py`

### Model Files Organization (✓)
- All model files properly organized under `LiteTTS/models/`
- GGUF model: `LiteTTS/models/Kokoro_espeak_Q4.gguf`
- ONNX model: `LiteTTS/models/model_q4_bak_bak.onnx`
- No model files found outside proper directories (excluding .venv dependencies)

### Next Phase: Configuration Consolidation
- Remove duplicate `config.json` from root
- Remove `override.json` from root
- Consolidate all settings into `config/settings.json`
- Add beta feature flags for performance optimization modules
