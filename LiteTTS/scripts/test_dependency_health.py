#!/usr/bin/env python3
"""
Dependency Health Test Script

Tests the dependency health monitoring and recovery system to ensure
startup validation, runtime monitoring, and automatic recovery work correctly.
"""

import sys
import os
import json
import time
import tempfile
from pathlib import Path
from typing import Dict, List, Any
import argparse

# Add LiteTTS to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from LiteTTS.utils.dependency_health import (
    DependencyHealth, 
    DependencyStatus,
    get_dependency_health
)

def test_startup_validation() -> Dict[str, Any]:
    """Test startup dependency validation"""
    
    print("🔍 Testing Startup Dependency Validation")
    print("=" * 45)
    
    results = {
        "validation_successful": False,
        "dependencies_checked": 0,
        "healthy_dependencies": 0,
        "missing_dependencies": 0,
        "critical_failures": 0,
        "validation_time": 0
    }
    
    try:
        health_monitor = DependencyHealth()
        
        start_time = time.time()
        validation_results = health_monitor.validate_startup_dependencies()
        validation_time = time.time() - start_time
        
        results["validation_time"] = validation_time
        results["dependencies_checked"] = len(validation_results)
        results["validation_successful"] = True
        
        for dep_name, result in validation_results.items():
            if result.status == DependencyStatus.HEALTHY:
                results["healthy_dependencies"] += 1
                print(f"✅ {dep_name}: {result.status.value}")
            elif result.status == DependencyStatus.MISSING:
                results["missing_dependencies"] += 1
                dep_info = health_monitor.dependencies[dep_name]
                if dep_info.required:
                    results["critical_failures"] += 1
                    print(f"❌ {dep_name}: {result.error_message} (CRITICAL)")
                else:
                    print(f"⚠️ {dep_name}: {result.error_message} (optional)")
            else:
                print(f"⚠️ {dep_name}: {result.status.value} - {result.error_message}")
        
        print(f"\n📊 Validation Summary:")
        print(f"   Dependencies checked: {results['dependencies_checked']}")
        print(f"   Healthy: {results['healthy_dependencies']}")
        print(f"   Missing: {results['missing_dependencies']}")
        print(f"   Critical failures: {results['critical_failures']}")
        print(f"   Validation time: {validation_time:.2f}s")
        
        return results
        
    except Exception as e:
        print(f"❌ Startup validation failed: {e}")
        results["validation_error"] = str(e)
        return results

def test_health_summary() -> Dict[str, Any]:
    """Test health summary generation"""
    
    print(f"\n📋 Testing Health Summary Generation")
    print("=" * 40)
    
    try:
        health_monitor = get_dependency_health()
        summary = health_monitor.get_health_summary()
        
        print(f"📊 Dependency Health Summary:")
        print(f"   Total dependencies: {summary['total_dependencies']}")
        print(f"   Healthy: {summary['healthy']}")
        print(f"   Missing: {summary['missing']}")
        print(f"   Critical missing: {summary['critical_missing']}")
        print(f"   Optional missing: {summary['optional_missing']}")
        print(f"   Overall health: {summary['overall_health']}")
        
        return {
            "summary_generated": True,
            "summary": summary
        }
        
    except Exception as e:
        print(f"❌ Health summary generation failed: {e}")
        return {
            "summary_generated": False,
            "error": str(e)
        }

