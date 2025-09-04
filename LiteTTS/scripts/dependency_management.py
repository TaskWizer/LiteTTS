#!/usr/bin/env python3
"""
Dependency Management Script

Provides automated testing, version pinning, and update procedures
for LiteTTS dependencies with security scanning and compatibility validation.
"""

import sys
import os
import json
import subprocess
import time
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import argparse

# Add LiteTTS to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def get_current_dependencies() -> Dict[str, str]:
    """Get currently installed dependencies with versions"""
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "list", "--format=json"
        ], capture_output=True, text=True, check=True)
        
        packages = json.loads(result.stdout)
        return {pkg["name"]: pkg["version"] for pkg in packages}
    except Exception as e:
        print(f"❌ Failed to get current dependencies: {e}")
        return {}

def read_pyproject_dependencies() -> Dict[str, Any]:
    """Read dependencies from pyproject.toml"""
    try:
        import tomllib
        
        pyproject_path = Path("pyproject.toml")
        if not pyproject_path.exists():
            print("⚠️ pyproject.toml not found")
            return {}
        
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        
        dependencies = {}
        
        # Main dependencies
        if "project" in data and "dependencies" in data["project"]:
            dependencies["main"] = data["project"]["dependencies"]
        
        # Optional dependencies
        if "project" in data and "optional-dependencies" in data["project"]:
            dependencies["optional"] = data["project"]["optional-dependencies"]
        
        return dependencies
        
    except ImportError:
        print("⚠️ tomllib not available, using fallback method")
        return {}
    except Exception as e:
        print(f"❌ Failed to read pyproject.toml: {e}")
        return {}

def validate_version_pins(dry_run: bool = True) -> Dict[str, Any]:
    """Validate current version pins and suggest improvements"""
    
    print("📌 Validating Version Pins")
    print("=" * 30)
    
    results = {
        "current_pins": {},
        "suggested_pins": {},
        "unpinned_packages": [],
        "outdated_pins": [],
        "validation_successful": True
    }
    
    # Get current dependencies
    current_deps = get_current_dependencies()
    pyproject_deps = read_pyproject_dependencies()
    
    # Critical packages that should be pinned
    critical_packages = [
        "torch", "onnxruntime", "fastapi", "uvicorn", 
        "numpy", "soundfile", "pydantic"
    ]
    
    print(f"🔍 Checking version pins for {len(critical_packages)} critical packages...")
    
    for package in critical_packages:
        if package in current_deps:
            current_version = current_deps[package]
            results["current_pins"][package] = current_version
            
            # Check if package is properly pinned in pyproject.toml
            is_pinned = False
            pin_info = "not pinned in pyproject.toml"
            
            # Look for the package in dependencies
            for dep_type, deps in pyproject_deps.items():
                if isinstance(deps, list):
                    for dep in deps:
                        if isinstance(dep, str) and dep.startswith(package):
                            if ">=" in dep or "==" in dep or "~=" in dep:
                                is_pinned = True
                                pin_info = dep
                            break
                elif isinstance(deps, dict):
                    for group, group_deps in deps.items():
                        if isinstance(group_deps, list):
                            for dep in group_deps:
                                if isinstance(dep, str) and dep.startswith(package):
                                    if ">=" in dep or "==" in dep or "~=" in dep:
                                        is_pinned = True
                                        pin_info = dep
                                    break
            
            if is_pinned:
                print(f"✅ {package}: {current_version} (pinned: {pin_info})")
            else:
                print(f"⚠️ {package}: {current_version} (not pinned)")
                results["unpinned_packages"].append(package)
                results["suggested_pins"][package] = f"{package}>={current_version}"
        else:
            print(f"❌ {package}: not installed")
            results["validation_successful"] = False
    
    # Summary
    print(f"\n📊 Version Pin Validation Summary:")
    print(f"   Packages checked: {len(critical_packages)}")
    print(f"   Properly pinned: {len(critical_packages) - len(results['unpinned_packages'])}")
    print(f"   Unpinned packages: {len(results['unpinned_packages'])}")
    
    if results["unpinned_packages"]:
        print(f"   Suggested pins:")
        for package in results["unpinned_packages"]:
            print(f"     - {results['suggested_pins'][package]}")
    
    return results

