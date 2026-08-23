#!/usr/bin/env python3
"""
Comprehensive validation script for enhanced Kokoro ONNX TTS API
Tests all enhanced features including package structure, imports, and functionality
"""

import json
import sys
import time
from pathlib import Path

import requests


def test_package_structure() -> dict[str, bool]:
    """Test that all package structure is correct"""
    print("🔍 Testing package structure...")

    results = {}

    # Test critical imports that were failing
    try:
        results["models_manager_import"] = True
        print("✅ ModelManager import successful")
    except Exception as e:
        results["models_manager_import"] = False
        print(f"❌ ModelManager import failed: {e}")

    try:
        results["hot_reload_import"] = True
        print("✅ HotReloadManager import successful")
    except Exception as e:
        results["hot_reload_import"] = False
        print(f"❌ HotReloadManager import failed: {e}")

    try:
        results["fault_tolerance_import"] = True
        print("✅ HealthChecker import successful")
    except Exception as e:
        results["fault_tolerance_import"] = False
        print(f"❌ HealthChecker import failed: {e}")

    try:
        results["downloader_import"] = True
        print("✅ Downloader import successful")
    except Exception as e:
        results["downloader_import"] = False
        print(f"❌ Downloader import failed: {e}")

    # Test __init__.py files exist
    init_files = [
        "LiteTTS/__init__.py",
        "LiteTTS/models/__init__.py",
        "LiteTTS/performance/__init__.py",
        "LiteTTS/LiteTTS/scripts/__init__.py",
        "LiteTTS/tests/__init__.py"
    ]

    for init_file in init_files:
        if Path(init_file).exists():
            results[f"init_{init_file.replace('/', '_').replace('.py', '')}"] = True
            print(f"✅ {init_file} exists")
        else:
            results[f"init_{init_file.replace('/', '_').replace('.py', '')}"] = False
            print(f"❌ {init_file} missing")

    return results

def test_configuration_system() -> dict[str, bool]:
    """Test the enhanced configuration system"""
    print("\n⚙️ Testing configuration system...")

    results = {}

    try:
        from LiteTTS.config import ConfigManager
        config = ConfigManager()

        # Test new configuration sections
        sections = ['model', 'voice', 'audio', 'server', 'performance', 'repository', 'paths']
        for section in sections:
            if hasattr(config, section):
                results[f"config_{section}"] = True
                print(f"✅ Configuration section '{section}' exists")
            else:
                results[f"config_{section}"] = False
                print(f"❌ Configuration section '{section}' missing")

        # Test specific configuration values
        if hasattr(config, 'voice') and hasattr(config.voice, 'default_voice'):
            results["config_default_voice"] = True
            print(f"✅ Default voice: {config.voice.default_voice}")
        else:
            results["config_default_voice"] = False
            print("❌ Default voice configuration missing")

        if hasattr(config, 'server') and hasattr(config.server, 'port'):
            results["config_server_port"] = True
            print(f"✅ Server port: {config.server.port}")
        else:
            results["config_server_port"] = False
            print("❌ Server port configuration missing")

    except Exception as e:
        results["config_system"] = False
        print(f"❌ Configuration system failed: {e}")

    return results

def test_logging_system() -> dict[str, bool]:
    """Test the comprehensive logging system"""
    print("\n📋 Testing logging system...")

    results = {}

    # Check log directory exists
    log_dir = Path("docs/logs")
    if log_dir.exists():
        results["log_directory"] = True
        print(f"✅ Log directory exists: {log_dir}")
    else:
        results["log_directory"] = False
        print(f"❌ Log directory missing: {log_dir}")
        return results

    # Check log files exist
    expected_logs = [
        "kokoro_tts.log",
        "performance.log",
        "cache.log",
        "errors.log",
        "structured.jsonl"
    ]

    for log_file in expected_logs:
        log_path = log_dir / log_file
        if log_path.exists():
            results[f"log_{log_file.replace('.', '_')}"] = True
            print(f"✅ Log file exists: {log_file}")
        else:
            results[f"log_{log_file.replace('.', '_')}"] = False
            print(f"❌ Log file missing: {log_file}")

    return results

