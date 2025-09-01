#!/usr/bin/env python3
"""
Performance Regression Test Runner
Simple script to run performance regression tests and generate reports
"""

import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from LiteTTS.tests.performance_regression_framework import PerformanceRegressionTester

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Run performance regression tests"""
    print("🚀 Performance Regression Test Runner")
    print("=" * 50)
    
    try:
        # Initialize tester
        tester = PerformanceRegressionTester()
        
        # Check if baseline exists
        baseline_exists = tester.baseline_file.exists()
        
        if not baseline_exists:
            print("📊 No baseline found. Creating initial baseline...")
            result = tester.run_performance_test_suite(save_as_baseline=True)
            print("✅ Baseline created successfully!")
        else:
            print("📈 Running regression tests against baseline...")
            result = tester.run_performance_test_suite(save_as_baseline=False)
        
        # Generate detailed report
        report = tester.generate_performance_report(result)
        
        # Print summary
        print(f"\n📋 Test Summary:")
        print(f"   Total Tests: {result.total_tests}")
        print(f"   Passed: {result.passed_tests}")
        print(f"   Failed: {result.failed_tests}")
        print(f"   Success Rate: {(result.passed_tests/result.total_tests*100):.1f}%")
        
        print(f"\n⚡ Performance Metrics:")
        print(f"   Average RTF: {result.average_rtf:.3f}")
        print(f"   Average Processing Time: {result.average_processing_time:.3f}s")
        print(f"   Memory Peak: {result.memory_peak_mb:.1f}MB")
        print(f"   CPU Peak: {result.cpu_peak_percent:.1f}%")
        
        if baseline_exists:
            print(f"\n📊 Baseline Comparison:")
            baseline_comp = result.baseline_comparison
            if 'rtf_change_percent' in baseline_comp:
                rtf_change = baseline_comp['rtf_change_percent']
                rtf_symbol = "📈" if rtf_change > 0 else "📉" if rtf_change < 0 else "➡️"
                print(f"   RTF Change: {rtf_symbol} {rtf_change:+.1f}%")
            
            if 'memory_change_percent' in baseline_comp:
                mem_change = baseline_comp['memory_change_percent']
                mem_symbol = "📈" if mem_change > 0 else "📉" if mem_change < 0 else "➡️"
                print(f"   Memory Change: {mem_symbol} {mem_change:+.1f}%")
        
        # Performance status
        status = report['analysis']['performance_status']
        status_symbols = {
            'PASSED': '✅',
            'FAILED': '❌',
            'REGRESSION_DETECTED': '⚠️',
            'RTF_THRESHOLD_EXCEEDED': '🐌',
            'MEMORY_THRESHOLD_EXCEEDED': '💾'
        }
        
        print(f"\n🎯 Performance Status: {status_symbols.get(status, '❓')} {status}")
        
        # Recommendations
        recommendations = report['analysis']['recommendations']
        if recommendations:
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
        
        # Files generated
        print(f"\n📁 Generated Files:")
        print(f"   📊 Performance Report: performance_report.json")
        if tester.baseline_file.exists():
            print(f"   📈 Baseline Data: {tester.baseline_file}")
        
        # Exit status
        if status == 'PASSED':
            print(f"\n🎉 All tests passed! Performance is within acceptable limits.")
            return True
        elif status == 'REGRESSION_DETECTED':
            print(f"\n⚠️  Performance regression detected. Review recent changes.")
            return False
        elif status == 'FAILED':
            print(f"\n❌ Some tests failed. Check logs for details.")
            return False
        else:
            print(f"\n⚠️  Performance issues detected. See recommendations above.")
            return False
            
    except Exception as e:
        logger.error(f"Performance testing failed: {e}")
        print(f"\n❌ Testing failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