def test_dependency_updates(dry_run: bool = True) -> Dict[str, Any]:
    """Test dependency updates for compatibility"""
    
    print(f"\n🔄 Testing Dependency Updates {'(DRY RUN)' if dry_run else ''}")
    print("=" * 50)
    
    results = {
        "updates_available": {},
        "compatibility_tests": {},
        "update_recommendations": [],
        "test_successful": True
    }
    
    if dry_run:
        print("🔍 Checking for available updates (dry run mode)...")
        
        try:
            # Check for outdated packages
            result = subprocess.run([
                sys.executable, "-m", "pip", "list", "--outdated", "--format=json"
            ], capture_output=True, text=True, check=True)
            
            outdated_packages = json.loads(result.stdout)
            
            for package in outdated_packages:
                name = package["name"]
                current = package["version"]
                latest = package["latest_version"]
                
                results["updates_available"][name] = {
                    "current": current,
                    "latest": latest,
                    "type": package.get("latest_filetype", "unknown")
                }
                
                print(f"📦 {name}: {current} → {latest}")
            
            print(f"\n📊 Update Check Summary:")
            print(f"   Packages with updates: {len(outdated_packages)}")
            
            if outdated_packages:
                print(f"   Note: Use --no-dry-run to test actual updates")
            else:
                print(f"   All packages are up to date")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to check for updates: {e}")
            results["test_successful"] = False
        except Exception as e:
            print(f"❌ Update check failed: {e}")
            results["test_successful"] = False
    
    else:
        print("⚠️ Actual update testing not implemented for safety")
        print("   This would require creating isolated test environments")
        results["test_successful"] = False
    
    return results

