#!/usr/bin/env python3
"""
Dependency Compatibility Test Script

Tests package compatibility, import functionality, and version conflicts
to ensure all dependencies work correctly together in the LiteTTS system.
"""

import sys
import importlib
import subprocess
import time
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple
import argparse

def get_installed_packages() -> Dict[str, str]:
    """Get list of installed packages with versions"""
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "list", "--format=json"], 
                              capture_output=True, text=True, check=True)
        packages = json.loads(result.stdout)
        return {pkg["name"]: pkg["version"] for pkg in packages}
    except Exception as e:
        print(f"❌ Failed to get installed packages: {e}")
        return {}

def test_core_dependencies() -> Dict[str, bool]:
    """Test core dependencies that are required for basic functionality"""
    
    core_deps = [
        "fastapi",
        "uvicorn", 
        "numpy",
        "soundfile",
        "onnxruntime",
        "torch",
        "pydantic",
        "requests",
        "pathlib",
        "json",
        "logging",
        "asyncio",
        "threading",
        "time",
        "os",
        "sys"
    ]
    
    results = {}
    
    print("🧪 Testing Core Dependencies")
    print("=" * 30)
    
    for dep in core_deps:
        try:
            importlib.import_module(dep)
            results[dep] = True
            print(f"✅ {dep}")
        except ImportError as e:
            results[dep] = False
            print(f"❌ {dep}: {e}")
        except Exception as e:
            results[dep] = False
            print(f"❌ {dep}: Unexpected error - {e}")
    
    return results

def test_optional_dependencies() -> Dict[str, bool]:
    """Test optional dependencies that provide enhanced functionality"""
    
    optional_deps = [
        "faster_whisper",
        "websockets", 
        "wsproto",
        "espeak",
        "pydub",
        "watchdog",
        "phonemizer",
        "matplotlib",
        "scipy"
    ]
    
    results = {}
    
    print("\n🔧 Testing Optional Dependencies")
    print("=" * 35)
    
    for dep in optional_deps:
        try:
            importlib.import_module(dep)
            results[dep] = True
            print(f"✅ {dep}")
        except ImportError:
            results[dep] = False
            print(f"⚠️ {dep}: Not available (optional)")
        except Exception as e:
            results[dep] = False
            print(f"❌ {dep}: Error - {e}")
    
    return results

def test_litetts_imports() -> Dict[str, bool]:
    """Test LiteTTS module imports"""
    
    litetts_modules = [
        "LiteTTS",
        "LiteTTS.config",
        "LiteTTS.api",
        "LiteTTS.performance",
        "LiteTTS.validation",
        "LiteTTS.utils",
        "LiteTTS.websocket",
        "LiteTTS.cache",
        "LiteTTS.monitoring",
        "LiteTTS.nlp",
        "LiteTTS.tts",
        "LiteTTS.voice"
    ]
    
    results = {}
    
    print("\n🏗️ Testing LiteTTS Module Imports")
    print("=" * 40)
    
    for module in litetts_modules:
        try:
            importlib.import_module(module)
            results[module] = True
            print(f"✅ {module}")
        except ImportError as e:
            results[module] = False
            print(f"❌ {module}: {e}")
        except Exception as e:
            results[module] = False
            print(f"❌ {module}: Unexpected error - {e}")
    
    return results

def check_version_conflicts() -> Dict[str, Any]:
    """Check for potential version conflicts"""
    
    print("\n🔍 Checking Version Conflicts")
    print("=" * 30)
    
    conflicts = {
        "detected_conflicts": [],
        "warnings": [],
        "recommendations": []
    }
    
    packages = get_installed_packages()
    
    # Check for known problematic combinations
    version_checks = [
        {
            "package": "torch",
            "min_version": "1.9.0",
            "reason": "Required for ONNX compatibility"
        },
        {
            "package": "onnxruntime", 
            "min_version": "1.10.0",
            "reason": "Performance and stability improvements"
        },
        {
            "package": "fastapi",
            "min_version": "0.68.0", 
            "reason": "WebSocket support and security fixes"
        },
        {
            "package": "uvicorn",
            "min_version": "0.15.0",
            "reason": "WebSocket protocol support"
        }
    ]
    
    for check in version_checks:
        pkg_name = check["package"]
        if pkg_name in packages:
            installed_version = packages[pkg_name]
            print(f"📦 {pkg_name}: {installed_version}")
            
            # Simple version comparison (basic implementation)
            try:
                from packaging import version
                if version.parse(installed_version) < version.parse(check["min_version"]):
                    conflicts["warnings"].append({
                        "package": pkg_name,
                        "installed": installed_version,
                        "minimum": check["min_version"],
                        "reason": check["reason"]
                    })
                    print(f"⚠️ {pkg_name} version may be too old")
            except ImportError:
                # Fallback without packaging library
                conflicts["recommendations"].append(f"Install packaging library for better version checking")
        else:
            print(f"❌ {pkg_name}: Not installed")
    
    return conflicts

