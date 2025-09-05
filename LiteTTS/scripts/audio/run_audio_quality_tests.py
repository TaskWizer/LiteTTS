#!/usr/bin/env python3
"""
Automated Audio Quality Testing Runner for Kokoro TTS API

This script runs comprehensive automated audio quality tests with integration
to our existing configuration validation and task management systems.
"""

import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from LiteTTS.testing.audio_quality_tester import AudioQualityTester, AudioTestCase
from LiteTTS.testing.espeak_integration_tests import EspeakIntegrationTestSuite

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AudioQualityTestRunner:
    """
    Main test runner for automated audio quality testing
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        # Use centralized config system with fallback to specified path
        if config_path is None:
            # Try to use centralized configuration
            try:
                from ...config import config as app_config
                self.config = app_config.to_dict() if hasattr(app_config, 'to_dict') else {}
                self.config_path = None  # Using centralized config
            except ImportError:
                # Fallback to default config file
                self.config_path = Path("config/settings.json") if Path("config/settings.json").exists() else Path("config.json")
                self.config = self._load_config()
        else:
            self.config_path = config_path
            self.config = self._load_config()
        
        # Initialize audio quality tester
        self.tester = AudioQualityTester(self.config)
        
        # Initialize test suites
        self.espeak_suite = EspeakIntegrationTestSuite()
        
        # Results storage
        self.results_dir = Path("test_results/audio_quality")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from config file with audio quality testing defaults
        """
        if self.config_path is None:
            return {}  # Already loaded from centralized config

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {self.config_path}, using defaults")
            config = {}
        
        # Add audio quality testing defaults if not present
        if "audio_quality_testing" not in config:
            config["audio_quality_testing"] = {
                "enabled": True,
                "api_base_url": "http://localhost:8354",
                "api_timeout": 30,
                "max_concurrent_tests": 3,
                "cache_enabled": True,
                "cache_dir": "cache/audio_quality",
                "quality_thresholds": {
                    "min_mos_score": 3.0,
                    "max_wer": 0.1,
                    "min_pronunciation_accuracy": 0.9,
                    "max_rtf": 0.25,
                    "min_prosody_score": 0.7
                },
                "asr_services": {
                    "enabled": False,  # Disabled by default
                    "deepgram": {
                        "enabled": False,
                        "api_key": "",
                        "model": "nova-2",
                        "language": "en-US"
                    },
                    "azure_speech": {
                        "enabled": False,
                        "subscription_key": "",
                        "region": "eastus"
                    },
                    "google_stt": {
                        "enabled": False,
                        "credentials_path": ""
                    }
                }
            }
        
        return config
    
    async def run_espeak_integration_tests(self, test_filter: str = "all") -> Dict[str, Any]:
        """
        Run eSpeak integration tests
        """
        logger.info("🎯 Running eSpeak Integration Tests")
        logger.info("=" * 50)
        
        # Get test cases based on filter
        if test_filter == "critical":
            test_cases = self.espeak_suite.get_critical_tests()
        elif test_filter == "symbols":
            test_cases = self.espeak_suite.get_symbol_processing_tests()
        elif test_filter == "regression":
            test_cases = self.espeak_suite.get_regression_tests()
        else:
            test_cases = self.espeak_suite.get_test_cases()
        
        logger.info(f"Running {len(test_cases)} test cases (filter: {test_filter})")
        
        # Run tests
        summary = await self.tester.run_test_suite(test_cases)
        
        # Generate report
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_path = self.results_dir / f"espeak_integration_report_{timestamp}.md"
        report_content = self.tester.generate_report(summary, report_path)
        
        logger.info(f"📊 Test Results Summary:")
        logger.info(f"   Total Tests: {summary['total_tests']}")
        logger.info(f"   Passed: {summary['passed_tests']}")
        logger.info(f"   Failed: {summary['failed_tests']}")
        logger.info(f"   Success Rate: {summary['success_rate']:.1%}")
        logger.info(f"   Quality Assessment: {summary['quality_assessment']}")
        logger.info(f"   Report saved: {report_path}")
        
        return summary
    
    async def run_configuration_impact_tests(self) -> Dict[str, Any]:
        """
        Test audio quality impact of different configuration settings
        """
        logger.info("🔧 Running Configuration Impact Tests")
        logger.info("=" * 50)
        
        # Test with beta features disabled (current state)
        logger.info("Testing with beta features disabled...")
        beta_disabled_summary = await self.run_espeak_integration_tests("critical")
        
        # Save baseline if this is the first run
        baseline_path = self.results_dir / "baseline_metrics.json"
        if not baseline_path.exists():
            self.tester.save_baseline_metrics(beta_disabled_summary, baseline_path)
            logger.info("✅ Baseline metrics saved")
        
        # Compare with baseline
        baseline_metrics = self.tester.load_baseline_metrics(baseline_path)
        if baseline_metrics:
            comparison = self._compare_with_baseline(beta_disabled_summary, baseline_metrics)
            logger.info(f"📈 Baseline Comparison: {comparison['status']}")
            
            if comparison['regressions']:
                logger.warning("⚠️  Detected regressions:")
                for regression in comparison['regressions']:
                    logger.warning(f"   - {regression}")
        
        return {
            "beta_disabled": beta_disabled_summary,
            "baseline_comparison": comparison if baseline_metrics else None
        }
    
    def _compare_with_baseline(self, current: Dict[str, Any], baseline: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare current results with baseline metrics
        """
        current_metrics = current.get("average_metrics", {})
        baseline_metrics = baseline.get("average_metrics", {})
        
        regressions = []
        improvements = []
        
        # Define regression thresholds (percentage change that indicates regression)
        regression_thresholds = {
            "mos_prediction": -0.1,  # 0.1 point decrease
            "wer": 0.02,  # 2% increase in error rate
            "pronunciation_accuracy": -0.05,  # 5% decrease
            "rtf": 0.05,  # 5% increase in processing time
            "prosody_score": -0.1  # 0.1 point decrease
        }
        
        for metric, current_value in current_metrics.items():
            if metric in baseline_metrics:
                baseline_value = baseline_metrics[metric]
                change = current_value - baseline_value
                
                if metric in regression_thresholds:
                    threshold = regression_thresholds[metric]
                    
                    if change < threshold:
                        regressions.append(f"{metric}: {current_value:.3f} vs {baseline_value:.3f} (change: {change:.3f})")
                    elif change > abs(threshold):
                        improvements.append(f"{metric}: {current_value:.3f} vs {baseline_value:.3f} (change: +{change:.3f})")
        
        status = "REGRESSION" if regressions else ("IMPROVEMENT" if improvements else "STABLE")
        
        return {
            "status": status,
            "regressions": regressions,
            "improvements": improvements,
            "current_quality": current.get("quality_assessment", "UNKNOWN"),
            "baseline_quality": baseline.get("quality_assessment", "UNKNOWN")
        }
    
    async def run_performance_validation(self) -> Dict[str, Any]:
        """
        Run performance validation tests
        """
        logger.info("⚡ Running Performance Validation Tests")
        logger.info("=" * 50)
        
        # Create performance-focused test cases
        performance_tests = [
            AudioTestCase(
                test_id="perf_short_text",
                input_text="Hello?",
                expected_transcription="hello question mark",
                test_category="performance",
                description="Short text performance test",
                max_rtf=0.15,  # Stricter RTF for short text
                priority="critical"
            ),
            AudioTestCase(
                test_id="perf_medium_text",
                input_text="What time is it? The cost is $50.99. Use the * symbol.",
                expected_transcription="what time is it question mark the cost is fifty dollars and ninety nine cents use the asterisk symbol",
                test_category="performance",
                description="Medium text performance test",
                max_rtf=0.2,
                priority="high"
            ),
            AudioTestCase(
                test_id="perf_long_text",
                input_text="This is a comprehensive test of the TTS system with multiple symbols and processing requirements. What is the current time? The total cost is $1,234.56. Please use the * symbol for multiplication. Email us at support@example.com for assistance!",
                expected_transcription="this is a comprehensive test of the tts system with multiple symbols and processing requirements what is the current time question mark the total cost is one thousand two hundred thirty four dollars and fifty six cents please use the asterisk symbol for multiplication email us at support example com for assistance exclamation mark",
                test_category="performance",
                description="Long text performance test",
                max_rtf=0.25,
                priority="normal"
            )
        ]
        
        # Run performance tests
        summary = await self.tester.run_test_suite(performance_tests)
        
        # Analyze performance metrics
        avg_metrics = summary.get("average_metrics", {})
        performance_assessment = {
            "rtf_performance": "EXCELLENT" if avg_metrics.get("rtf", 1.0) < 0.15 else 
                              "GOOD" if avg_metrics.get("rtf", 1.0) < 0.2 else
                              "ACCEPTABLE" if avg_metrics.get("rtf", 1.0) < 0.25 else "POOR",
            "processing_time": avg_metrics.get("processing_time", 0),
            "average_rtf": avg_metrics.get("rtf", 0),
            "meets_targets": avg_metrics.get("rtf", 1.0) < 0.25
        }
        
        logger.info(f"📊 Performance Assessment: {performance_assessment['rtf_performance']}")
        logger.info(f"   Average RTF: {performance_assessment['average_rtf']:.3f}")
        logger.info(f"   Meets Targets: {performance_assessment['meets_targets']}")
        
        return {
            "summary": summary,
            "performance_assessment": performance_assessment
        }
    
    async def run_comprehensive_test_suite(self) -> Dict[str, Any]:
        """
        Run the complete comprehensive test suite
        """
        logger.info("🚀 Running Comprehensive Audio Quality Test Suite")
        logger.info("=" * 60)
        
        start_time = time.perf_counter()
        
        # Run all test categories
        results = {}
        
        try:
            # 1. eSpeak Integration Tests
            results["espeak_integration"] = await self.run_espeak_integration_tests("all")
            
            # 2. Configuration Impact Tests
            results["configuration_impact"] = await self.run_configuration_impact_tests()
            
            # 3. Performance Validation
            results["performance_validation"] = await self.run_performance_validation()
            
            # Calculate overall results
            total_time = time.perf_counter() - start_time
            overall_assessment = self._calculate_overall_assessment(results)
            
            results["overall"] = {
                "total_time": total_time,
                "assessment": overall_assessment,
                "timestamp": time.time()
            }
            
            # Save comprehensive results
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            results_path = self.results_dir / f"comprehensive_results_{timestamp}.json"
            with open(results_path, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            logger.info(f"\n🎉 Comprehensive Test Suite Completed!")
            logger.info(f"   Total Time: {total_time:.2f}s")
            logger.info(f"   Overall Assessment: {overall_assessment}")
            logger.info(f"   Results saved: {results_path}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Comprehensive test suite failed: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e), "results": results}
    
    def _calculate_overall_assessment(self, results: Dict[str, Any]) -> str:
        """
        Calculate overall assessment from all test results
        """
        assessments = []
        
        # Collect quality assessments from different test categories
        if "espeak_integration" in results:
            assessments.append(results["espeak_integration"].get("quality_assessment", "UNKNOWN"))
        
        if "performance_validation" in results:
            perf_summary = results["performance_validation"].get("summary", {})
            assessments.append(perf_summary.get("quality_assessment", "UNKNOWN"))
        
        # Determine overall assessment
        if not assessments:
            return "UNKNOWN"
        
        if all(a in ["EXCELLENT", "GOOD"] for a in assessments):
            return "EXCELLENT"
        elif all(a in ["EXCELLENT", "GOOD", "ACCEPTABLE"] for a in assessments):
            return "GOOD"
        elif any(a == "POOR" for a in assessments):
            return "POOR"
        else:
            return "ACCEPTABLE"


async def main():
    """
    Main function for running audio quality tests
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Automated Audio Quality Testing for Kokoro TTS")
    parser.add_argument("--test-type", choices=["espeak", "config", "performance", "comprehensive"], 
                       default="comprehensive", help="Type of tests to run")
    parser.add_argument("--filter", choices=["all", "critical", "symbols", "regression"], 
                       default="all", help="Test filter for eSpeak tests")
    parser.add_argument("--config", type=Path, help="Path to config.json file")
    
    args = parser.parse_args()
    
    # Initialize test runner
    runner = AudioQualityTestRunner(args.config)
    
    # Run tests based on type
    if args.test_type == "espeak":
        results = await runner.run_espeak_integration_tests(args.filter)
    elif args.test_type == "config":
        results = await runner.run_configuration_impact_tests()
    elif args.test_type == "performance":
        results = await runner.run_performance_validation()
    else:  # comprehensive
        results = await runner.run_comprehensive_test_suite()
    
    # Return appropriate exit code
    if "error" in results:
        return 1
    
    # Check if tests passed
    if args.test_type == "comprehensive":
        overall_assessment = results.get("overall", {}).get("assessment", "UNKNOWN")
        return 0 if overall_assessment in ["EXCELLENT", "GOOD", "ACCEPTABLE"] else 1
    else:
        quality_assessment = results.get("quality_assessment", "UNKNOWN")
        return 0 if quality_assessment in ["EXCELLENT", "GOOD", "ACCEPTABLE"] else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