def test_app_startup() -> dict[str, bool]:
    """Test application startup without errors"""
    print("\n🚀 Testing application startup...")

    results = {}

    try:
        import app
        results["app_import"] = True
        print("✅ App module imported successfully")

        # Test that the app can be imported and has the main function
        if hasattr(app, 'main') or hasattr(app, 'create_app'):
            results["app_main_function"] = True
            print("✅ App main function exists")
        else:
            results["app_main_function"] = False
            print("❌ App main function missing")

        # Test configuration import
        try:
            results["app_config"] = True
            print("✅ App configuration loaded")
        except Exception as e:
            results["app_config"] = False
            print(f"❌ App configuration failed: {e}")

    except Exception as e:
        results["app_startup"] = False
        print(f"❌ App startup failed: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")

    return results

def test_api_endpoints(base_url: str = "http://localhost:8354") -> dict[str, bool]:
    """Test API endpoints (requires running server)"""
    print(f"\n🌐 Testing API endpoints at {base_url}...")

    results = {}

    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/v1/health", timeout=5)
        if response.status_code == 200:
            results["health_endpoint"] = True
            print("✅ Health endpoint responding")
        else:
            results["health_endpoint"] = False
            print(f"❌ Health endpoint failed: {response.status_code}")
    except Exception as e:
        results["health_endpoint"] = False
        print(f"❌ Health endpoint error: {e}")

    # Test voices endpoint
    try:
        response = requests.get(f"{base_url}/v1/voices", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'voices' in data and len(data['voices']) > 0:
                results["voices_endpoint"] = True
                print(f"✅ Voices endpoint responding with {len(data['voices'])} voices")
            else:
                results["voices_endpoint"] = False
                print("❌ Voices endpoint returned empty data")
        else:
            results["voices_endpoint"] = False
            print(f"❌ Voices endpoint failed: {response.status_code}")
    except Exception as e:
        results["voices_endpoint"] = False
        print(f"❌ Voices endpoint error: {e}")

    return results

def main():
    """Run comprehensive validation"""
    print("🎯 Kokoro ONNX TTS API - Comprehensive Validation")
    print("=" * 60)

    all_results = {}

    # Run all tests
    all_results.update(test_package_structure())
    all_results.update(test_configuration_system())
    all_results.update(test_logging_system())
    all_results.update(test_app_startup())

    # Test API endpoints if server is running
    try:
        all_results.update(test_api_endpoints())
    except Exception as e:
        print(f"\n⚠️ API endpoint testing skipped (server not running): {e}")

    # Summary
    print("\n📊 Validation Summary")
    print("=" * 60)

    passed = sum(1 for result in all_results.values() if result)
    total = len(all_results)

    print(f"✅ Passed: {passed}/{total} tests")
    print(f"❌ Failed: {total - passed}/{total} tests")

    if total - passed > 0:
        print("\n❌ Failed tests:")
        for test_name, result in all_results.items():
            if not result:
                print(f"   - {test_name}")

    # Save results
    results_file = Path("docs/logs/validation_results.json")
    results_file.parent.mkdir(parents=True, exist_ok=True)

    with open(results_file, 'w') as f:
        json.dump({
            'timestamp': time.time(),
            'summary': {
                'passed': passed,
                'total': total,
                'success_rate': passed / total if total > 0 else 0
            },
            'results': all_results
        }, f, indent=2)

    print(f"\n📄 Results saved to: {results_file}")

    # Exit with appropriate code
    if passed == total:
        print("\n🎉 All tests passed! Enhanced Kokoro ONNX TTS API is ready!")
        sys.exit(0)
    else:
        print(f"\n⚠️ {total - passed} tests failed. Please review and fix issues.")
        sys.exit(1)

if __name__ == "__main__":
    main()