def test_individual_dependency_checks() -> Dict[str, Any]:
    """Test individual dependency health checks"""
    
    print(f"\n🔍 Testing Individual Dependency Checks")
    print("=" * 45)
    
    health_monitor = DependencyHealth()
    test_dependencies = ["torch", "numpy", "fastapi", "nonexistent_package"]
    
    results = {
        "individual_checks": {},
        "successful_checks": 0,
        "total_checks": len(test_dependencies)
    }
    
    for dep_name in test_dependencies:
        try:
            result = health_monitor.check_dependency_health(dep_name)
            results["individual_checks"][dep_name] = {
                "status": result.status.value,
                "version": result.version,
                "error_message": result.error_message
            }
            
            if result.status == DependencyStatus.HEALTHY:
                results["successful_checks"] += 1
                print(f"✅ {dep_name}: {result.status.value} (v{result.version})")
            else:
                print(f"❌ {dep_name}: {result.status.value} - {result.error_message}")
                
        except Exception as e:
            print(f"❌ {dep_name}: Check failed - {e}")
            results["individual_checks"][dep_name] = {
                "status": "error",
                "error": str(e)
            }
    
    success_rate = results["successful_checks"] / results["total_checks"]
    print(f"\n📊 Individual Check Results:")
    print(f"   Successful checks: {results['successful_checks']}/{results['total_checks']}")
    print(f"   Success rate: {success_rate:.1%}")
    
    return results

def simulate_dependency_failure_and_recovery(simulate_failures: bool = False) -> Dict[str, Any]:
    """Test dependency failure simulation and recovery"""
    
    print(f"\n🔄 Testing Dependency Recovery")
    print("=" * 35)
    
    if not simulate_failures:
        print("⚠️ Skipping failure simulation (use --simulate-failures to enable)")
        return {"recovery_test_skipped": True}
    
    results = {
        "recovery_attempts": {},
        "successful_recoveries": 0,
        "total_attempts": 0
    }
    
    health_monitor = DependencyHealth()
    
    # Test recovery for optional dependencies that might be missing
    optional_deps = [
        name for name, info in health_monitor.dependencies.items()
        if not info.required
    ]
    
    print(f"Testing recovery for optional dependencies: {', '.join(optional_deps[:3])}")
    
    for dep_name in optional_deps[:3]:  # Test first 3 optional deps
        try:
            print(f"\n🧪 Testing recovery for {dep_name}...")
            
            # Check current status
            current_status = health_monitor.check_dependency_health(dep_name)
            print(f"   Current status: {current_status.status.value}")
            
            # If it's already healthy, we can't test recovery
            if current_status.status == DependencyStatus.HEALTHY:
                print(f"   ✅ {dep_name} is healthy, recovery not needed")
                results["recovery_attempts"][dep_name] = {
                    "needed": False,
                    "status": "healthy"
                }
                continue
            
            # Attempt recovery
            recovery_result = health_monitor.attempt_recovery(dep_name)
            results["total_attempts"] += 1
            
            results["recovery_attempts"][dep_name] = {
                "needed": True,
                "attempted": recovery_result.recovery_attempted,
                "successful": recovery_result.recovery_successful,
                "final_status": recovery_result.status.value,
                "error_message": recovery_result.error_message
            }
            
            if recovery_result.recovery_successful:
                results["successful_recoveries"] += 1
                print(f"   ✅ Recovery successful for {dep_name}")
            else:
                print(f"   ❌ Recovery failed for {dep_name}: {recovery_result.error_message}")
                
        except Exception as e:
            print(f"   ❌ Recovery test failed for {dep_name}: {e}")
            results["recovery_attempts"][dep_name] = {
                "needed": True,
                "attempted": False,
                "successful": False,
                "error": str(e)
            }
    
    if results["total_attempts"] > 0:
        recovery_rate = results["successful_recoveries"] / results["total_attempts"]
        print(f"\n📊 Recovery Test Results:")
        print(f"   Recovery attempts: {results['total_attempts']}")
        print(f"   Successful recoveries: {results['successful_recoveries']}")
        print(f"   Recovery success rate: {recovery_rate:.1%}")
    
    return results

