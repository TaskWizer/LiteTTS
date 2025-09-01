#!/usr/bin/env python3
"""
Comprehensive Test Suite for Kokoro ONNX TTS API

Tests all new functionality including SSML background noise, voice showcase,
RTF optimization, pronunciation fixes, and dashboard functionality.
"""

import requests
import time
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Tuple
import subprocess
import sys

class ComprehensiveTestSuite:
    """Comprehensive test suite for all TTS functionality"""
    
    def __init__(self, base_url: str = "http://localhost:8354"):
        self.base_url = base_url
        self.test_results = {
            'summary': {
                'total_tests': 0,
                'passed': 0,
                'failed': 0,
                'skipped': 0,
                'success_rate': 0.0
            },
            'test_suites': {},
            'performance_metrics': {},
            'regression_tests': {}
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all comprehensive tests"""
        
        print("🧪 Comprehensive Test Suite - Kokoro ONNX TTS API")
        print("=" * 50)
        
        # Check server availability
        if not self._check_server_availability():
            print("❌ Server not available - skipping tests")
            return self.test_results
        
        # Test suites
        test_suites = [
            ("Basic API Functionality", self.test_basic_api),
            ("SSML Background Noise", self.test_ssml_background),
            ("Voice Showcase", self.test_voice_showcase),
            ("Dashboard Analytics", self.test_dashboard),
            ("Pronunciation Accuracy", self.test_pronunciation),
            ("Performance & RTF", self.test_performance),
            ("Error Handling", self.test_error_handling),
            ("Configuration", self.test_configuration),
            ("Regression Tests", self.test_regression)
        ]
        
        for suite_name, test_function in test_suites:
            print(f"\n🔍 Testing: {suite_name}")
            print("-" * 30)
            
            try:
                suite_results = test_function()
                self.test_results['test_suites'][suite_name] = suite_results
                
                # Update summary
                self.test_results['summary']['total_tests'] += suite_results.get('total', 0)
                self.test_results['summary']['passed'] += suite_results.get('passed', 0)
                self.test_results['summary']['failed'] += suite_results.get('failed', 0)
                self.test_results['summary']['skipped'] += suite_results.get('skipped', 0)
                
                # Print suite summary
                passed = suite_results.get('passed', 0)
                total = suite_results.get('total', 0)
                if total > 0:
                    success_rate = (passed / total) * 100
                    status = "✅" if success_rate >= 90 else "⚠️" if success_rate >= 70 else "❌"
                    print(f"   {status} {suite_name}: {passed}/{total} ({success_rate:.1f}%)")
                
            except Exception as e:
                print(f"   ❌ Error in {suite_name}: {e}")
                self.test_results['test_suites'][suite_name] = {
                    'total': 1, 'passed': 0, 'failed': 1, 'error': str(e)
                }
        
        # Calculate overall success rate
        total = self.test_results['summary']['total_tests']
        passed = self.test_results['summary']['passed']
        if total > 0:
            self.test_results['summary']['success_rate'] = (passed / total) * 100
        
        return self.test_results
    
    def test_basic_api(self) -> Dict[str, Any]:
        """Test basic API functionality"""
        
        results = {'total': 0, 'passed': 0, 'failed': 0, 'tests': []}
        
        # Test 1: Get voices
        results['total'] += 1
        try:
            response = requests.get(f"{self.base_url}/v1/voices", timeout=10)
            if response.status_code == 200 and 'voices' in response.json():
                results['passed'] += 1
                results['tests'].append({'name': 'get_voices', 'status': 'passed'})
            else:
                results['failed'] += 1
                results['tests'].append({'name': 'get_voices', 'status': 'failed', 'error': f'HTTP {response.status_code}'})
        except Exception as e:
            results['failed'] += 1
            results['tests'].append({'name': 'get_voices', 'status': 'failed', 'error': str(e)})
        
        # Test 2: Basic TTS synthesis
        results['total'] += 1
        try:
            response = requests.post(
                f"{self.base_url}/v1/audio/speech",
                json={"input": "Hello world", "voice": "af_heart", "response_format": "mp3"},
                timeout=30
            )
            if response.status_code == 200 and len(response.content) > 1000:
                results['passed'] += 1
                results['tests'].append({'name': 'basic_tts', 'status': 'passed'})
            else:
                results['failed'] += 1
                results['tests'].append({'name': 'basic_tts', 'status': 'failed', 'error': f'HTTP {response.status_code} or small audio'})
        except Exception as e:
            results['failed'] += 1
            results['tests'].append({'name': 'basic_tts', 'status': 'failed', 'error': str(e)})
        
        # Test 3: Voice validation
        results['total'] += 1
        try:
            response = requests.post(
                f"{self.base_url}/v1/audio/speech",
                json={"input": "Test", "voice": "invalid_voice", "response_format": "mp3"},
                timeout=10
            )
            if response.status_code == 400:  # Should return error for invalid voice
                results['passed'] += 1
                results['tests'].append({'name': 'voice_validation', 'status': 'passed'})
            else:
                results['failed'] += 1
                results['tests'].append({'name': 'voice_validation', 'status': 'failed', 'error': f'Expected 400, got {response.status_code}'})
        except Exception as e:
            results['failed'] += 1
            results['tests'].append({'name': 'voice_validation', 'status': 'failed', 'error': str(e)})
        
        return results
    
    def test_ssml_background(self) -> Dict[str, Any]:
        """Test SSML background noise functionality"""
        
        results = {'total': 0, 'passed': 0, 'failed': 0, 'tests': []}
        
        # Test background types
        background_types = ["nature", "rain", "coffee_shop", "office", "wind"]
        
        for bg_type in background_types:
            results['total'] += 1
            try:
                ssml_text = f'<speak><background type="{bg_type}" volume="20">Testing {bg_type} background sounds.</background></speak>'
                response = requests.post(
                    f"{self.base_url}/v1/audio/speech",
                    json={"input": ssml_text, "voice": "af_heart", "response_format": "mp3"},
                    timeout=30
                )
                
                if response.status_code == 200 and len(response.content) > 5000:  # Background audio should be larger
                    results['passed'] += 1
                    results['tests'].append({'name': f'ssml_background_{bg_type}', 'status': 'passed'})
                else:
                    results['failed'] += 1
                    results['tests'].append({'name': f'ssml_background_{bg_type}', 'status': 'failed', 'error': f'HTTP {response.status_code} or small audio'})
            except Exception as e:
                results['failed'] += 1
                results['tests'].append({'name': f'ssml_background_{bg_type}', 'status': 'failed', 'error': str(e)})
        
        # Test volume control
        results['total'] += 1
        try:
            ssml_text = '<speak><background type="rain" volume="50">Testing volume control.</background></speak>'
            response = requests.post(
                f"{self.base_url}/v1/audio/speech",
                json={"input": ssml_text, "voice": "af_heart", "response_format": "mp3"},
                timeout=30
            )
            
            if response.status_code == 200:
                results['passed'] += 1
                results['tests'].append({'name': 'ssml_volume_control', 'status': 'passed'})
            else:
                results['failed'] += 1
                results['tests'].append({'name': 'ssml_volume_control', 'status': 'failed', 'error': f'HTTP {response.status_code}'})
        except Exception as e:
            results['failed'] += 1
            results['tests'].append({'name': 'ssml_volume_control', 'status': 'failed', 'error': str(e)})
        
        return results
    
    def test_voice_showcase(self) -> Dict[str, Any]:
        """Test voice showcase functionality"""
        
        results = {'total': 0, 'passed': 0, 'failed': 0, 'tests': []}
        
        # Test 1: Voice showcase files exist
        results['total'] += 1
        showcase_path = Path("docs/voices/README.md")
        if showcase_path.exists():
            results['passed'] += 1
            results['tests'].append({'name': 'showcase_readme_exists', 'status': 'passed'})
        else:
            results['failed'] += 1
            results['tests'].append({'name': 'showcase_readme_exists', 'status': 'failed', 'error': 'README.md not found'})
        
        # Test 2: Audio samples exist
        results['total'] += 1
        audio_samples = list(Path("docs/voices").glob("*.mp3"))
        if len(audio_samples) >= 50:  # Should have most voice samples
            results['passed'] += 1
            results['tests'].append({'name': 'audio_samples_exist', 'status': 'passed', 'count': len(audio_samples)})
        else:
            results['failed'] += 1
            results['tests'].append({'name': 'audio_samples_exist', 'status': 'failed', 'error': f'Only {len(audio_samples)} samples found'})
        
        # Test 3: README content validation
        results['total'] += 1
        if showcase_path.exists():
            try:
                with open(showcase_path, 'r') as f:
                    content = f.read()
                
                if 'Voice Showcase' in content and 'audio controls' in content:
                    results['passed'] += 1
                    results['tests'].append({'name': 'showcase_content_valid', 'status': 'passed'})
                else:
                    results['failed'] += 1
                    results['tests'].append({'name': 'showcase_content_valid', 'status': 'failed', 'error': 'Missing expected content'})
            except Exception as e:
                results['failed'] += 1
                results['tests'].append({'name': 'showcase_content_valid', 'status': 'failed', 'error': str(e)})
        else:
            results['failed'] += 1
            results['tests'].append({'name': 'showcase_content_valid', 'status': 'failed', 'error': 'README.md not found'})
        
        return results
    
    def test_dashboard(self) -> Dict[str, Any]:
        """Test dashboard analytics functionality"""
        
        results = {'total': 0, 'passed': 0, 'failed': 0, 'tests': []}
        
        # Test 1: Dashboard accessibility
        results['total'] += 1
        try:
            response = requests.get(f"{self.base_url}/dashboard", timeout=10)
            if response.status_code == 200:
                results['passed'] += 1
                results['tests'].append({'name': 'dashboard_accessible', 'status': 'passed'})
            else:
                results['failed'] += 1
                results['tests'].append({'name': 'dashboard_accessible', 'status': 'failed', 'error': f'HTTP {response.status_code}'})
        except Exception as e:
            results['failed'] += 1
            results['tests'].append({'name': 'dashboard_accessible', 'status': 'failed', 'error': str(e)})
        
        # Test 2: Dashboard content
        results['total'] += 1
        try:
            response = requests.get(f"{self.base_url}/dashboard", timeout=10)
            if response.status_code == 200:
                content = response.text
                if 'Performance Metrics' in content and 'RTF' in content:
                    results['passed'] += 1
                    results['tests'].append({'name': 'dashboard_content', 'status': 'passed'})
                else:
                    results['failed'] += 1
                    results['tests'].append({'name': 'dashboard_content', 'status': 'failed', 'error': 'Missing expected metrics'})
            else:
                results['failed'] += 1
                results['tests'].append({'name': 'dashboard_content', 'status': 'failed', 'error': f'HTTP {response.status_code}'})
        except Exception as e:
            results['failed'] += 1
            results['tests'].append({'name': 'dashboard_content', 'status': 'failed', 'error': str(e)})
        
        return results
    
    def test_pronunciation(self) -> Dict[str, Any]:
        """Test pronunciation accuracy fixes"""
        
        results = {'total': 0, 'passed': 0, 'failed': 0, 'tests': []}
        
        # Test problematic words that were fixed
        test_cases = [
            ("Hello world", "basic_pronunciation"),
            ("What's happening today?", "contractions"),
            ("The asterisk symbol is useful.", "asterisk_pronunciation"),
            ("For example, this works.", "abbreviation_handling"),
            ("The boy's toy is fun.", "possessive_handling")
        ]
        
        for text, test_name in test_cases:
            results['total'] += 1
            try:
                response = requests.post(
                    f"{self.base_url}/v1/audio/speech",
                    json={"input": text, "voice": "af_heart", "response_format": "mp3"},
                    timeout=30
                )
                
                if response.status_code == 200 and len(response.content) > 1000:
                    results['passed'] += 1
                    results['tests'].append({'name': test_name, 'status': 'passed'})
                else:
                    results['failed'] += 1
                    results['tests'].append({'name': test_name, 'status': 'failed', 'error': f'HTTP {response.status_code} or small audio'})
            except Exception as e:
                results['failed'] += 1
                results['tests'].append({'name': test_name, 'status': 'failed', 'error': str(e)})
        
        return results
    
    def test_performance(self) -> Dict[str, Any]:
        """Test performance and RTF metrics"""
        
        results = {'total': 0, 'passed': 0, 'failed': 0, 'tests': [], 'metrics': {}}
        
        # Test 1: RTF measurement
        results['total'] += 1
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/v1/audio/speech",
                json={"input": "This is a test for RTF measurement.", "voice": "af_heart", "response_format": "mp3"},
                timeout=30
            )
            end_time = time.time()
            
            if response.status_code == 200:
                generation_time = end_time - start_time
                audio_size = len(response.content)
                estimated_duration = audio_size / 16000  # Rough estimate
                rtf = generation_time / estimated_duration if estimated_duration > 0 else 0
                
                results['metrics']['rtf'] = rtf
                results['metrics']['generation_time'] = generation_time
                results['metrics']['audio_size'] = audio_size
                
                if rtf < 1.0:  # Should be faster than real-time
                    results['passed'] += 1
                    results['tests'].append({'name': 'rtf_performance', 'status': 'passed', 'rtf': rtf})
                else:
                    results['failed'] += 1
                    results['tests'].append({'name': 'rtf_performance', 'status': 'failed', 'error': f'RTF too high: {rtf}'})
            else:
                results['failed'] += 1
                results['tests'].append({'name': 'rtf_performance', 'status': 'failed', 'error': f'HTTP {response.status_code}'})
        except Exception as e:
            results['failed'] += 1
            results['tests'].append({'name': 'rtf_performance', 'status': 'failed', 'error': str(e)})
        
        # Test 2: Cache performance
        results['total'] += 1
        try:
            # First request (cache miss)
            start_time = time.time()
            response1 = requests.post(
                f"{self.base_url}/v1/audio/speech",
                json={"input": "Cache test phrase", "voice": "af_heart", "response_format": "mp3"},
                timeout=30
            )
            first_time = time.time() - start_time
            
            # Second request (cache hit)
            start_time = time.time()
            response2 = requests.post(
                f"{self.base_url}/v1/audio/speech",
                json={"input": "Cache test phrase", "voice": "af_heart", "response_format": "mp3"},
                timeout=30
            )
            second_time = time.time() - start_time
            
            if response1.status_code == 200 and response2.status_code == 200:
                speedup = first_time / second_time if second_time > 0 else 0
                results['metrics']['cache_speedup'] = speedup
                results['metrics']['first_request_time'] = first_time
                results['metrics']['second_request_time'] = second_time
                
                if speedup > 2.0:  # Cache should provide significant speedup
                    results['passed'] += 1
                    results['tests'].append({'name': 'cache_performance', 'status': 'passed', 'speedup': speedup})
                else:
                    results['failed'] += 1
                    results['tests'].append({'name': 'cache_performance', 'status': 'failed', 'error': f'Low speedup: {speedup}'})
            else:
                results['failed'] += 1
                results['tests'].append({'name': 'cache_performance', 'status': 'failed', 'error': 'HTTP errors'})
        except Exception as e:
            results['failed'] += 1
            results['tests'].append({'name': 'cache_performance', 'status': 'failed', 'error': str(e)})
        
        return results
    
    def test_error_handling(self) -> Dict[str, Any]:
        """Test error handling and edge cases"""
        
        results = {'total': 0, 'passed': 0, 'failed': 0, 'tests': []}
        
        # Test cases that should return specific errors
        error_cases = [
            ({"input": "", "voice": "af_heart", "response_format": "mp3"}, "empty_input"),
            ({"input": "Test", "voice": "nonexistent", "response_format": "mp3"}, "invalid_voice"),
            ({"input": "Test", "voice": "af_heart", "response_format": "invalid"}, "invalid_format"),
            ({"voice": "af_heart", "response_format": "mp3"}, "missing_input"),
        ]
        
        for payload, test_name in error_cases:
            results['total'] += 1
            try:
                response = requests.post(
                    f"{self.base_url}/v1/audio/speech",
                    json=payload,
                    timeout=10
                )
                
                if response.status_code >= 400:  # Should return error
                    results['passed'] += 1
                    results['tests'].append({'name': test_name, 'status': 'passed', 'status_code': response.status_code})
                else:
                    results['failed'] += 1
                    results['tests'].append({'name': test_name, 'status': 'failed', 'error': f'Expected error, got {response.status_code}'})
            except Exception as e:
                results['failed'] += 1
                results['tests'].append({'name': test_name, 'status': 'failed', 'error': str(e)})
        
        return results
    
    def test_configuration(self) -> Dict[str, Any]:
        """Test configuration and setup"""
        
        results = {'total': 0, 'passed': 0, 'failed': 0, 'tests': []}
        
        # Test 1: Config file exists
        results['total'] += 1
        config_path = Path("config.json")
        if config_path.exists():
            results['passed'] += 1
            results['tests'].append({'name': 'config_file_exists', 'status': 'passed'})
        else:
            results['failed'] += 1
            results['tests'].append({'name': 'config_file_exists', 'status': 'failed', 'error': 'config.json not found'})
        
        # Test 2: Port configuration
        results['total'] += 1
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                if config.get('port') == 8080:
                    results['passed'] += 1
                    results['tests'].append({'name': 'port_configuration', 'status': 'passed'})
                else:
                    results['failed'] += 1
                    results['tests'].append({'name': 'port_configuration', 'status': 'failed', 'error': f'Port is {config.get("port")}, expected 8080'})
            except Exception as e:
                results['failed'] += 1
                results['tests'].append({'name': 'port_configuration', 'status': 'failed', 'error': str(e)})
        else:
            results['failed'] += 1
            results['tests'].append({'name': 'port_configuration', 'status': 'failed', 'error': 'config.json not found'})
        
        return results
    
    def test_regression(self) -> Dict[str, Any]:
        """Test for regressions in existing functionality"""
        
        results = {'total': 0, 'passed': 0, 'failed': 0, 'tests': []}
        
        # Test that basic functionality still works after all changes
        regression_tests = [
            ("Hello world", "af_heart", "basic_regression"),
            ("This is a longer sentence to test.", "am_onyx", "male_voice_regression"),
            ("Testing British accent.", "bf_alice", "british_voice_regression"),
            ("日本語のテスト", "jf_alpha", "japanese_voice_regression"),
        ]
        
        for text, voice, test_name in regression_tests:
            results['total'] += 1
            try:
                response = requests.post(
                    f"{self.base_url}/v1/audio/speech",
                    json={"input": text, "voice": voice, "response_format": "mp3"},
                    timeout=30
                )
                
                if response.status_code == 200 and len(response.content) > 1000:
                    results['passed'] += 1
                    results['tests'].append({'name': test_name, 'status': 'passed'})
                else:
                    results['failed'] += 1
                    results['tests'].append({'name': test_name, 'status': 'failed', 'error': f'HTTP {response.status_code} or small audio'})
            except Exception as e:
                results['failed'] += 1
                results['tests'].append({'name': test_name, 'status': 'failed', 'error': str(e)})
        
        return results
    
    def _check_server_availability(self) -> bool:
        """Check if the TTS server is running"""
        try:
            response = requests.get(f"{self.base_url}/v1/voices", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def save_results(self, output_file: str = "docs/comprehensive_test_results.json"):
        """Save test results to file"""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        print(f"\n📄 Test results saved: {output_file}")
    
    def print_summary(self):
        """Print test summary"""
        summary = self.test_results['summary']
        
        print(f"\n📊 COMPREHENSIVE TEST SUMMARY")
        print(f"=" * 35)
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']} ✅")
        print(f"Failed: {summary['failed']} ❌")
        print(f"Skipped: {summary['skipped']} ⏭️")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        
        # Overall status
        if summary['success_rate'] >= 95:
            print(f"Overall Status: 🟢 EXCELLENT")
        elif summary['success_rate'] >= 85:
            print(f"Overall Status: 🟡 GOOD")
        elif summary['success_rate'] >= 70:
            print(f"Overall Status: 🟠 FAIR")
        else:
            print(f"Overall Status: 🔴 NEEDS ATTENTION")

def main():
    """Run comprehensive test suite"""
    test_suite = ComprehensiveTestSuite()
    results = test_suite.run_all_tests()
    test_suite.save_results()
    test_suite.print_summary()
    
    return results

if __name__ == "__main__":
    main()