def security_scan() -> Dict[str, Any]:
    """Perform security scanning of dependencies"""
    
    print(f"\n🔒 Security Scanning")
    print("=" * 25)
    
    results = {
        "scan_completed": False,
        "vulnerabilities": [],
        "recommendations": [],
        "scan_tool": None
    }
    
    # Try different security scanning tools
    scan_tools = [
        {
            "name": "pip-audit",
            "command": [sys.executable, "-m", "pip_audit", "--format=json"],
            "install_cmd": "uv add pip-audit"
        },
        {
            "name": "safety",
            "command": [sys.executable, "-m", "safety", "check", "--json"],
            "install_cmd": "uv add safety"
        }
    ]
    
    for tool in scan_tools:
        try:
            print(f"🔍 Trying {tool['name']}...")
            
            result = subprocess.run(
                tool["command"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print(f"✅ {tool['name']}: No vulnerabilities found")
                results["scan_completed"] = True
                results["scan_tool"] = tool["name"]
                break
            else:
                # Parse vulnerabilities if any
                try:
                    if tool["name"] == "pip-audit" and result.stdout:
                        vuln_data = json.loads(result.stdout)
                        results["vulnerabilities"] = vuln_data.get("vulnerabilities", [])
                    elif tool["name"] == "safety" and result.stdout:
                        vuln_data = json.loads(result.stdout)
                        results["vulnerabilities"] = vuln_data
                    
                    print(f"⚠️ {tool['name']}: {len(results['vulnerabilities'])} vulnerabilities found")
                    results["scan_completed"] = True
                    results["scan_tool"] = tool["name"]
                    break
                except json.JSONDecodeError:
                    print(f"❌ {tool['name']}: Failed to parse output")
                    continue
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {tool['name']}: Scan timed out")
            continue
        except FileNotFoundError:
            print(f"❌ {tool['name']}: Not installed")
            print(f"   Install with: {tool['install_cmd']}")
            continue
        except Exception as e:
            print(f"❌ {tool['name']}: Scan failed - {e}")
            continue
    
    if not results["scan_completed"]:
        print(f"⚠️ No security scanning tools available")
        print(f"   Consider installing pip-audit or safety for vulnerability scanning")
        results["recommendations"].append("Install security scanning tools")
    
    return results

def generate_dependency_report() -> Dict[str, Any]:
    """Generate comprehensive dependency management report"""
    
    print(f"\n📋 Generating Dependency Management Report")
    print("=" * 45)
    
    # Collect all test results
    pin_validation = validate_version_pins(dry_run=True)
    update_testing = test_dependency_updates(dry_run=True)
    security_results = security_scan()
    
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "version_pins": pin_validation,
        "update_testing": update_testing,
        "security_scan": security_results,
        "recommendations": []
    }
    
    # Generate recommendations
    if pin_validation["unpinned_packages"]:
        report["recommendations"].append({
            "type": "version_pinning",
            "priority": "high",
            "description": f"Pin {len(pin_validation['unpinned_packages'])} critical packages",
            "packages": pin_validation["unpinned_packages"]
        })
    
    if update_testing["updates_available"]:
        report["recommendations"].append({
            "type": "updates",
            "priority": "medium", 
            "description": f"Test {len(update_testing['updates_available'])} available updates",
            "packages": list(update_testing["updates_available"].keys())
        })
    
    if security_results["vulnerabilities"]:
        report["recommendations"].append({
            "type": "security",
            "priority": "critical",
            "description": f"Address {len(security_results['vulnerabilities'])} security vulnerabilities",
            "vulnerabilities": security_results["vulnerabilities"]
        })
    
    # Save report
    report_file = Path("logs/dependency_management_report.json")
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📄 Report saved to: {report_file}")
    
    return report

def main():
    """Main dependency management execution"""
    
    parser = argparse.ArgumentParser(description="Dependency management and testing")
    parser.add_argument("--test-updates", action="store_true",
                       help="Test dependency updates for compatibility")
    parser.add_argument("--dry-run", action="store_true", default=True,
                       help="Perform dry run without making changes")
    parser.add_argument("--no-dry-run", action="store_false", dest="dry_run",
                       help="Perform actual operations (use with caution)")
    parser.add_argument("--validate-pins", action="store_true", default=True,
                       help="Validate version pins")
    parser.add_argument("--security-scan", action="store_true",
                       help="Perform security vulnerability scan")
    
    args = parser.parse_args()
    
    print("🧪 Dependency Management Test Suite")
    print("=" * 50)
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE EXECUTION'}")
    print()
    
    # Generate comprehensive report
    report = generate_dependency_report()
    
    # Evaluate overall status
    pin_issues = len(report["version_pins"]["unpinned_packages"])
    security_issues = len(report["security_scan"]["vulnerabilities"])
    update_count = len(report["update_testing"]["updates_available"])
    
    print(f"\n" + "=" * 50)
    print(f"📊 DEPENDENCY MANAGEMENT RESULTS:")
    print(f"   Version Pin Issues: {pin_issues}")
    print(f"   Security Vulnerabilities: {security_issues}")
    print(f"   Available Updates: {update_count}")
    print(f"   Total Recommendations: {len(report['recommendations'])}")
    
    # Determine overall status
    critical_issues = security_issues
    high_priority_issues = pin_issues
    
    if critical_issues > 0:
        status = "❌ CRITICAL ISSUES"
        print(f"\n🚨 Critical security vulnerabilities detected!")
    elif high_priority_issues > 0:
        status = "⚠️ HIGH PRIORITY ISSUES"
        print(f"\n⚠️ Version pinning issues detected")
    elif update_count > 0:
        status = "📋 UPDATES AVAILABLE"
        print(f"\n📋 Dependency updates available for testing")
    else:
        status = "✅ ALL GOOD"
        print(f"\n🎉 Dependency management is in good shape!")
    
    print(f"\nOverall Status: {status}")
    
    # Show recommendations
    if report["recommendations"]:
        print(f"\n💡 Recommendations:")
        for i, rec in enumerate(report["recommendations"], 1):
            priority_emoji = {"critical": "🚨", "high": "⚠️", "medium": "📋", "low": "💡"}
            emoji = priority_emoji.get(rec["priority"], "📋")
            print(f"   {i}. {emoji} {rec['description']} (Priority: {rec['priority']})")
    
    return 0 if critical_issues == 0 else 1

if __name__ == "__main__":
    exit(main())
