#!/usr/bin/env python3
"""
Comprehensive Audio Quality Test Runner
Executes the full audio quality testing suite with reporting and CI/CD integration
"""

import asyncio
import argparse
import logging
import sys
import json
from pathlib import Path
from typing import Optional

# Add LiteTTS to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from LiteTTS.testing.comprehensive_audio_quality_suite import ComprehensiveAudioQualityTestSuite, TestSuiteResults

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AudioQualityTestRunner:
    """Main test runner for comprehensive audio quality testing"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.test_suite = ComprehensiveAudioQualityTestSuite(config_path)
        
    async def run_full_test_suite(self) -> TestSuiteResults:
        """Run the complete audio quality test suite"""
        logger.info("🧪 Starting Comprehensive Audio Quality Test Suite")
        logger.info("=" * 60)
        
        try:
            # Check if TTS server is running
            await self._check_server_availability()
            
            # Run comprehensive tests
            results = await self.test_suite.run_comprehensive_test_suite()
            
            # Display results summary
            self._display_results_summary(results)
            
            # Handle CI/CD integration
            await self._handle_cicd_integration(results)
            
            return results
            
        except Exception as e:
            logger.error(f"Test suite failed: {e}")
            raise
    
    async def _check_server_availability(self):
        """Check if TTS server is available"""
        import aiohttp
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.test_suite.api_base_url}/health", timeout=5) as response:
                    if response.status == 200:
                        logger.info(f"✅ TTS server available at {self.test_suite.api_base_url}")
                    else:
                        raise Exception(f"TTS server returned status {response.status}")
        except Exception as e:
            logger.error(f"❌ TTS server not available: {e}")
            logger.error("Please ensure the TTS server is running before running tests")
            raise
    
    def _display_results_summary(self, results: TestSuiteResults):
        """Display test results summary"""
        logger.info("\n" + "=" * 60)
        logger.info("📊 TEST RESULTS SUMMARY")
        logger.info("=" * 60)
        
        # Overall metrics
        logger.info(f"🎯 Overall Score: {results.overall_score:.1f}%")
        logger.info(f"✅ Tests Passed: {results.passed_tests}/{results.total_tests}")
        logger.info(f"❌ Tests Failed: {results.failed_tests}")
        logger.info(f"⏭️  Tests Skipped: {results.skipped_tests}")
        logger.info(f"⏱️  Execution Time: {results.execution_time:.2f}s")
        
        # Regression check
        if results.regression_detected:
            logger.warning("⚠️  QUALITY REGRESSION DETECTED!")
        else:
            logger.info("✅ No quality regressions detected")
        
        # Category breakdown
        logger.info("\n📋 Category Results:")
        for category, category_result in results.category_results.items():
            total = category_result["total"]
            passed = category_result["passed"]
            failed = category_result["failed"]
            pass_rate = (passed / total * 100) if total > 0 else 0
            
            status_icon = "✅" if failed == 0 else "⚠️" if passed > failed else "❌"
            logger.info(f"  {status_icon} {category.title()}: {passed}/{total} ({pass_rate:.1f}%)")
            
            # Show average metrics if available
            if "avg_metrics" in category_result and category_result["avg_metrics"]:
                metrics = category_result["avg_metrics"]
                logger.info(f"    📈 Avg Metrics: RTF={metrics.get('rtf', 0):.3f}, "
                          f"WER={metrics.get('wer', 0):.3f}, "
                          f"MOS={metrics.get('mos_prediction', 0):.2f}")
        
        # Quality thresholds status
        logger.info("\n🎯 Quality Thresholds:")
        thresholds = self.test_suite.quality_thresholds
        logger.info(f"  • Min MOS Score: {thresholds.get('min_mos_score', 3.0)}")
        logger.info(f"  • Max WER: {thresholds.get('max_wer', 0.1)}")
        logger.info(f"  • Min Pronunciation Accuracy: {thresholds.get('min_pronunciation_accuracy', 0.9)}")
        logger.info(f"  • Max RTF: {thresholds.get('max_rtf', 0.25)}")
        logger.info(f"  • Min Prosody Score: {thresholds.get('min_prosody_score', 0.7)}")
    
    async def _handle_cicd_integration(self, results: TestSuiteResults):
        """Handle CI/CD integration and failure conditions"""
        config = self.test_suite.audio_config.get("integration", {})
        
        if config.get("ci_cd_enabled", False):
            logger.info("\n🔄 CI/CD Integration:")
            
            # Check if we should fail on regression
            if config.get("fail_on_regression", True) and results.regression_detected:
                logger.error("❌ Failing build due to quality regression")
                sys.exit(1)
            
            # Check overall pass rate
            pass_rate = results.passed_tests / results.total_tests if results.total_tests > 0 else 0
            min_pass_rate = config.get("min_pass_rate", 0.9)
            
            if pass_rate < min_pass_rate:
                logger.error(f"❌ Failing build due to low pass rate: {pass_rate:.2f} < {min_pass_rate}")
                sys.exit(1)
            
            logger.info("✅ CI/CD checks passed")
    
    async def run_category_tests(self, category: str) -> TestSuiteResults:
        """Run tests for a specific category only"""
        logger.info(f"🧪 Running {category} Audio Quality Tests")
        
        # This would be implemented to run only specific category tests
        # For now, run full suite and filter results
        results = await self.test_suite.run_comprehensive_test_suite()
        
        # Filter results to only include the specified category
        if category in results.category_results:
            category_result = results.category_results[category]
            filtered_results = TestSuiteResults(
                total_tests=category_result["total"],
                passed_tests=category_result["passed"],
                failed_tests=category_result["failed"],
                skipped_tests=category_result["skipped"],
                overall_score=category_result["passed"] / category_result["total"] * 100 if category_result["total"] > 0 else 0,
                category_results={category: category_result},
                performance_metrics={},
                quality_metrics={},
                regression_detected=False,
                execution_time=results.execution_time,
                timestamp=results.timestamp
            )
            return filtered_results
        else:
            logger.warning(f"Category '{category}' not found in test results")
            return results
    
    async def run_performance_validation(self) -> TestSuiteResults:
        """Run performance-focused validation tests"""
        logger.info("🚀 Running Performance Validation Tests")
        return await self.run_category_tests("performance")
    
    async def run_regression_tests(self) -> TestSuiteResults:
        """Run regression detection tests"""
        logger.info("🔍 Running Regression Detection Tests")
        
        results = await self.test_suite.run_comprehensive_test_suite()
        
        if results.regression_detected:
            logger.warning("⚠️  Quality regression detected!")
            # Generate detailed regression report
            await self._generate_regression_report(results)
        else:
            logger.info("✅ No regressions detected")
        
        return results
    
    async def _generate_regression_report(self, results: TestSuiteResults):
        """Generate detailed regression analysis report"""
        logger.info("📝 Generating regression analysis report...")
        
        # This would generate a detailed comparison with baseline
        # For now, just log the regression detection
        logger.info("Regression report would be generated here with detailed analysis")

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Comprehensive Audio Quality Test Runner")
    parser.add_argument("--config", "-c", help="Configuration file path")
    parser.add_argument("--category", help="Run tests for specific category only")
    parser.add_argument("--performance", action="store_true", help="Run performance validation tests")
    parser.add_argument("--regression", action="store_true", help="Run regression detection tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize test runner
    runner = AudioQualityTestRunner(args.config)
    
    try:
        # Run appropriate test suite
        if args.category:
            results = await runner.run_category_tests(args.category)
        elif args.performance:
            results = await runner.run_performance_validation()
        elif args.regression:
            results = await runner.run_regression_tests()
        else:
            results = await runner.run_full_test_suite()
        
        # Exit with appropriate code
        if results.failed_tests > 0:
            logger.warning(f"⚠️  {results.failed_tests} tests failed")
            sys.exit(1)
        else:
            logger.info("🎉 All tests passed!")
            sys.exit(0)
            
    except KeyboardInterrupt:
        logger.info("Test run interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Test run failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
