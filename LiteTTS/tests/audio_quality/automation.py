#!/usr/bin/env python3
"""
Automated Test Execution System for Audio Quality Validation
Provides configurable thresholds, detailed reporting, and CI/CD integration
"""

import json
import time
import logging
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import asdict
import subprocess

from .framework import QualityThresholds
from .test_cases import AudioQualityTestSuite, TestResult

logger = logging.getLogger(__name__)

class AutomatedTestRunner:
    """Automated test execution with configurable thresholds and reporting"""
    
    def __init__(self, config_file: Optional[Path] = None):
        self.config = self._load_config(config_file)
        self.thresholds = QualityThresholds(**self.config.get("quality_thresholds", {}))
        self.test_suite = AudioQualityTestSuite(
            api_base_url=self.config.get("api_base_url", "http://localhost:8354"),
            thresholds=self.thresholds
        )
        self.results_dir = Path(self.config.get("results_dir", "test_results/audio_quality"))
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
    def _load_config(self, config_file: Optional[Path]) -> Dict[str, Any]:
        """Load test configuration"""
        default_config = {
            "api_base_url": "http://localhost:8354",
            "api_timeout": 30,
            "max_concurrent_tests": 3,
            "results_dir": "test_results/audio_quality",
            "quality_thresholds": {
                "min_mos_score": 3.0,
                "max_wer": 0.1,
                "min_pronunciation_accuracy": 0.9,
                "max_rtf": 0.25,
                "min_prosody_score": 0.7
            },
            "test_categories": {
                "short_text": {"enabled": True, "priority": "critical"},
                "long_text": {"enabled": True, "priority": "high"},
                "symbols": {"enabled": True, "priority": "high"},
                "contractions": {"enabled": True, "priority": "high"},
                "numbers": {"enabled": True, "priority": "medium"},
                "prosody": {"enabled": True, "priority": "high"},
                "edge_cases": {"enabled": True, "priority": "low"}
            },
            "model_types": ["gguf", "onnx"],
            "reporting": {
                "save_audio_samples": False,
                "generate_detailed_reports": True,
                "include_baseline_comparison": True,
                "alert_on_regression": True
            },
            "ci_cd": {
                "fail_on_regression": True,
                "baseline_update_threshold": 0.05,
                "performance_monitoring": True
            }
        }
        
        if config_file and config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
                logger.info(f"Loaded configuration from {config_file}")
            except Exception as e:
                logger.warning(f"Failed to load config file {config_file}: {e}")
                logger.info("Using default configuration")
        
        return default_config
    
    def run_automated_tests(self, categories: Optional[List[str]] = None,
                           model_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run automated test suite with full reporting"""
        logger.info("Starting automated audio quality test suite")
        
        # Filter categories based on configuration
        if categories is None:
            categories = [cat for cat, config in self.config["test_categories"].items() 
                         if config.get("enabled", True)]
        
        if model_types is None:
            model_types = self.config.get("model_types", ["gguf", "onnx"])
        
        # Check API availability
        if not self._check_api_availability():
            raise RuntimeError("TTS API is not available")
        
        # Run test suite
        start_time = time.time()
        results = self.test_suite.run_full_suite(model_types, categories)
        execution_time = time.time() - start_time
        
        # Generate comprehensive report
        report = self._generate_comprehensive_report(results, execution_time)
        
        # Save results
        self._save_results(report)
        
        # Check for regressions
        regression_detected = self._check_for_regressions(report)
        
        # Generate alerts if needed
        if regression_detected and self.config["reporting"]["alert_on_regression"]:
            self._generate_alerts(report)
        
        # CI/CD integration
        if self.config["ci_cd"]["fail_on_regression"] and regression_detected:
            logger.error("Regression detected - failing CI/CD pipeline")
            sys.exit(1)
        
        logger.info(f"Automated test suite completed in {execution_time:.2f} seconds")
        return report
    
    def _check_api_availability(self) -> bool:
        """Check if TTS API is available"""
        try:
            import requests
            url = f"{self.config['api_base_url']}/health"
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"API availability check failed: {e}")
            return False
    
    def _generate_comprehensive_report(self, results: Dict[str, List], 
                                     execution_time: float) -> Dict[str, Any]:
        """Generate comprehensive test report with analysis"""
        report = self.test_suite.generate_report()
        
        # Add execution metadata
        report["execution_metadata"] = {
            "execution_time_seconds": execution_time,
            "configuration": self.config,
            "environment": self._get_environment_info()
        }
        
        # Add performance analysis
        report["performance_analysis"] = self._analyze_performance(results)
        
        # Add quality analysis
        report["quality_analysis"] = self._analyze_quality(results)
        
        # Add regression analysis
        report["regression_analysis"] = self._analyze_regressions(results)
        
        return report
    
    def _get_environment_info(self) -> Dict[str, Any]:
        """Get environment information for reporting"""
        try:
            import platform
            import psutil
            
            return {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "cpu_count": psutil.cpu_count(),
                "memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception:
            return {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}
    
    def _analyze_performance(self, results: Dict[str, List]) -> Dict[str, Any]:
        """Analyze performance metrics across all tests"""
        analysis = {}
        
        for model_type, test_results in results.items():
            rtf_values = [r.performance_metrics.rtf for r in test_results if r.performance_metrics.rtf > 0]
            generation_times = [r.performance_metrics.generation_time_ms for r in test_results]
            
            analysis[model_type] = {
                "rtf_statistics": {
                    "mean": sum(rtf_values) / len(rtf_values) if rtf_values else 0,
                    "max": max(rtf_values) if rtf_values else 0,
                    "min": min(rtf_values) if rtf_values else 0,
                    "target_compliance": sum(1 for rtf in rtf_values if rtf <= self.thresholds.max_rtf) / len(rtf_values) if rtf_values else 0
                },
                "generation_time_statistics": {
                    "mean_ms": sum(generation_times) / len(generation_times) if generation_times else 0,
                    "max_ms": max(generation_times) if generation_times else 0,
                    "min_ms": min(generation_times) if generation_times else 0
                }
            }
        
        return analysis
    
    def _analyze_quality(self, results: Dict[str, List]) -> Dict[str, Any]:
        """Analyze quality metrics across all tests"""
        analysis = {}
        
        for model_type, test_results in results.items():
            mos_scores = [r.quality_metrics.mos_prediction for r in test_results]
            wer_scores = [r.content_metrics.wer_score for r in test_results]
            prosody_scores = [r.quality_metrics.prosody_score for r in test_results]
            
            analysis[model_type] = {
                "mos_statistics": {
                    "mean": sum(mos_scores) / len(mos_scores) if mos_scores else 0,
                    "min": min(mos_scores) if mos_scores else 0,
                    "target_compliance": sum(1 for mos in mos_scores if mos >= self.thresholds.min_mos_score) / len(mos_scores) if mos_scores else 0
                },
                "wer_statistics": {
                    "mean": sum(wer_scores) / len(wer_scores) if wer_scores else 0,
                    "max": max(wer_scores) if wer_scores else 0,
                    "target_compliance": sum(1 for wer in wer_scores if wer <= self.thresholds.max_wer) / len(wer_scores) if wer_scores else 0
                },
                "prosody_statistics": {
                    "mean": sum(prosody_scores) / len(prosody_scores) if prosody_scores else 0,
                    "min": min(prosody_scores) if prosody_scores else 0,
                    "target_compliance": sum(1 for ps in prosody_scores if ps >= self.thresholds.min_prosody_score) / len(prosody_scores) if prosody_scores else 0
                }
            }
        
        return analysis
    
    def _analyze_regressions(self, results: Dict[str, List]) -> Dict[str, Any]:
        """Analyze for performance and quality regressions"""
        # Load baseline if available
        baseline_file = self.results_dir / "baseline_results.json"
        if not baseline_file.exists():
            return {"baseline_available": False, "message": "No baseline available for regression analysis"}
        
        try:
            with open(baseline_file, 'r') as f:
                baseline = json.load(f)
            
            regression_analysis = {"baseline_available": True, "regressions": []}
            
            for model_type, test_results in results.items():
                if model_type not in baseline.get("summary", {}):
                    continue
                
                current_summary = self._calculate_summary_stats(test_results)
                baseline_summary = baseline["summary"][model_type]
                
                # Check for regressions
                rtf_regression = current_summary["average_rtf"] > baseline_summary["average_rtf"] * 1.1
                score_regression = current_summary["average_score"] < baseline_summary["average_score"] * 0.95
                pass_rate_regression = current_summary["pass_rate"] < baseline_summary["pass_rate"] * 0.9
                
                if rtf_regression or score_regression or pass_rate_regression:
                    regression_analysis["regressions"].append({
                        "model_type": model_type,
                        "rtf_regression": rtf_regression,
                        "score_regression": score_regression,
                        "pass_rate_regression": pass_rate_regression,
                        "current_metrics": current_summary,
                        "baseline_metrics": baseline_summary
                    })
            
            return regression_analysis
            
        except Exception as e:
            logger.error(f"Regression analysis failed: {e}")
            return {"baseline_available": False, "error": str(e)}
    
    def _calculate_summary_stats(self, test_results: List) -> Dict[str, float]:
        """Calculate summary statistics for a set of test results"""
        if not test_results:
            return {"average_rtf": 0, "average_score": 0, "pass_rate": 0}
        
        rtf_values = [r.performance_metrics.rtf for r in test_results if r.performance_metrics.rtf > 0]
        scores = [r.score for r in test_results]
        passed = sum(1 for r in test_results if r.overall_result == TestResult.PASS)
        
        return {
            "average_rtf": sum(rtf_values) / len(rtf_values) if rtf_values else 0,
            "average_score": sum(scores) / len(scores) if scores else 0,
            "pass_rate": passed / len(test_results)
        }
    
    def _check_for_regressions(self, report: Dict[str, Any]) -> bool:
        """Check if any regressions were detected"""
        regression_analysis = report.get("regression_analysis", {})
        return len(regression_analysis.get("regressions", [])) > 0
    
    def _save_results(self, report: Dict[str, Any]):
        """Save test results and reports"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        # Save detailed report
        report_file = self.results_dir / f"audio_quality_report_{timestamp}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        logger.info(f"Detailed report saved to {report_file}")
        
        # Save summary report
        summary_file = self.results_dir / f"summary_{timestamp}.json"
        summary = {
            "timestamp": report["timestamp"],
            "summary": report["summary"],
            "performance_analysis": report["performance_analysis"],
            "quality_analysis": report["quality_analysis"]
        }
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        # Update baseline if this is a good run
        if self._should_update_baseline(report):
            baseline_file = self.results_dir / "baseline_results.json"
            with open(baseline_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            logger.info("Updated baseline results")
    
    def _should_update_baseline(self, report: Dict[str, Any]) -> bool:
        """Determine if baseline should be updated"""
        # Update baseline if overall performance is good and no major issues
        for model_summary in report["summary"].values():
            if model_summary["pass_rate"] < 0.8 or model_summary["average_score"] < 0.7:
                return False
        return True
    
    def _generate_alerts(self, report: Dict[str, Any]):
        """Generate alerts for regressions or failures"""
        regressions = report.get("regression_analysis", {}).get("regressions", [])
        
        if regressions:
            alert_message = f"Audio Quality Regression Detected!\n\n"
            for regression in regressions:
                alert_message += f"Model: {regression['model_type']}\n"
                if regression['rtf_regression']:
                    alert_message += "- RTF performance regression\n"
                if regression['score_regression']:
                    alert_message += "- Quality score regression\n"
                if regression['pass_rate_regression']:
                    alert_message += "- Pass rate regression\n"
                alert_message += "\n"
            
            logger.warning(alert_message)
            
            # Save alert to file
            alert_file = self.results_dir / f"alert_{time.strftime('%Y%m%d_%H%M%S')}.txt"
            with open(alert_file, 'w') as f:
                f.write(alert_message)
    
    def cleanup(self):
        """Clean up test resources"""
        self.test_suite.cleanup()

def main():
    """Command-line interface for automated testing"""
    parser = argparse.ArgumentParser(description="Automated Audio Quality Testing")
    parser.add_argument("--config", type=Path, help="Configuration file path")
    parser.add_argument("--categories", nargs="+", help="Test categories to run")
    parser.add_argument("--models", nargs="+", help="Model types to test")
    parser.add_argument("--output", type=Path, help="Output directory")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Initialize test runner
        runner = AutomatedTestRunner(args.config)
        
        # Override output directory if specified
        if args.output:
            runner.results_dir = args.output
            runner.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Run tests
        report = runner.run_automated_tests(args.categories, args.models)
        
        # Print summary
        print("\n=== Audio Quality Test Summary ===")
        for model_type, summary in report["summary"].items():
            print(f"\n{model_type.upper()} Model:")
            print(f"  Tests: {summary['total_tests']}")
            print(f"  Passed: {summary['passed']} ({summary['pass_rate']:.1%})")
            print(f"  Failed: {summary['failed']}")
            print(f"  Average Score: {summary['average_score']:.3f}")
            print(f"  Average RTF: {summary['average_rtf']:.3f}")
        
        # Check for regressions
        regressions = report.get("regression_analysis", {}).get("regressions", [])
        if regressions:
            print(f"\n⚠️  {len(regressions)} regression(s) detected!")
            sys.exit(1)
        else:
            print("\n✅ All tests passed - no regressions detected")
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        sys.exit(1)
    finally:
        if 'runner' in locals():
            runner.cleanup()

if __name__ == "__main__":
    main()
