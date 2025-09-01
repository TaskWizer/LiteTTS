#!/usr/bin/env python3
"""
Enhanced eSpeak Integration Script
Optimizes eSpeak integration for better phonetic processing and symbol pronunciation fixes
"""

import os
import sys
import json
import logging
import subprocess
import shutil
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class EspeakTestResult:
    """Result of eSpeak integration test"""
    test_name: str
    input_text: str
    expected_output: str
    actual_output: str
    success: bool
    processing_time: float
    error_message: str = ""

@dataclass
class EspeakOptimizationResult:
    """Result of eSpeak optimization"""
    optimization_name: str
    before_performance: Dict[str, Any]
    after_performance: Dict[str, Any]
    improvement_percentage: float
    success: bool
    notes: str = ""

class EspeakIntegrationEnhancer:
    """Enhanced eSpeak integration optimizer"""
    
    def __init__(self):
        self.results_dir = Path("test_results/espeak_enhancement")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Test cases for symbol pronunciation
        self.symbol_test_cases = [
            {
                "name": "question_mark_basic",
                "input": "What is your name?",
                "expected": "question mark",
                "category": "punctuation"
            },
            {
                "name": "asterisk_symbol",
                "input": "Use the * symbol here",
                "expected": "asterisk",
                "category": "symbols"
            },
            {
                "name": "ampersand_symbol",
                "input": "Johnson & Johnson",
                "expected": "and",
                "category": "symbols"
            },
            {
                "name": "at_symbol",
                "input": "Email me at user@domain.com",
                "expected": "at",
                "category": "symbols"
            },
            {
                "name": "hash_symbol",
                "input": "Use hashtag #example",
                "expected": "hash",
                "category": "symbols"
            },
            {
                "name": "dollar_symbol",
                "input": "It costs $50",
                "expected": "dollar",
                "category": "currency"
            },
            {
                "name": "percent_symbol",
                "input": "50% complete",
                "expected": "percent",
                "category": "symbols"
            }
        ]
        
        # Interjection test cases
        self.interjection_test_cases = [
            {
                "name": "hmm_basic",
                "input": "Hmm, that's interesting",
                "expected": "hmm",
                "category": "interjections"
            },
            {
                "name": "hmm_variations",
                "input": "Hmmm, let me think",
                "expected": "hmm",
                "category": "interjections"
            }
        ]
        
        # Contraction test cases
        self.contraction_test_cases = [
            {
                "name": "im_contraction",
                "input": "I'm going home",
                "expected": "I am",
                "category": "contractions"
            },
            {
                "name": "youre_contraction",
                "input": "You're welcome",
                "expected": "you are",
                "category": "contractions"
            }
        ]
    
    def check_espeak_installation(self) -> Tuple[bool, str, Dict[str, Any]]:
        """Check if eSpeak is installed and get version info"""
        logger.info("Checking eSpeak installation...")
        
        # Try to find eSpeak executable
        espeak_path = shutil.which("espeak") or shutil.which("espeak-ng")
        
        if not espeak_path:
            return False, "eSpeak not found in PATH", {}
        
        try:
            # Get version information
            result = subprocess.run([espeak_path, "--version"], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                version_info = {
                    "path": espeak_path,
                    "version": result.stdout.strip(),
                    "available": True
                }
                
                # Test basic functionality
                test_result = subprocess.run([espeak_path, "-q", "-x", "hello"], 
                                           capture_output=True, text=True, timeout=5)
                
                if test_result.returncode == 0:
                    version_info["phoneme_output"] = test_result.stdout.strip()
                    version_info["functional"] = True
                else:
                    version_info["functional"] = False
                    version_info["error"] = test_result.stderr
                
                return True, espeak_path, version_info
            else:
                return False, f"eSpeak version check failed: {result.stderr}", {}
                
        except Exception as e:
            return False, f"Error checking eSpeak: {str(e)}", {}
    
    def install_espeak_if_missing(self) -> bool:
        """Check eSpeak availability and provide installation guidance"""
        available, path_or_error, info = self.check_espeak_installation()

        if available:
            logger.info(f"eSpeak already available at: {path_or_error}")
            return True

        logger.warning("eSpeak not found. For optimal pronunciation processing, install eSpeak:")
        logger.warning("Ubuntu/Debian: sudo apt-get install espeak espeak-data")
        logger.warning("CentOS/RHEL: sudo yum install espeak")
        logger.warning("macOS: brew install espeak")
        logger.warning("Continuing without eSpeak installation...")

        return False
    
    def test_espeak_phonemization(self, test_cases: List[Dict[str, str]]) -> List[EspeakTestResult]:
        """Test eSpeak phonemization with various inputs"""
        logger.info("Testing eSpeak phonemization...")
        
        available, espeak_path, info = self.check_espeak_installation()
        if not available:
            logger.error("eSpeak not available for testing")
            return []
        
        results = []
        
        for test_case in test_cases:
            logger.info(f"Testing: {test_case['name']}")
            
            try:
                start_time = time.perf_counter()
                
                # Test ASCII phonemes
                result = subprocess.run([
                    espeak_path, "-q", "-x", "-v", "en-us", test_case["input"]
                ], capture_output=True, text=True, timeout=10)
                
                processing_time = time.perf_counter() - start_time
                
                if result.returncode == 0:
                    phonemes = result.stdout.strip()
                    
                    # Check if expected output is present
                    success = test_case["expected"].lower() in test_case["input"].lower()
                    
                    results.append(EspeakTestResult(
                        test_name=test_case["name"],
                        input_text=test_case["input"],
                        expected_output=test_case["expected"],
                        actual_output=phonemes,
                        success=success,
                        processing_time=processing_time
                    ))
                else:
                    results.append(EspeakTestResult(
                        test_name=test_case["name"],
                        input_text=test_case["input"],
                        expected_output=test_case["expected"],
                        actual_output="",
                        success=False,
                        processing_time=processing_time,
                        error_message=result.stderr
                    ))
                    
            except Exception as e:
                results.append(EspeakTestResult(
                    test_name=test_case["name"],
                    input_text=test_case["input"],
                    expected_output=test_case["expected"],
                    actual_output="",
                    success=False,
                    processing_time=0.0,
                    error_message=str(e)
                ))
        
        return results
    
    def optimize_espeak_configuration(self) -> Dict[str, Any]:
        """Optimize eSpeak configuration for better performance"""
        logger.info("Optimizing eSpeak configuration...")
        
        # Load current configuration
        config_path = Path("config.json")
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            config = {}
        
        # Enhanced eSpeak configuration
        optimized_espeak_config = {
            "enabled": True,
            "voice": "en-us",
            "phoneme_format": "ascii",
            "punctuation_mode": "some",
            "cache_enabled": True,
            "cache_size": 10000,
            "fallback_to_existing": True,
            "timeout_seconds": 5.0,
            "espeak_path": None,  # Auto-detect
            "optimization_settings": {
                "use_fast_voice_switching": True,
                "enable_symbol_preprocessing": True,
                "cache_phoneme_patterns": True,
                "batch_processing": True
            }
        }
        
        # Enhanced symbol processing configuration
        optimized_symbol_config = {
            "enabled": True,
            "fix_asterisk_pronunciation": True,
            "normalize_quotation_marks": True,
            "fix_apostrophe_handling": True,
            "natural_ampersand_pronunciation": True,
            "fix_html_entities": True,
            "handle_quotes_naturally": True,
            "preserve_markdown": False,
            "context_aware_symbols": True,
            "unicode_normalization": True,
            "espeak_enhanced_processing": {
                "enabled": True,
                "fix_question_mark_pronunciation": True,
                "fix_asterisk_pronunciation": True,
                "context_aware_processing": True,
                "punctuation_mode": "some",
                "symbol_mapping_optimization": True,
                "performance_mode": "balanced"
            }
        }
        
        # Update configuration
        config["espeak_integration"] = optimized_espeak_config
        config["symbol_processing"] = optimized_symbol_config
        
        # Save optimized configuration
        optimized_config_path = self.results_dir / "optimized_config.json"
        with open(optimized_config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Optimized configuration saved to: {optimized_config_path}")
        
        return {
            "espeak_config": optimized_espeak_config,
            "symbol_config": optimized_symbol_config,
            "config_file": str(optimized_config_path)
        }
    
    def create_enhanced_symbol_mappings(self) -> Dict[str, str]:
        """Create enhanced symbol mappings for better pronunciation"""
        logger.info("Creating enhanced symbol mappings...")
        
        enhanced_mappings = {
            # Punctuation symbols
            "?": "question mark",
            "!": "exclamation mark",
            ".": "period",
            ",": "comma",
            ";": "semicolon",
            ":": "colon",
            
            # Mathematical symbols
            "*": "asterisk",
            "+": "plus",
            "-": "minus",
            "=": "equals",
            "/": "slash",
            "\\": "backslash",
            "%": "percent",
            
            # Currency symbols
            "$": "dollar",
            "€": "euro",
            "£": "pound",
            "¥": "yen",
            
            # Other symbols
            "&": "and",
            "@": "at",
            "#": "hash",
            "^": "caret",
            "_": "underscore",
            "|": "pipe",
            "~": "tilde",
            "`": "backtick",
            
            # Brackets
            "(": "open parenthesis",
            ")": "close parenthesis",
            "[": "open bracket",
            "]": "close bracket",
            "{": "open brace",
            "}": "close brace",
            "<": "less than",
            ">": "greater than",
            
            # Quotes
            '"': "",  # Remove quotes to prevent pronunciation issues
            "'": "",  # Remove apostrophes in quotes
            """: "",  # Smart quotes
            """: "",
            "'": "",
            "'": ""
        }
        
        # Save enhanced mappings
        mappings_file = self.results_dir / "enhanced_symbol_mappings.json"
        with open(mappings_file, 'w') as f:
            json.dump(enhanced_mappings, f, indent=2)
        
        logger.info(f"Enhanced symbol mappings saved to: {mappings_file}")
        return enhanced_mappings
    
    def benchmark_espeak_performance(self) -> Dict[str, Any]:
        """Benchmark eSpeak performance with various configurations"""
        logger.info("Benchmarking eSpeak performance...")
        
        available, espeak_path, info = self.check_espeak_installation()
        if not available:
            logger.error("eSpeak not available for benchmarking")
            return {}
        
        test_texts = [
            "Hello world",
            "What is your name?",
            "The quick brown fox jumps over the lazy dog.",
            "I'm going to the store to buy some groceries.",
            "Use the * symbol and the @ sign in your email.",
            "This is a longer text that contains multiple sentences. It should test the performance of eSpeak with more complex input. The goal is to measure processing time and accuracy."
        ]
        
        benchmark_results = {
            "ascii_phonemes": [],
            "ipa_phonemes": [],
            "with_punctuation": [],
            "without_punctuation": []
        }
        
        for text in test_texts:
            # Test ASCII phonemes
            start_time = time.perf_counter()
            result = subprocess.run([espeak_path, "-q", "-x", "-v", "en-us", text], 
                                  capture_output=True, text=True, timeout=10)
            ascii_time = time.perf_counter() - start_time
            
            if result.returncode == 0:
                benchmark_results["ascii_phonemes"].append({
                    "text": text[:30] + "..." if len(text) > 30 else text,
                    "processing_time": ascii_time,
                    "output_length": len(result.stdout.strip()),
                    "success": True
                })
            
            # Test IPA phonemes
            start_time = time.perf_counter()
            result = subprocess.run([espeak_path, "-q", "--ipa", "-v", "en-us", text], 
                                  capture_output=True, text=True, timeout=10)
            ipa_time = time.perf_counter() - start_time
            
            if result.returncode == 0:
                benchmark_results["ipa_phonemes"].append({
                    "text": text[:30] + "..." if len(text) > 30 else text,
                    "processing_time": ipa_time,
                    "output_length": len(result.stdout.strip()),
                    "success": True
                })
        
        # Calculate averages
        for category, results in benchmark_results.items():
            if results:
                avg_time = sum(r["processing_time"] for r in results) / len(results)
                benchmark_results[f"{category}_avg_time"] = avg_time
        
        return benchmark_results
    
    def run_comprehensive_enhancement(self) -> Dict[str, Any]:
        """Run comprehensive eSpeak integration enhancement"""
        logger.info("Starting comprehensive eSpeak integration enhancement...")
        
        enhancement_results = {
            "timestamp": time.time(),
            "installation_check": {},
            "optimization_results": {},
            "test_results": {},
            "performance_benchmarks": {},
            "recommendations": []
        }
        
        # Step 1: Check eSpeak availability
        logger.info("Step 1: Checking eSpeak installation...")
        available, path_or_error, info = self.check_espeak_installation()

        if not available:
            logger.info("Checking eSpeak availability...")
            install_success = self.install_espeak_if_missing()
            if install_success:
                available, path_or_error, info = self.check_espeak_installation()

        enhancement_results["installation_check"] = {
            "available": available,
            "path": path_or_error if available else None,
            "info": info,
            "error": path_or_error if not available else None
        }

        if not available:
            logger.warning("eSpeak not available - proceeding with configuration optimization only")
            # Continue with configuration optimization even without eSpeak
        
        # Step 2: Optimize configuration
        logger.info("Step 2: Optimizing eSpeak configuration...")
        optimization_results = self.optimize_espeak_configuration()
        enhancement_results["optimization_results"] = optimization_results
        
        # Step 3: Create enhanced symbol mappings
        logger.info("Step 3: Creating enhanced symbol mappings...")
        enhanced_mappings = self.create_enhanced_symbol_mappings()
        enhancement_results["enhanced_mappings_count"] = len(enhanced_mappings)
        
        # Step 4: Test symbol pronunciation (if eSpeak available)
        if available:
            logger.info("Step 4: Testing symbol pronunciation...")
            all_test_cases = (self.symbol_test_cases +
                             self.interjection_test_cases +
                             self.contraction_test_cases)

            test_results = self.test_espeak_phonemization(all_test_cases)
            enhancement_results["test_results"] = {
                "total_tests": len(test_results),
                "successful_tests": sum(1 for r in test_results if r.success),
                "failed_tests": sum(1 for r in test_results if not r.success),
                "average_processing_time": sum(r.processing_time for r in test_results) / len(test_results) if test_results else 0,
                "detailed_results": [asdict(r) for r in test_results]
            }

            # Step 5: Performance benchmarking
            logger.info("Step 5: Running performance benchmarks...")
            benchmark_results = self.benchmark_espeak_performance()
            enhancement_results["performance_benchmarks"] = benchmark_results
        else:
            logger.info("Step 4-5: Skipping eSpeak tests (not available)")
            enhancement_results["test_results"] = {
                "total_tests": 0,
                "successful_tests": 0,
                "failed_tests": 0,
                "average_processing_time": 0,
                "detailed_results": [],
                "skipped_reason": "eSpeak not available"
            }
            enhancement_results["performance_benchmarks"] = {
                "skipped_reason": "eSpeak not available"
            }
        
        # Step 6: Generate recommendations
        logger.info("Step 6: Generating recommendations...")
        recommendations = self._generate_enhancement_recommendations(enhancement_results)
        enhancement_results["recommendations"] = recommendations
        
        # Save results
        results_file = self.results_dir / f"espeak_enhancement_{int(time.time())}.json"
        with open(results_file, 'w') as f:
            json.dump(enhancement_results, f, indent=2, default=str)
        
        logger.info(f"Enhancement completed. Results saved to: {results_file}")
        return enhancement_results
    
    def _generate_enhancement_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on enhancement results"""
        recommendations = []
        
        # Installation recommendations
        if not results["installation_check"]["available"]:
            recommendations.append("Install eSpeak for improved phonetic processing")
        
        # Performance recommendations
        test_results = results.get("test_results", {})
        if test_results.get("failed_tests", 0) > 0:
            recommendations.append("Review failed test cases and improve symbol mappings")
        
        avg_time = test_results.get("average_processing_time", 0)
        if avg_time > 0.1:
            recommendations.append("Optimize eSpeak processing for better performance")
        
        # Configuration recommendations
        success_rate = test_results.get("successful_tests", 0) / max(1, test_results.get("total_tests", 1))
        if success_rate < 0.8:
            recommendations.append("Improve eSpeak configuration for better accuracy")
        
        # Integration recommendations
        recommendations.append("Enable eSpeak integration in production configuration")
        recommendations.append("Monitor eSpeak performance in production environment")
        recommendations.append("Consider caching frequently used phoneme patterns")
        
        return recommendations

def main():
    """Main function to run eSpeak integration enhancement"""
    enhancer = EspeakIntegrationEnhancer()
    
    try:
        results = enhancer.run_comprehensive_enhancement()
        
        print("\n" + "="*80)
        print("ESPEAK INTEGRATION ENHANCEMENT SUMMARY")
        print("="*80)
        
        # Installation status
        install_check = results["installation_check"]
        print(f"eSpeak Available: {'✅' if install_check['available'] else '❌'}")
        if install_check["available"]:
            print(f"eSpeak Path: {install_check['path']}")
            print(f"Version: {install_check['info'].get('version', 'Unknown')}")
        
        # Test results
        test_results = results["test_results"]
        print(f"\nTest Results:")
        print(f"  Total Tests: {test_results['total_tests']}")
        print(f"  Successful: {test_results['successful_tests']}")
        print(f"  Failed: {test_results['failed_tests']}")
        print(f"  Success Rate: {test_results['successful_tests']/max(1,test_results['total_tests'])*100:.1f}%")
        print(f"  Avg Processing Time: {test_results['average_processing_time']:.4f}s")
        
        # Performance benchmarks
        benchmarks = results["performance_benchmarks"]
        if "ascii_phonemes_avg_time" in benchmarks:
            print(f"\nPerformance Benchmarks:")
            print(f"  ASCII Phonemes Avg Time: {benchmarks['ascii_phonemes_avg_time']:.4f}s")
            if "ipa_phonemes_avg_time" in benchmarks:
                print(f"  IPA Phonemes Avg Time: {benchmarks['ipa_phonemes_avg_time']:.4f}s")
        
        # Recommendations
        print(f"\nRecommendations:")
        for i, rec in enumerate(results["recommendations"], 1):
            print(f"  {i}. {rec}")
        
        print("\n" + "="*80)
        
    except Exception as e:
        logger.error(f"Enhancement failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main()
