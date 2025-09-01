#!/usr/bin/env python3
"""
Simple Performance Test
Lightweight performance testing without full TTS dependencies
"""

import time
import logging
import json
import statistics
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import sys
import os

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from LiteTTS.nlp.text_normalizer import TextNormalizer
    from LiteTTS.nlp.rime_ai_integration import rime_ai_processor
    TEXT_PROCESSING_AVAILABLE = True
except ImportError as e:
    TEXT_PROCESSING_AVAILABLE = False
    print(f"Text processing not available: {e}")

logger = logging.getLogger(__name__)

@dataclass
class SimplePerformanceMetrics:
    """Simple performance metrics"""
    test_name: str
    text_length: int
    processing_time: float
    throughput_chars_per_sec: float
    success: bool
    error_message: Optional[str] = None

class SimplePerformanceTester:
    """Lightweight performance tester for text processing components"""
    
    def __init__(self):
        self.test_texts = [
            "Hello world",
            "The quick brown fox jumps over the lazy dog.",
            "This is a test of the text processing system with numbers like 123 and symbols like $.",
            "Performance testing requires systematic evaluation of processing speed and accuracy. "
            "The system should handle contractions like don't, won't, and can't properly.",
            "Complex text with URLs like https://example.com, emails like test@example.com, "
            "currency amounts like $123.45, dates like 2023-10-27, and contractions like I'll, you'll."
        ]
        
        if TEXT_PROCESSING_AVAILABLE:
            self.text_normalizer = TextNormalizer()
        
        logger.info("Simple performance tester initialized")
    
    def run_text_processing_performance_test(self) -> List[SimplePerformanceMetrics]:
        """Test text processing performance"""
        if not TEXT_PROCESSING_AVAILABLE:
            return [SimplePerformanceMetrics(
                test_name="text_processing_unavailable",
                text_length=0,
                processing_time=0.0,
                throughput_chars_per_sec=0.0,
                success=False,
                error_message="Text processing components not available"
            )]
        
        results = []
        
        for i, text in enumerate(self.test_texts):
            test_name = f"text_normalization_{i+1}"
            
            try:
                start_time = time.perf_counter()
                
                # Test text normalization
                normalized_text = self.text_normalizer.normalize_text(text)
                
                end_time = time.perf_counter()
                processing_time = end_time - start_time
                
                # Calculate throughput
                throughput = len(text) / processing_time if processing_time > 0 else 0
                
                results.append(SimplePerformanceMetrics(
                    test_name=test_name,
                    text_length=len(text),
                    processing_time=processing_time,
                    throughput_chars_per_sec=throughput,
                    success=True
                ))
                
                logger.info(f"Test {test_name}: {processing_time:.4f}s, {throughput:.0f} chars/sec")
                
            except Exception as e:
                logger.error(f"Test {test_name} failed: {e}")
                results.append(SimplePerformanceMetrics(
                    test_name=test_name,
                    text_length=len(text),
                    processing_time=0.0,
                    throughput_chars_per_sec=0.0,
                    success=False,
                    error_message=str(e)
                ))
        
        return results
    
    def run_rime_ai_performance_test(self) -> List[SimplePerformanceMetrics]:
        """Test RIME AI processing performance"""
        results = []
        
        # Test RIME AI notation processing
        rime_test_texts = [
            "Hello {k1Ast0xm} world",  # RIME AI notation
            "The pronunciation of {h1Ed0n1Izm} is important",
            "Testing {1Ast0r1Isk} pronunciation",
            "Normal text without RIME notation",
            "Mixed text with {f0n1Et1Ik} and normal words"
        ]
        
        for i, text in enumerate(rime_test_texts):
            test_name = f"rime_ai_processing_{i+1}"
            
            try:
                start_time = time.perf_counter()
                
                # Test RIME AI processing
                analysis = rime_ai_processor.process_text_with_rime_ai(text)
                
                end_time = time.perf_counter()
                processing_time = end_time - start_time
                
                # Calculate throughput
                throughput = len(text) / processing_time if processing_time > 0 else 0
                
                results.append(SimplePerformanceMetrics(
                    test_name=test_name,
                    text_length=len(text),
                    processing_time=processing_time,
                    throughput_chars_per_sec=throughput,
                    success=True
                ))
                
                logger.info(f"Test {test_name}: {processing_time:.4f}s, confidence: {analysis.confidence_score:.2f}")
                
            except Exception as e:
                logger.error(f"Test {test_name} failed: {e}")
                results.append(SimplePerformanceMetrics(
                    test_name=test_name,
                    text_length=len(text),
                    processing_time=0.0,
                    throughput_chars_per_sec=0.0,
                    success=False,
                    error_message=str(e)
                ))
        
        return results
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all available performance tests"""
        logger.info("Running all performance tests")
        
        all_results = {}
        
        # Text processing tests
        text_results = self.run_text_processing_performance_test()
        all_results['text_processing'] = text_results
        
        # RIME AI tests
        rime_results = self.run_rime_ai_performance_test()
        all_results['rime_ai_processing'] = rime_results
        
        # Calculate summary statistics
        all_metrics = text_results + rime_results
        successful_metrics = [m for m in all_metrics if m.success]
        
        if successful_metrics:
            summary = {
                'total_tests': len(all_metrics),
                'successful_tests': len(successful_metrics),
                'failed_tests': len(all_metrics) - len(successful_metrics),
                'average_processing_time': statistics.mean(m.processing_time for m in successful_metrics),
                'average_throughput': statistics.mean(m.throughput_chars_per_sec for m in successful_metrics),
                'min_processing_time': min(m.processing_time for m in successful_metrics),
                'max_processing_time': max(m.processing_time for m in successful_metrics),
                'total_characters_processed': sum(m.text_length for m in successful_metrics)
            }
        else:
            summary = {
                'total_tests': len(all_metrics),
                'successful_tests': 0,
                'failed_tests': len(all_metrics),
                'error': 'All tests failed'
            }
        
        all_results['summary'] = summary
        
        return all_results
    
    def save_results(self, results: Dict[str, Any], filename: str = "simple_performance_results.json"):
        """Save test results to file"""
        # Convert dataclasses to dictionaries for JSON serialization
        serializable_results = {}
        
        for key, value in results.items():
            if key == 'summary':
                serializable_results[key] = value
            else:
                serializable_results[key] = [asdict(item) for item in value]
        
        try:
            with open(filename, 'w') as f:
                json.dump(serializable_results, f, indent=2)
            logger.info(f"Results saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to save results: {e}")

def main():
    """Main test execution"""
    print("Simple Performance Test")
    print("=" * 30)
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    try:
        tester = SimplePerformanceTester()
        results = tester.run_all_tests()
        
        # Print summary
        summary = results['summary']
        print(f"\nTest Summary:")
        print(f"  Total Tests: {summary['total_tests']}")
        print(f"  Successful: {summary['successful_tests']}")
        print(f"  Failed: {summary['failed_tests']}")
        
        if 'average_processing_time' in summary:
            print(f"  Average Processing Time: {summary['average_processing_time']:.4f}s")
            print(f"  Average Throughput: {summary['average_throughput']:.0f} chars/sec")
            print(f"  Total Characters Processed: {summary['total_characters_processed']}")
        
        # Save results
        tester.save_results(results)
        
        # Print detailed results
        print(f"\nDetailed Results:")
        for category, metrics in results.items():
            if category == 'summary':
                continue
            
            print(f"\n{category.replace('_', ' ').title()}:")
            for metric in metrics:
                status = "✅" if metric.success else "❌"
                if metric.success:
                    print(f"  {status} {metric.test_name}: {metric.processing_time:.4f}s ({metric.throughput_chars_per_sec:.0f} chars/sec)")
                else:
                    print(f"  {status} {metric.test_name}: {metric.error_message}")
        
        success = summary['failed_tests'] == 0
        if success:
            print(f"\n🎉 All tests passed!")
        else:
            print(f"\n⚠️  {summary['failed_tests']} tests failed.")
        
        return success
        
    except Exception as e:
        logger.error(f"Performance testing failed: {e}")
        print(f"\n❌ Testing failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
