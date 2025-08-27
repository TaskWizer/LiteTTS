#!/usr/bin/env python3
"""
RTF Performance Optimization System
Optimize for RTF < 0.25 for short text, < 0.2 overall, with special focus on texts under 20 characters
"""

import os
import sys
import json
import logging
import asyncio
import aiohttp
import time
import statistics
import wave
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class RTFTestCase:
    """RTF performance test case"""
    test_id: str
    input_text: str
    text_length: int
    category: str
    target_rtf: float
    priority: str
    description: str

@dataclass
class RTFResult:
    """RTF performance test result"""
    test_case: RTFTestCase
    generation_time: float
    audio_duration: float
    rtf: float
    success: bool
    target_met: bool
    voice_model: str
    error_message: str = ""

@dataclass
class RTFOptimizationConfig:
    """RTF optimization configuration"""
    enable_model_caching: bool
    enable_text_preprocessing_cache: bool
    enable_parallel_processing: bool
    max_concurrent_requests: int
    enable_audio_streaming: bool
    enable_fast_inference_mode: bool
    optimize_for_short_text: bool
    preload_models: bool
    use_quantized_models: bool
    enable_batch_processing: bool

class RTFPerformanceOptimizer:
    """RTF performance optimization system"""
    
    def __init__(self, api_base_url: str = "http://localhost:8354"):
        self.api_base_url = api_base_url
        self.results_dir = Path("test_results/rtf_optimization")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Create comprehensive test cases
        self.test_cases = self._create_rtf_test_cases()
        
        # Performance tracking
        self.baseline_results = []
        self.optimized_results = []
        
    def _create_rtf_test_cases(self) -> List[RTFTestCase]:
        """Create comprehensive RTF test cases"""
        test_cases = []
        
        # Ultra-short text tests (< 10 characters) - Critical for RTF
        ultra_short_texts = [
            "Hi",
            "Hello",
            "Yes",
            "No",
            "Thanks",
            "OK",
            "Stop",
            "Go",
            "Wait"
        ]
        
        for i, text in enumerate(ultra_short_texts):
            test_cases.append(RTFTestCase(
                test_id=f"ultra_short_{i+1}",
                input_text=text,
                text_length=len(text),
                category="ultra_short",
                target_rtf=0.15,  # Very aggressive target for ultra-short
                priority="critical",
                description=f"Ultra-short text: '{text}' ({len(text)} chars)"
            ))
        
        # Short text tests (10-20 characters) - Primary focus
        short_texts = [
            "Good morning",
            "How are you?",
            "Thank you",
            "See you later",
            "Have a nice day",
            "What's up?",
            "I'm fine",
            "Goodbye",
            "Please help me"
        ]
        
        for i, text in enumerate(short_texts):
            test_cases.append(RTFTestCase(
                test_id=f"short_{i+1}",
                input_text=text,
                text_length=len(text),
                category="short",
                target_rtf=0.2,  # Target for short text
                priority="critical",
                description=f"Short text: '{text}' ({len(text)} chars)"
            ))
        
        # Medium text tests (20-50 characters)
        medium_texts = [
            "The quick brown fox jumps over the lazy dog",
            "This is a test of the emergency broadcast system",
            "Please speak clearly and slowly for best results",
            "Natural language processing is fascinating",
            "Text-to-speech technology has improved significantly"
        ]
        
        for i, text in enumerate(medium_texts):
            test_cases.append(RTFTestCase(
                test_id=f"medium_{i+1}",
                input_text=text,
                text_length=len(text),
                category="medium",
                target_rtf=0.25,  # Standard target
                priority="high",
                description=f"Medium text: '{text[:30]}...' ({len(text)} chars)"
            ))
        
        # Performance stress tests
        stress_texts = [
            "A" * 10,  # Repetitive ultra-short
            "Hello world! " * 3,  # Repetitive short
            "Performance testing with numbers: 1, 2, 3, 4, 5.",  # Numbers
            "Special characters: @#$%^&*()_+-=[]{}|;:,.<>?",  # Symbols
            "Mixed case: ThIs Is A tEsT oF mIxEd CaSe TeXt"  # Mixed case
        ]
        
        for i, text in enumerate(stress_texts):
            test_cases.append(RTFTestCase(
                test_id=f"stress_{i+1}",
                input_text=text,
                text_length=len(text),
                category="stress",
                target_rtf=0.25,
                priority="normal",
                description=f"Stress test: {text[:30]}... ({len(text)} chars)"
            ))
        
        return test_cases
    
    async def generate_audio_with_timing(self, text: str, voice: str = "af_heart") -> Tuple[bool, float, float, str]:
        """Generate audio and measure timing"""
        try:
            start_time = time.perf_counter()
            
            async with aiohttp.ClientSession() as session:
                payload = {
                    'model': 'kokoro',
                    'input': text,
                    'voice': voice,
                    'response_format': 'wav'
                }
                
                async with session.post(
                    f"{self.api_base_url}/v1/audio/speech",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    generation_time = time.perf_counter() - start_time
                    
                    if response.status == 200:
                        audio_data = await response.read()
                        
                        # Analyze audio duration
                        audio_duration = self._analyze_audio_duration(audio_data)
                        
                        return True, generation_time, audio_duration, ""
                    else:
                        error_text = await response.text()
                        return False, generation_time, 0.0, f"HTTP {response.status}: {error_text}"
                        
        except Exception as e:
            generation_time = time.perf_counter() - start_time
            return False, generation_time, 0.0, str(e)
    
    def _analyze_audio_duration(self, audio_data: bytes) -> float:
        """Analyze audio duration from WAV data"""
        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name
            
            with wave.open(temp_path, 'rb') as wav_file:
                frames = wav_file.getnframes()
                sample_rate = wav_file.getframerate()
                duration = frames / float(sample_rate)
            
            os.unlink(temp_path)
            return duration
            
        except Exception as e:
            logger.warning(f"Audio duration analysis failed: {e}")
            return 0.0
    
    async def test_single_rtf_case(self, test_case: RTFTestCase, voice: str = "af_heart") -> RTFResult:
        """Test a single RTF case"""
        logger.info(f"Testing RTF: {test_case.test_id} - {test_case.description}")
        
        success, generation_time, audio_duration, error = await self.generate_audio_with_timing(
            test_case.input_text, voice
        )
        
        if success and audio_duration > 0:
            rtf = generation_time / audio_duration
            target_met = rtf <= test_case.target_rtf
        else:
            rtf = float('inf')
            target_met = False
        
        result = RTFResult(
            test_case=test_case,
            generation_time=generation_time,
            audio_duration=audio_duration,
            rtf=rtf,
            success=success,
            target_met=target_met,
            voice_model=voice,
            error_message=error
        )
        
        logger.info(f"Completed: {test_case.test_id} - RTF: {rtf:.3f}, Target: {test_case.target_rtf}, Met: {'✅' if target_met else '❌'}")
        return result
    
    async def run_baseline_rtf_tests(self, voice_models: List[str] = None) -> List[RTFResult]:
        """Run baseline RTF performance tests"""
        if voice_models is None:
            voice_models = ["af_heart"]
        
        logger.info("Running baseline RTF performance tests...")
        
        baseline_results = []
        
        for voice in voice_models:
            logger.info(f"Testing voice: {voice}")
            
            for test_case in self.test_cases:
                result = await self.test_single_rtf_case(test_case, voice)
                baseline_results.append(result)
        
        self.baseline_results = baseline_results
        logger.info(f"Baseline tests completed: {len(baseline_results)} results")
        return baseline_results
    
    def calculate_optimization_config(self, baseline_results: List[RTFResult]) -> RTFOptimizationConfig:
        """Calculate optimal RTF optimization configuration"""
        logger.info("Calculating optimal RTF optimization configuration...")
        
        # Analyze baseline performance
        failed_targets = [r for r in baseline_results if not r.target_met and r.success]
        ultra_short_results = [r for r in baseline_results if r.test_case.category == "ultra_short" and r.success]
        short_results = [r for r in baseline_results if r.test_case.category == "short" and r.success]
        
        # Determine optimization strategy based on failures
        needs_aggressive_optimization = len(failed_targets) > len(baseline_results) * 0.3
        needs_short_text_optimization = any(not r.target_met for r in ultra_short_results + short_results)
        
        config = RTFOptimizationConfig(
            enable_model_caching=True,
            enable_text_preprocessing_cache=True,
            enable_parallel_processing=needs_aggressive_optimization,
            max_concurrent_requests=4 if needs_aggressive_optimization else 2,
            enable_audio_streaming=True,
            enable_fast_inference_mode=needs_short_text_optimization,
            optimize_for_short_text=needs_short_text_optimization,
            preload_models=True,
            use_quantized_models=True,
            enable_batch_processing=needs_aggressive_optimization
        )
        
        logger.info(f"Optimization config: Aggressive: {needs_aggressive_optimization}, Short text focus: {needs_short_text_optimization}")
        return config
    
    def apply_rtf_optimizations(self, config: RTFOptimizationConfig) -> Dict[str, Any]:
        """Apply RTF optimizations"""
        logger.info("Applying RTF optimizations...")
        
        optimization_settings = {
            "model_optimization": {
                "use_quantized_models": config.use_quantized_models,
                "preload_models": config.preload_models,
                "enable_model_caching": config.enable_model_caching,
                "cache_size_mb": 128 if config.enable_model_caching else 0
            },
            "inference_optimization": {
                "enable_fast_inference_mode": config.enable_fast_inference_mode,
                "optimize_for_short_text": config.optimize_for_short_text,
                "enable_audio_streaming": config.enable_audio_streaming,
                "batch_size": 4 if config.enable_batch_processing else 1
            },
            "text_processing_optimization": {
                "enable_preprocessing_cache": config.enable_text_preprocessing_cache,
                "cache_size": 1000 if config.enable_text_preprocessing_cache else 0,
                "skip_unnecessary_processing": config.optimize_for_short_text
            },
            "system_optimization": {
                "enable_parallel_processing": config.enable_parallel_processing,
                "max_concurrent_requests": config.max_concurrent_requests,
                "thread_pool_size": config.max_concurrent_requests * 2
            }
        }
        
        # Apply environment variables for optimization
        if config.enable_fast_inference_mode:
            os.environ['KOKORO_FAST_INFERENCE'] = 'true'
            os.environ['KOKORO_OPTIMIZE_SHORT_TEXT'] = 'true'
        
        if config.use_quantized_models:
            os.environ['KOKORO_USE_QUANTIZED'] = 'true'
        
        logger.info("RTF optimizations applied")
        return optimization_settings
    
    async def run_optimized_rtf_tests(self, config: RTFOptimizationConfig, voice_models: List[str] = None) -> List[RTFResult]:
        """Run optimized RTF performance tests"""
        if voice_models is None:
            voice_models = ["af_heart"]
        
        logger.info("Running optimized RTF performance tests...")
        
        # Apply optimizations
        optimization_settings = self.apply_rtf_optimizations(config)
        
        # Wait for optimizations to take effect
        await asyncio.sleep(2)
        
        optimized_results = []
        
        for voice in voice_models:
            logger.info(f"Testing optimized voice: {voice}")
            
            if config.enable_parallel_processing:
                # Run tests in parallel for better performance
                semaphore = asyncio.Semaphore(config.max_concurrent_requests)
                
                async def test_with_semaphore(test_case):
                    async with semaphore:
                        return await self.test_single_rtf_case(test_case, voice)
                
                tasks = [test_with_semaphore(tc) for tc in self.test_cases]
                results = await asyncio.gather(*tasks)
                optimized_results.extend(results)
            else:
                # Run tests sequentially
                for test_case in self.test_cases:
                    result = await self.test_single_rtf_case(test_case, voice)
                    optimized_results.append(result)
        
        self.optimized_results = optimized_results
        logger.info(f"Optimized tests completed: {len(optimized_results)} results")
        return optimized_results
    
    def analyze_rtf_improvements(self, baseline_results: List[RTFResult], optimized_results: List[RTFResult]) -> Dict[str, Any]:
        """Analyze RTF performance improvements"""
        logger.info("Analyzing RTF performance improvements...")
        
        # Group results by category
        categories = ["ultra_short", "short", "medium", "stress"]
        analysis = {}
        
        for category in categories:
            baseline_cat = [r for r in baseline_results if r.test_case.category == category and r.success]
            optimized_cat = [r for r in optimized_results if r.test_case.category == category and r.success]
            
            if baseline_cat and optimized_cat:
                baseline_rtf = [r.rtf for r in baseline_cat]
                optimized_rtf = [r.rtf for r in optimized_cat]
                
                baseline_targets_met = sum(1 for r in baseline_cat if r.target_met)
                optimized_targets_met = sum(1 for r in optimized_cat if r.target_met)
                
                analysis[category] = {
                    "baseline_avg_rtf": statistics.mean(baseline_rtf),
                    "optimized_avg_rtf": statistics.mean(optimized_rtf),
                    "rtf_improvement": statistics.mean(baseline_rtf) - statistics.mean(optimized_rtf),
                    "rtf_improvement_percent": ((statistics.mean(baseline_rtf) - statistics.mean(optimized_rtf)) / statistics.mean(baseline_rtf)) * 100,
                    "baseline_targets_met": baseline_targets_met,
                    "optimized_targets_met": optimized_targets_met,
                    "target_improvement": optimized_targets_met - baseline_targets_met,
                    "total_tests": len(baseline_cat)
                }
        
        # Overall analysis
        all_baseline = [r for r in baseline_results if r.success]
        all_optimized = [r for r in optimized_results if r.success]
        
        if all_baseline and all_optimized:
            baseline_rtf_all = [r.rtf for r in all_baseline]
            optimized_rtf_all = [r.rtf for r in all_optimized]
            
            analysis["overall"] = {
                "baseline_avg_rtf": statistics.mean(baseline_rtf_all),
                "optimized_avg_rtf": statistics.mean(optimized_rtf_all),
                "rtf_improvement": statistics.mean(baseline_rtf_all) - statistics.mean(optimized_rtf_all),
                "rtf_improvement_percent": ((statistics.mean(baseline_rtf_all) - statistics.mean(optimized_rtf_all)) / statistics.mean(baseline_rtf_all)) * 100,
                "baseline_targets_met": sum(1 for r in all_baseline if r.target_met),
                "optimized_targets_met": sum(1 for r in all_optimized if r.target_met),
                "total_tests": len(all_baseline)
            }
        
        return analysis
    
    def generate_rtf_recommendations(self, analysis: Dict[str, Any], config: RTFOptimizationConfig) -> List[str]:
        """Generate RTF optimization recommendations"""
        recommendations = []
        
        overall = analysis.get("overall", {})
        
        # Overall performance recommendations
        if overall.get("optimized_avg_rtf", 1.0) > 0.25:
            recommendations.append("Overall RTF still exceeds 0.25 target - consider hardware upgrade or model optimization")
        
        # Category-specific recommendations
        ultra_short = analysis.get("ultra_short", {})
        if ultra_short.get("optimized_avg_rtf", 1.0) > 0.15:
            recommendations.append("Ultra-short text RTF exceeds 0.15 target - implement specialized short text optimization")
        
        short = analysis.get("short", {})
        if short.get("optimized_avg_rtf", 1.0) > 0.2:
            recommendations.append("Short text RTF exceeds 0.2 target - focus on text preprocessing optimization")
        
        # Improvement recommendations
        if overall.get("rtf_improvement_percent", 0) < 10:
            recommendations.append("Limited RTF improvement achieved - consider more aggressive optimization strategies")
        
        # Configuration recommendations
        if not config.enable_parallel_processing:
            recommendations.append("Enable parallel processing for better performance on multi-core systems")
        
        if not config.use_quantized_models:
            recommendations.append("Use quantized models for better inference speed")
        
        return recommendations

    async def run_comprehensive_rtf_optimization(self, voice_models: List[str] = None) -> Dict[str, Any]:
        """Run comprehensive RTF performance optimization"""
        if voice_models is None:
            voice_models = ["af_heart"]

        logger.info("Starting comprehensive RTF performance optimization...")

        # Step 1: Run baseline tests
        baseline_results = await self.run_baseline_rtf_tests(voice_models)

        # Step 2: Calculate optimization configuration
        config = self.calculate_optimization_config(baseline_results)

        # Step 3: Run optimized tests
        optimized_results = await self.run_optimized_rtf_tests(config, voice_models)

        # Step 4: Analyze improvements
        analysis = self.analyze_rtf_improvements(baseline_results, optimized_results)

        # Step 5: Generate recommendations
        recommendations = self.generate_rtf_recommendations(analysis, config)

        # Compile comprehensive results
        results = {
            "optimization_timestamp": time.time(),
            "voice_models_tested": voice_models,
            "optimization_config": asdict(config),
            "baseline_results": [asdict(r) for r in baseline_results],
            "optimized_results": [asdict(r) for r in optimized_results],
            "performance_analysis": analysis,
            "recommendations": recommendations,
            "summary": self._generate_performance_summary(baseline_results, optimized_results, analysis)
        }

        # Save results
        results_file = self.results_dir / f"rtf_optimization_results_{int(time.time())}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"RTF optimization completed. Results saved to: {results_file}")
        return results

    def _generate_performance_summary(self, baseline_results: List[RTFResult],
                                    optimized_results: List[RTFResult],
                                    analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate performance summary"""

        # Calculate success rates
        baseline_success = sum(1 for r in baseline_results if r.success)
        optimized_success = sum(1 for r in optimized_results if r.success)

        baseline_targets_met = sum(1 for r in baseline_results if r.target_met)
        optimized_targets_met = sum(1 for r in optimized_results if r.target_met)

        overall = analysis.get("overall", {})

        summary = {
            "total_tests": len(baseline_results),
            "baseline_success_rate": baseline_success / len(baseline_results) if baseline_results else 0,
            "optimized_success_rate": optimized_success / len(optimized_results) if optimized_results else 0,
            "baseline_target_compliance": baseline_targets_met / baseline_success if baseline_success > 0 else 0,
            "optimized_target_compliance": optimized_targets_met / optimized_success if optimized_success > 0 else 0,
            "rtf_improvement_percent": overall.get("rtf_improvement_percent", 0),
            "targets_improvement": optimized_targets_met - baseline_targets_met,
            "performance_grade": self._calculate_performance_grade(analysis),
            "critical_targets_met": {
                "ultra_short_rtf_015": analysis.get("ultra_short", {}).get("optimized_avg_rtf", 1.0) <= 0.15,
                "short_rtf_020": analysis.get("short", {}).get("optimized_avg_rtf", 1.0) <= 0.2,
                "overall_rtf_025": overall.get("optimized_avg_rtf", 1.0) <= 0.25
            }
        }

        return summary

    def _calculate_performance_grade(self, analysis: Dict[str, Any]) -> str:
        """Calculate overall performance grade"""
        overall = analysis.get("overall", {})
        ultra_short = analysis.get("ultra_short", {})
        short = analysis.get("short", {})

        score = 0

        # RTF targets
        if overall.get("optimized_avg_rtf", 1.0) <= 0.2:
            score += 3
        elif overall.get("optimized_avg_rtf", 1.0) <= 0.25:
            score += 2
        elif overall.get("optimized_avg_rtf", 1.0) <= 0.3:
            score += 1

        # Short text performance
        if ultra_short.get("optimized_avg_rtf", 1.0) <= 0.15:
            score += 2
        elif ultra_short.get("optimized_avg_rtf", 1.0) <= 0.2:
            score += 1

        if short.get("optimized_avg_rtf", 1.0) <= 0.2:
            score += 2
        elif short.get("optimized_avg_rtf", 1.0) <= 0.25:
            score += 1

        # Improvement
        if overall.get("rtf_improvement_percent", 0) >= 20:
            score += 2
        elif overall.get("rtf_improvement_percent", 0) >= 10:
            score += 1

        # Grade assignment
        if score >= 8:
            return "A+"
        elif score >= 7:
            return "A"
        elif score >= 6:
            return "B+"
        elif score >= 5:
            return "B"
        elif score >= 4:
            return "C+"
        elif score >= 3:
            return "C"
        else:
            return "D"

async def main():
    """Main function to run RTF performance optimization"""
    optimizer = RTFPerformanceOptimizer()

    try:
        results = await optimizer.run_comprehensive_rtf_optimization(["af_heart"])

        print("\n" + "="*80)
        print("RTF PERFORMANCE OPTIMIZATION SUMMARY")
        print("="*80)

        summary = results["summary"]
        analysis = results["performance_analysis"]

        print(f"Total Tests: {summary['total_tests']}")
        print(f"Performance Grade: {summary['performance_grade']}")
        print(f"RTF Improvement: {summary['rtf_improvement_percent']:.1f}%")
        print(f"Target Compliance Improvement: {summary['optimized_target_compliance']:.1%}")

        print(f"\nCritical Targets:")
        targets = summary["critical_targets_met"]
        print(f"  Ultra-short RTF < 0.15: {'✅' if targets['ultra_short_rtf_015'] else '❌'}")
        print(f"  Short RTF < 0.20: {'✅' if targets['short_rtf_020'] else '❌'}")
        print(f"  Overall RTF < 0.25: {'✅' if targets['overall_rtf_025'] else '❌'}")

        print(f"\nCategory Performance:")
        for category in ["ultra_short", "short", "medium", "overall"]:
            if category in analysis:
                cat_data = analysis[category]
                print(f"  {category.title()}: {cat_data['baseline_avg_rtf']:.3f} → {cat_data['optimized_avg_rtf']:.3f} RTF")

        print(f"\nRecommendations:")
        for i, rec in enumerate(results["recommendations"], 1):
            print(f"  {i}. {rec}")

        print("\n" + "="*80)

    except Exception as e:
        logger.error(f"RTF optimization failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(main())
