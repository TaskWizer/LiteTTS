#!/usr/bin/env python3
"""
Final Production Readiness Assessment
"""

import requests
import json
import time
import psutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List

class ProductionReadinessAssessment:
    """Comprehensive production readiness assessment"""
    
    def __init__(self):
        self.results = {}
        self.score = 0
        self.max_score = 0
        
    def assess_core_functionality(self) -> Dict[str, Any]:
        """Assess core TTS functionality"""
        print("🔧 Assessing Core Functionality")
        print("-" * 40)
        
        tests = [
            ("Basic TTS", self._test_basic_tts),
            ("Multiple Voices", self._test_multiple_voices),
            ("Different Formats", self._test_different_formats),
            ("Speed Control", self._test_speed_control),
            ("Error Handling", self._test_error_handling),
        ]
        
        results = {}
        for test_name, test_func in tests:
            try:
                result = test_func()
                results[test_name] = result
                if result.get('success', False):
                    self.score += 1
                    print(f"   ✅ {test_name}: PASS")
                else:
                    print(f"   ❌ {test_name}: FAIL - {result.get('error', 'Unknown error')}")
                self.max_score += 1
            except Exception as e:
                results[test_name] = {'success': False, 'error': str(e)}
                print(f"   ❌ {test_name}: ERROR - {e}")
                self.max_score += 1
        
        return results
    
    def assess_performance(self) -> Dict[str, Any]:
        """Assess performance characteristics"""
        print("\n⚡ Assessing Performance")
        print("-" * 40)
        
        performance_results = {}
        
        # Test response times
        try:
            # Cache miss test
            unique_text = f"Performance test {time.time()}"
            start_time = time.time()
            response = requests.post(
                "http://localhost:8354/v1/audio/speech",
                json={"model": "kokoro", "input": unique_text, "voice": "af_heart", "response_format": "mp3"},
                timeout=10
            )
            cache_miss_time = time.time() - start_time
            
            # Cache hit test
            start_time = time.time()
            response = requests.post(
                "http://localhost:8354/v1/audio/speech",
                json={"model": "kokoro", "input": unique_text, "voice": "af_heart", "response_format": "mp3"},
                timeout=10
            )
            cache_hit_time = time.time() - start_time
            
            performance_results['cache_miss_time'] = cache_miss_time
            performance_results['cache_hit_time'] = cache_hit_time
            performance_results['speedup'] = cache_miss_time / cache_hit_time if cache_hit_time > 0 else 0
            
            # Performance scoring
            if cache_hit_time < 0.1:  # 100ms
                self.score += 2
                print(f"   ✅ Cache Hit Performance: EXCELLENT ({cache_hit_time:.3f}s)")
            elif cache_hit_time < 0.5:  # 500ms
                self.score += 1
                print(f"   ⚡ Cache Hit Performance: GOOD ({cache_hit_time:.3f}s)")
            else:
                print(f"   ⚠️ Cache Hit Performance: NEEDS IMPROVEMENT ({cache_hit_time:.3f}s)")
            
            if cache_miss_time < 5.0:  # 5s
                self.score += 1
                print(f"   ✅ Cache Miss Performance: GOOD ({cache_miss_time:.3f}s)")
            else:
                print(f"   ⚠️ Cache Miss Performance: SLOW ({cache_miss_time:.3f}s)")
            
            self.max_score += 3
            
        except Exception as e:
            performance_results['error'] = str(e)
            print(f"   ❌ Performance Test Failed: {e}")
            self.max_score += 3
        
        return performance_results
    
    def assess_reliability(self) -> Dict[str, Any]:
        """Assess system reliability"""
        print("\n🛡️ Assessing Reliability")
        print("-" * 40)
        
        reliability_results = {}
        
        # Test health endpoint
        try:
            response = requests.get("http://localhost:8354/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                reliability_results['health_check'] = True
                reliability_results['health_data'] = health_data
                self.score += 1
                print("   ✅ Health Check: OPERATIONAL")
            else:
                reliability_results['health_check'] = False
                print(f"   ❌ Health Check: FAILED ({response.status_code})")
            self.max_score += 1
        except Exception as e:
            reliability_results['health_check'] = False
            reliability_results['health_error'] = str(e)
            print(f"   ❌ Health Check: ERROR - {e}")
            self.max_score += 1
        
        # Test concurrent requests
        try:
            import threading
            import queue
            
            results_queue = queue.Queue()
            
            def make_request(request_id):
                try:
                    response = requests.post(
                        "http://localhost:8354/v1/audio/speech",
                        json={"model": "kokoro", "input": f"Concurrent test {request_id}", "voice": "af_heart", "response_format": "mp3"},
                        timeout=10
                    )
                    results_queue.put({'id': request_id, 'success': response.status_code == 200})
                except Exception as e:
                    results_queue.put({'id': request_id, 'success': False, 'error': str(e)})
            
            # Launch 5 concurrent requests
            threads = []
            for i in range(5):
                thread = threading.Thread(target=make_request, args=(i,))
                threads.append(thread)
                thread.start()
            
            # Wait for completion
            for thread in threads:
                thread.join(timeout=15)
            
            # Collect results
            concurrent_results = []
            while not results_queue.empty():
                concurrent_results.append(results_queue.get())
            
            successful = sum(1 for r in concurrent_results if r.get('success', False))
            reliability_results['concurrent_test'] = {
                'total': len(concurrent_results),
                'successful': successful,
                'success_rate': successful / len(concurrent_results) if concurrent_results else 0
            }
            
            if successful >= 4:  # 80% success rate
                self.score += 1
                print(f"   ✅ Concurrent Requests: RELIABLE ({successful}/5 successful)")
            else:
                print(f"   ⚠️ Concurrent Requests: UNRELIABLE ({successful}/5 successful)")
            
            self.max_score += 1
            
        except Exception as e:
            reliability_results['concurrent_error'] = str(e)
            print(f"   ❌ Concurrent Test: ERROR - {e}")
            self.max_score += 1
        
        return reliability_results
    
    def assess_configuration(self) -> Dict[str, Any]:
        """Assess configuration management"""
        print("\n⚙️ Assessing Configuration")
        print("-" * 40)
        
        config_results = {}
        
        # Check config file exists (check both locations)
        config_file = None
        if Path("config.json").exists():
            config_file = Path("config.json")
        elif Path("LiteTTS/config.json").exists():
            config_file = Path("LiteTTS/config.json")

        if config_file:
            try:
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                
                required_sections = ["model", "voice", "audio", "server", "performance", "tokenizer"]
                missing_sections = [s for s in required_sections if s not in config_data]
                
                config_results['config_file_exists'] = True
                config_results['sections_present'] = len(required_sections) - len(missing_sections)
                config_results['total_sections'] = len(required_sections)
                config_results['missing_sections'] = missing_sections
                
                if not missing_sections:
                    self.score += 1
                    print("   ✅ Configuration: COMPLETE")
                else:
                    print(f"   ⚠️ Configuration: INCOMPLETE (missing: {missing_sections})")
                
                self.max_score += 1
                
            except Exception as e:
                config_results['config_error'] = str(e)
                print(f"   ❌ Configuration: ERROR - {e}")
                self.max_score += 1
        else:
            config_results['config_file_exists'] = False
            print("   ❌ Configuration: FILE MISSING")
            self.max_score += 1
        
        return config_results
    
    def assess_documentation(self) -> Dict[str, Any]:
        """Assess documentation quality"""
        print("\n📚 Assessing Documentation")
        print("-" * 40)
        
        doc_results = {}
        
        # Check for key documentation files
        key_docs = {
            'README.md': 'Main documentation',
            'docs/SYSTEM_STATUS.md': 'System status',
            'LiteTTS/config.json': 'Configuration',
            'pyproject.toml': 'Project configuration'
        }
        
        present_docs = 0
        for doc_path, description in key_docs.items():
            if Path(doc_path).exists():
                present_docs += 1
                print(f"   ✅ {description}: PRESENT")
            else:
                print(f"   ❌ {description}: MISSING")
        
        doc_results['key_docs_present'] = present_docs
        doc_results['total_key_docs'] = len(key_docs)
        
        if present_docs >= len(key_docs) * 0.8:  # 80% of key docs
            self.score += 1
        
        self.max_score += 1
        
        return doc_results
    
    def _test_basic_tts(self) -> Dict[str, Any]:
        """Test basic TTS functionality"""
        response = requests.post(
            "http://localhost:8354/v1/audio/speech",
            json={"model": "kokoro", "input": "Hello, world!", "voice": "af_heart", "response_format": "mp3"},
            timeout=10
        )
        return {
            'success': response.status_code == 200,
            'status_code': response.status_code,
            'audio_size': len(response.content) if response.status_code == 200 else 0
        }
    
    def _test_multiple_voices(self) -> Dict[str, Any]:
        """Test multiple voice support"""
        voices = ["af_heart", "am_puck"]
        results = []
        
        for voice in voices:
            response = requests.post(
                "http://localhost:8354/v1/audio/speech",
                json={"model": "kokoro", "input": "Test voice", "voice": voice, "response_format": "mp3"},
                timeout=10
            )
            results.append(response.status_code == 200)
        
        return {
            'success': all(results),
            'voices_tested': len(voices),
            'voices_working': sum(results)
        }
    
    def _test_different_formats(self) -> Dict[str, Any]:
        """Test different audio formats"""
        formats = ["mp3", "wav"]
        results = []
        
        for fmt in formats:
            response = requests.post(
                "http://localhost:8354/v1/audio/speech",
                json={"model": "kokoro", "input": "Format test", "voice": "af_heart", "response_format": fmt},
                timeout=10
            )
            results.append(response.status_code == 200)
        
        return {
            'success': all(results),
            'formats_tested': len(formats),
            'formats_working': sum(results)
        }
    
    def _test_speed_control(self) -> Dict[str, Any]:
        """Test speed control"""
        response = requests.post(
            "http://localhost:8354/v1/audio/speech",
            json={"model": "kokoro", "input": "Speed test", "voice": "af_heart", "speed": 1.5, "response_format": "mp3"},
            timeout=10
        )
        return {
            'success': response.status_code == 200,
            'status_code': response.status_code
        }
    
    def _test_error_handling(self) -> Dict[str, Any]:
        """Test error handling"""
        # Test with invalid voice
        response = requests.post(
            "http://localhost:8354/v1/audio/speech",
            json={"model": "kokoro", "input": "Error test", "voice": "invalid_voice", "response_format": "mp3"},
            timeout=10
        )
        return {
            'success': response.status_code in [400, 422],  # Should return error
            'status_code': response.status_code
        }
    
    def generate_final_report(self) -> Dict[str, Any]:
        """Generate final production readiness report"""
        print("\n" + "=" * 60)
        print("📋 FINAL PRODUCTION READINESS ASSESSMENT")
        print("=" * 60)
        
        # Calculate overall score
        percentage = (self.score / self.max_score * 100) if self.max_score > 0 else 0
        
        print(f"\n📊 Overall Score: {self.score}/{self.max_score} ({percentage:.1f}%)")
        
        # Determine readiness level
        if percentage >= 90:
            readiness = "✅ PRODUCTION READY"
            recommendation = "Deploy to production immediately"
        elif percentage >= 80:
            readiness = "⚡ MOSTLY READY"
            recommendation = "Address minor issues before production deployment"
        elif percentage >= 70:
            readiness = "⚠️ NEEDS IMPROVEMENT"
            recommendation = "Address critical issues before production deployment"
        else:
            readiness = "❌ NOT READY"
            recommendation = "Significant work required before production deployment"
        
        print(f"🎯 Readiness Level: {readiness}")
        print(f"💡 Recommendation: {recommendation}")
        
        return {
            'score': self.score,
            'max_score': self.max_score,
            'percentage': percentage,
            'readiness': readiness,
            'recommendation': recommendation,
            'timestamp': time.time()
        }

def main():
    """Main assessment function"""
    print("🚀 Starting Production Readiness Assessment")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8354/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server not accessible - please start the server first")
            return
    except:
        print("❌ Server not accessible - please start the server first")
        print("💡 Run: python LiteTTS/start_server.py")
        return
    
    print("✅ Server is accessible - beginning assessment")
    
    # Run assessment
    assessment = ProductionReadinessAssessment()
    
    # Run all assessments
    core_results = assessment.assess_core_functionality()
    performance_results = assessment.assess_performance()
    reliability_results = assessment.assess_reliability()
    config_results = assessment.assess_configuration()
    doc_results = assessment.assess_documentation()
    
    # Generate final report
    final_report = assessment.generate_final_report()
    
    # Save results
    results = {
        'core_functionality': core_results,
        'performance': performance_results,
        'reliability': reliability_results,
        'configuration': config_results,
        'documentation': doc_results,
        'final_report': final_report
    }
    
    with open('production_readiness_report.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: production_readiness_report.json")
    print("\n🎉 Assessment complete!")

if __name__ == "__main__":
    main()