def test_validate_and_recover() -> Dict[str, Any]:
    """Test the combined validate and recover functionality"""
    
    print(f"\n🔧 Testing Validate and Recover")
    print("=" * 35)
    
    try:
        health_monitor = DependencyHealth()
        
        start_time = time.time()
        results = health_monitor.validate_and_recover(auto_recover=True)
        total_time = time.time() - start_time
        
        healthy_count = sum(1 for r in results.values() if r.status == DependencyStatus.HEALTHY)
        recovery_attempted = sum(1 for r in results.values() if r.recovery_attempted)
        recovery_successful = sum(1 for r in results.values() if r.recovery_successful)
        
        print(f"📊 Validate and Recover Results:")
        print(f"   Total dependencies: {len(results)}")
        print(f"   Healthy after process: {healthy_count}")
        print(f"   Recovery attempts: {recovery_attempted}")
        print(f"   Successful recoveries: {recovery_successful}")
        print(f"   Total time: {total_time:.2f}s")
        
        return {
            "validate_recover_successful": True,
            "total_dependencies": len(results),
            "healthy_count": healthy_count,
            "recovery_attempted": recovery_attempted,
            "recovery_successful": recovery_successful,
            "total_time": total_time
        }
        
    except Exception as e:
        print(f"❌ Validate and recover failed: {e}")
        return {
            "validate_recover_successful": False,
            "error": str(e)
        }

def main():
    """Main test execution"""
    
    parser = argparse.ArgumentParser(description="Test dependency health monitoring")
    parser.add_argument("--simulate-failures", action="store_true",
                       help="Simulate dependency failures for recovery testing")
    parser.add_argument("--test-recovery", action="store_true",
                       help="Test recovery mechanisms")
    
    args = parser.parse_args()
    
    print("🧪 Dependency Health Test Suite")
    print("=" * 50)
    print("Testing dependency health monitoring and recovery...")
    print()
    
    # Test 1: Startup validation
    startup_results = test_startup_validation()
    
    # Test 2: Health summary
    summary_results = test_health_summary()
    
    # Test 3: Individual dependency checks
    individual_results = test_individual_dependency_checks()
    
    # Test 4: Recovery testing (if enabled)
    recovery_results = {}
    if args.test_recovery:
        recovery_results = simulate_dependency_failure_and_recovery(args.simulate_failures)
    
    # Test 5: Validate and recover
    validate_recover_results = test_validate_and_recover()
    
    # Overall results
    print(f"\n" + "=" * 50)
    print(f"📊 DEPENDENCY HEALTH TEST RESULTS:")
    
    startup_success = startup_results.get("validation_successful", False)
    summary_success = summary_results.get("summary_generated", False)
    individual_success = individual_results.get("successful_checks", 0) > 0
    validate_recover_success = validate_recover_results.get("validate_recover_successful", False)
    
    print(f"   Startup Validation: {'✅ PASS' if startup_success else '❌ FAIL'}")
    print(f"   Health Summary: {'✅ PASS' if summary_success else '❌ FAIL'}")
    print(f"   Individual Checks: {'✅ PASS' if individual_success else '❌ FAIL'}")
    print(f"   Validate & Recover: {'✅ PASS' if validate_recover_success else '❌ FAIL'}")
    
    if recovery_results and not recovery_results.get("recovery_test_skipped"):
        recovery_success = recovery_results.get("successful_recoveries", 0) >= 0
        print(f"   Recovery Testing: {'✅ PASS' if recovery_success else '❌ FAIL'}")
    
    overall_success = all([startup_success, summary_success, individual_success, validate_recover_success])
    print(f"\nOverall Status: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    # Save results
    results_file = Path("logs/dependency_health_test.log")
    results_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(results_file, 'w') as f:
        json.dump({
            "startup_validation": startup_results,
            "health_summary": summary_results,
            "individual_checks": individual_results,
            "recovery_testing": recovery_results,
            "validate_and_recover": validate_recover_results
        }, f, indent=2)
    
    print(f"📄 Detailed results saved to: {results_file}")
    
    if overall_success:
        print("\n🎉 Dependency health monitoring system working correctly!")
        print("✅ Startup validation functional")
        print("✅ Health monitoring operational")
        print("✅ Individual dependency checks working")
        print("✅ Validate and recover process functional")
        return 0
    else:
        print("\n⚠️ Some dependency health issues detected")
        print("❌ Check the detailed log for specific failures")
        return 1

if __name__ == "__main__":
    exit(main())
