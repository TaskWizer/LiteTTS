# Windows 10 Compatibility Guide

This guide provides comprehensive information about running LiteTTS on Windows 10, including compatibility fixes, validation tools, and troubleshooting steps.

## 🎯 Quick Start for Windows Users

### Prerequisites
- Windows 10 (build 1903 or later recommended)
- Python 3.8+ (Python 3.12+ recommended)
- PowerShell or Command Prompt with UTF-8 support

### Installation Steps

1. **Clone the repository:**
   ```cmd
   git clone https://github.com/TaskWizer/LiteTTS.git
   cd LiteTTS
   ```

2. **Run Windows compatibility validation:**
   ```cmd
   python scripts/windows_compatibility_test.py
   ```

3. **If validation passes, start the application:**
   ```cmd
   uv run python app.py
   ```

## 🔧 Windows Compatibility Fixes

LiteTTS includes several Windows-specific compatibility fixes:

### Unicode Encoding Support
- **Issue**: Windows console uses cp1252 encoding by default, causing UnicodeEncodeError with emoji characters
- **Fix**: Automatic console encoding configuration and emoji fallback system
- **Location**: `LiteTTS/utils/platform_emojis.py`, `LiteTTS/startup.py`

### File Operations
- **Issue**: File operations without explicit encoding specification cause UnicodeDecodeError
- **Fix**: All file operations now use UTF-8 encoding explicitly
- **Affected Files**: Configuration files, HTML files, JSON files

### Dependency Warnings
- **Issue**: pkg_resources deprecation warnings from third-party libraries
- **Fix**: Comprehensive warning suppression system
- **Location**: `LiteTTS/utils/deprecation_warnings.py`

## 🧪 Validation Tools

### Windows Compatibility Test
Comprehensive test suite that validates all Windows compatibility fixes:

```cmd
python scripts/windows_compatibility_test.py
```

**Tests Include:**
- Platform detection
- Unicode encoding detection and handling
- Console configuration
- File encoding operations
- JSON file operations
- Warning suppression
- Logging system with emojis
- Core module imports

### Windows Startup Validator
Validates that LiteTTS can start correctly on Windows:

```cmd
python scripts/windows_startup_validator.py
```

**Validation Steps:**
- Environment validation
- Early imports without warnings
- Emoji display capabilities
- File operations
- Logging system
- Core module imports

## 📊 Test Results

Both validation tools save detailed results to `test_results/`:
- `windows_compatibility_results.json` - Compatibility test results
- `windows_startup_validation.json` - Startup validation results

## 🐛 Troubleshooting

### Common Issues and Solutions

#### 1. UnicodeEncodeError in Console Output
**Symptoms:**
```
UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f4cb'
```

**Solutions:**
1. Run the compatibility test to verify fixes are working
2. Ensure you're using a modern terminal (Windows Terminal recommended)
3. Set environment variable: `set PYTHONIOENCODING=utf-8`

#### 2. UnicodeDecodeError Reading Files
**Symptoms:**
```
UnicodeDecodeError: 'charmap' codec can't decode byte 0x8f
```

**Solutions:**
1. Verify all file operations use UTF-8 encoding
2. Check that HTML/config files are saved in UTF-8 format
3. Run the file operations test

#### 3. pkg_resources Deprecation Warnings
**Symptoms:**
```
UserWarning: pkg_resources is deprecated as an API
```

**Solutions:**
1. Warnings should be automatically suppressed
2. If warnings persist, check warning suppression initialization
3. Update dependencies if possible

### Advanced Troubleshooting

#### Enable Debug Logging
```cmd
set LOGLEVEL=DEBUG
python app.py
```

#### Test Individual Components
```python
# Test emoji handling
python -c "from LiteTTS.utils.platform_emojis import format_log_message; print(format_log_message('rocket', 'Test'))"

# Test console configuration
python -c "from LiteTTS.startup import configure_windows_console; print(configure_windows_console())"

# Test file encoding
python -c "import json; print(json.dumps({'test': '🚀'}, ensure_ascii=False))"
```

## 🔍 Manual Verification Steps

If automated tests fail, you can manually verify the fixes:

### 1. Console Encoding Test
```cmd
python -c "print('🚀 📋 ✅ Test emojis')"
```
Should display emojis without errors.

### 2. File Encoding Test
```cmd
echo {"test": "🚀"} > test.json
python -c "import json; print(json.load(open('test.json', encoding='utf-8')))"
del test.json
```

### 3. Import Test
```cmd
python -c "from LiteTTS.config import config; print('Config loaded successfully')"
```

## 📋 Windows-Specific Configuration

### Recommended Terminal Settings
For best experience, use Windows Terminal with these settings:

1. **Install Windows Terminal** from Microsoft Store
2. **Configure UTF-8 support:**
   - Open Windows Terminal settings
   - Add to profile: `"commandline": "cmd.exe /k chcp 65001"`
3. **Use a Unicode-compatible font** (Cascadia Code recommended)

### Environment Variables
Set these environment variables for optimal Windows compatibility:

```cmd
set PYTHONIOENCODING=utf-8
set PYTHONLEGACYWINDOWSSTDIO=utf-8
set PYTHONUTF8=1
```

### PowerShell Configuration
For PowerShell users, add to your profile:

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
```

## 🚀 Performance Optimization for Windows

### CPU Optimization
LiteTTS includes Windows-specific CPU optimization:
- Automatic core detection and allocation
- Thermal protection
- ONNX runtime optimization for Windows

### Memory Management
- Optimized for Windows memory patterns
- Automatic garbage collection tuning
- Cache size optimization based on available RAM

## 📞 Support

If you encounter Windows-specific issues:

1. **Run the validation tools** first to identify specific problems
2. **Check the troubleshooting section** for common solutions
3. **Review test results** in `test_results/` for detailed diagnostics
4. **Create an issue** with validation results and error logs

### Required Information for Bug Reports
- Windows version (`winver` command output)
- Python version (`python --version`)
- Validation test results
- Complete error logs
- Steps to reproduce

## 🔄 Updates and Maintenance

### Keeping Windows Compatibility Updated
1. Run validation tests after each update
2. Monitor for new Windows-specific issues
3. Update dependencies regularly
4. Test with new Windows builds

### Contributing Windows Fixes
If you discover Windows-specific issues:
1. Create a test case in the validation suite
2. Implement the fix
3. Verify with validation tools
4. Submit a pull request with test results

## 📚 Additional Resources

- [Windows Terminal Documentation](https://docs.microsoft.com/en-us/windows/terminal/)
- [Python Unicode on Windows](https://docs.python.org/3/howto/unicode.html#unicode-on-windows)
- [UTF-8 Support in Windows](https://docs.microsoft.com/en-us/windows/apps/design/globalizing/use-utf8-code-page)

---

**Note**: This compatibility guide is specifically for Windows 10. Windows 11 users should also follow these guidelines, though some issues may not apply to newer Windows versions.