def test_dependency_compatibility(check_imports: bool = True, check_versions: bool = True) -> bool:
    """
    Main dependency compatibility test function.
    
    Args:
        check_imports: Whether to test import functionality
        check_versions: Whether to check version compatibility
        
    Returns:
        True if all tests pass, False otherwise
    """
    
    print("🧪 Dependency Compatibility Test Suite")
    print("=" * 50)
    print("Testing package compatibility and import functionality...")
    print()
    
    all_results = {}
    overall_success = True
    
    if check_imports:
        # Test core dependencies
        core_results = test_core_dependencies()
        all_results["core"] = core_results
        
        # Test optional dependencies  
        optional_results = test_optional_dependencies()
        all_results["optional"] = optional_results
        
        # Test LiteTTS imports
        litetts_results = test_litetts_imports()
        all_results["litetts"] = litetts_results
        
        # Evaluate import results
        core_failures = sum(1 for success in core_results.values() if not success)
        litetts_failures = sum(1 for success in litetts_results.values() if not success)
        
        if core_failures > 0 or litetts_failures > 0:
            overall_success = False
    
    if check_versions:
        # Check version conflicts
        conflicts = check_version_conflicts()
        all_results["conflicts"] = conflicts
        
        if conflicts["detected_conflicts"] or conflicts["warnings"]:
            overall_success = False
    
    # Generate summary report
    print(f"\n" + "=" * 50)
    print(f"📊 DEPENDENCY COMPATIBILITY RESULTS:")
    
    if check_imports:
        core_success_rate = sum(all_results["core"].values()) / len(all_results["core"])
        optional_success_rate = sum(all_results["optional"].values()) / len(all_results["optional"])
        litetts_success_rate = sum(all_results["litetts"].values()) / len(all_results["litetts"])
        
        print(f"   Core Dependencies: {core_success_rate:.1%} success rate")
        print(f"   Optional Dependencies: {optional_success_rate:.1%} success rate") 
        print(f"   LiteTTS Modules: {litetts_success_rate:.1%} success rate")
    
    if check_versions:
        conflict_count = len(all_results["conflicts"]["detected_conflicts"])
        warning_count = len(all_results["conflicts"]["warnings"])
        print(f"   Version Conflicts: {conflict_count} detected")
        print(f"   Version Warnings: {warning_count} found")
    
    print(f"\nOverall Status: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    # Save detailed results
    results_file = Path("logs/dependency_audit.log")
    results_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(results_file, 'w') as f:
        f.write(f"Dependency Compatibility Test Results\n")
        f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Overall Success: {overall_success}\n\n")
        
        for category, results in all_results.items():
            f.write(f"{category.upper()} RESULTS:\n")
            if isinstance(results, dict) and "detected_conflicts" in results:
                # Version conflict results
                f.write(f"Conflicts: {len(results['detected_conflicts'])}\n")
                f.write(f"Warnings: {len(results['warnings'])}\n")
                for warning in results["warnings"]:
                    f.write(f"  - {warning}\n")
            else:
                # Import test results
                for item, success in results.items():
                    f.write(f"  {item}: {'PASS' if success else 'FAIL'}\n")
            f.write("\n")
    
    print(f"📄 Detailed results saved to: {results_file}")
    
    return overall_success

def main():
    """Main test execution"""
    
    parser = argparse.ArgumentParser(description="Test dependency compatibility")
    parser.add_argument("--check-imports", action="store_true", default=True,
                       help="Test import functionality")
    parser.add_argument("--check-versions", action="store_true", default=True, 
                       help="Check version compatibility")
    
    args = parser.parse_args()
    
    success = test_dependency_compatibility(args.check_imports, args.check_versions)
    
    if success:
        print("\n🎉 All dependency compatibility tests passed!")
        print("✅ Package imports working correctly")
        print("✅ No critical version conflicts detected")
        print("✅ LiteTTS modules loading successfully")
        return 0
    else:
        print("\n⚠️ Some dependency compatibility issues detected")
        print("❌ Check the detailed log for specific failures")
        print("💡 Consider updating packages or resolving conflicts")
        return 1

if __name__ == "__main__":
    exit(main())
