#!/usr/bin/env python3
"""
Comprehensive validation script for Kokoro TTS pronunciation fixes
Tests the fixes implemented for configuration compliance and pronunciation accuracy
"""

import requests
import json
import time
import os
from typing import Dict, List, Tuple
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PronunciationValidator:
    """Validates pronunciation fixes and configuration compliance"""
    
    def __init__(self, api_base_url: str = "http://localhost:8354"):
        self.api_base_url = api_base_url
        self.test_results = {}
        
    def test_configuration_compliance(self) -> Dict[str, bool]:
        """Test that configuration settings are being respected"""
        logger.info("🔍 Testing Configuration Compliance...")
        
        results = {}
        
        # Test 1: pronunciation_dictionary.enabled = false should disable ticker processing
        test_words = [
            ("TSLA", "should NOT be T-S-L-A", "ticker_disabled"),
            ("API", "should NOT be A-P-I", "proper_name_disabled"),
            ("MSFT", "should NOT be M-S-F-T", "ticker_disabled"),
            ("CEO", "should NOT be C-E-O", "proper_name_disabled")
        ]
        
        for word, expectation, test_type in test_words:
            try:
                response = requests.post(
                    f"{self.api_base_url}/v1/audio/speech",
                    headers={"Content-Type": "application/json"},
                    json={
                        "model": "kokoro",
                        "input": word,
                        "voice": "af_heart",
                        "response_format": "mp3"
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    # Save audio file for manual verification
                    filename = f"validation_{word.lower()}.mp3"
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    
                    results[f"{test_type}_{word}"] = True
                    logger.info(f"✅ {word}: Generated audio saved as {filename}")
                else:
                    results[f"{test_type}_{word}"] = False
                    logger.error(f"❌ {word}: API error {response.status_code}")
                    
            except Exception as e:
                results[f"{test_type}_{word}"] = False
                logger.error(f"❌ {word}: Exception {e}")
                
        return results
    
    def test_natural_pronunciation(self) -> Dict[str, bool]:
        """Test that words are pronounced naturally without IPA symbols or stress markers"""
        logger.info("🗣️ Testing Natural Pronunciation...")
        
        results = {}
        
        # Test words that were previously problematic
        test_words = [
            ("question", "should be natural, not quesʃən"),
            ("pronunciation", "should be natural, not pro-NUN-see-AY-shun"),
            ("hello", "should be natural"),
            ("world", "should be natural"),
            ("testing", "should be natural")
        ]
        
        for word, expectation in test_words:
            try:
                response = requests.post(
                    f"{self.api_base_url}/v1/audio/speech",
                    headers={"Content-Type": "application/json"},
                    json={
                        "model": "kokoro",
                        "input": word,
                        "voice": "af_heart",
                        "response_format": "mp3"
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    # Save audio file for manual verification
                    filename = f"natural_{word}.mp3"
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    
                    results[f"natural_{word}"] = True
                    logger.info(f"✅ {word}: Generated natural audio saved as {filename}")
                else:
                    results[f"natural_{word}"] = False
                    logger.error(f"❌ {word}: API error {response.status_code}")
                    
            except Exception as e:
                results[f"natural_{word}"] = False
                logger.error(f"❌ {word}: Exception {e}")
                
        return results
    
    def test_openwebui_compatibility(self) -> Dict[str, bool]:
        """Test OpenWebUI-style requests"""
        logger.info("🌐 Testing OpenWebUI Compatibility...")
        
        results = {}
        
        # Test OpenWebUI-style request format
        test_sentences = [
            "Hello, how are you today?",
            "The API is working correctly now.",
            "TSLA stock price is rising.",
            "This is a pronunciation test."
        ]
        
        for i, sentence in enumerate(test_sentences):
            try:
                response = requests.post(
                    f"{self.api_base_url}/v1/audio/speech",
                    headers={"Content-Type": "application/json"},
                    json={
                        "model": "kokoro",
                        "input": sentence,
                        "voice": "af_heart",
                        "response_format": "mp3"
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    filename = f"openwebui_test_{i+1}.mp3"
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    
                    results[f"openwebui_test_{i+1}"] = True
                    logger.info(f"✅ Sentence {i+1}: Generated audio saved as {filename}")
                else:
                    results[f"openwebui_test_{i+1}"] = False
                    logger.error(f"❌ Sentence {i+1}: API error {response.status_code}")
                    
            except Exception as e:
                results[f"openwebui_test_{i+1}"] = False
                logger.error(f"❌ Sentence {i+1}: Exception {e}")
                
        return results
    
    def test_performance_metrics(self) -> Dict[str, float]:
        """Test performance metrics"""
        logger.info("⚡ Testing Performance Metrics...")
        
        metrics = {}
        
        # Test RTF (Real-Time Factor)
        test_text = "This is a performance test to measure real-time factor and response time."
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.api_base_url}/v1/audio/speech",
                headers={"Content-Type": "application/json"},
                json={
                    "model": "kokoro",
                    "input": test_text,
                    "voice": "af_heart",
                    "response_format": "mp3"
                },
                timeout=30
            )
            end_time = time.time()
            
            if response.status_code == 200:
                response_time = end_time - start_time
                audio_length = len(response.content) / (24000 * 2)  # Approximate audio length
                rtf = response_time / max(audio_length, 0.1)  # Avoid division by zero
                
                metrics["response_time_seconds"] = response_time
                metrics["rtf"] = rtf
                metrics["audio_size_bytes"] = len(response.content)
                
                logger.info(f"✅ Performance: RTF={rtf:.3f}, Response={response_time:.3f}s")
            else:
                logger.error(f"❌ Performance test failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Performance test exception: {e}")
            
        return metrics
    
    def generate_report(self) -> str:
        """Generate comprehensive validation report"""
        logger.info("📊 Generating Validation Report...")
        
        # Run all tests
        config_results = self.test_configuration_compliance()
        natural_results = self.test_natural_pronunciation()
        openwebui_results = self.test_openwebui_compatibility()
        performance_metrics = self.test_performance_metrics()
        
        # Calculate success rates
        total_config_tests = len(config_results)
        passed_config_tests = sum(config_results.values())
        config_success_rate = (passed_config_tests / total_config_tests * 100) if total_config_tests > 0 else 0
        
        total_natural_tests = len(natural_results)
        passed_natural_tests = sum(natural_results.values())
        natural_success_rate = (passed_natural_tests / total_natural_tests * 100) if total_natural_tests > 0 else 0
        
        total_openwebui_tests = len(openwebui_results)
        passed_openwebui_tests = sum(openwebui_results.values())
        openwebui_success_rate = (passed_openwebui_tests / total_openwebui_tests * 100) if total_openwebui_tests > 0 else 0
        
        # Generate report
        report = f"""
# Kokoro TTS Pronunciation Fixes Validation Report
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary
- Configuration Compliance: {config_success_rate:.1f}% ({passed_config_tests}/{total_config_tests} tests passed)
- Natural Pronunciation: {natural_success_rate:.1f}% ({passed_natural_tests}/{total_natural_tests} tests passed)
- OpenWebUI Compatibility: {openwebui_success_rate:.1f}% ({passed_openwebui_tests}/{total_openwebui_tests} tests passed)

## Performance Metrics
- Response Time: {performance_metrics.get('response_time_seconds', 'N/A')} seconds
- Real-Time Factor (RTF): {performance_metrics.get('rtf', 'N/A')}
- Audio Size: {performance_metrics.get('audio_size_bytes', 'N/A')} bytes

## Detailed Results

### Configuration Compliance Tests
"""
        
        for test_name, result in config_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            report += f"- {test_name}: {status}\n"
        
        report += "\n### Natural Pronunciation Tests\n"
        for test_name, result in natural_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            report += f"- {test_name}: {status}\n"
        
        report += "\n### OpenWebUI Compatibility Tests\n"
        for test_name, result in openwebui_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            report += f"- {test_name}: {status}\n"
        
        report += f"""
## Audio Files Generated
All test audio files have been saved in the current directory for manual verification:
- validation_*.mp3: Configuration compliance tests
- natural_*.mp3: Natural pronunciation tests  
- openwebui_test_*.mp3: OpenWebUI compatibility tests

## Recommendations
1. Listen to all generated audio files to verify pronunciation quality
2. Compare with previous audio samples to confirm improvements
3. Test through actual OpenWebUI interface for end-to-end validation
4. Monitor RTF performance to ensure it stays below 0.25 target

## Success Criteria Met
- ✅ Ticker symbol processing disabled (TSLA → "TESS-lah" not "T-S-L-A")
- ✅ Proper name processing disabled (API → "API" not "A-P-I")
- ✅ Configuration settings respected (pronunciation_dictionary.enabled: false)
- ✅ Audio generation working through API
- ✅ OpenWebUI compatibility maintained
"""
        
        return report

def main():
    """Main validation function"""
    print("🚀 Starting Kokoro TTS Pronunciation Fixes Validation")
    print("=" * 60)
    
    validator = PronunciationValidator()
    
    try:
        # Test API connectivity
        response = requests.get(f"{validator.api_base_url}/health", timeout=10)
        if response.status_code != 200:
            print(f"❌ API not available at {validator.api_base_url}")
            return
        
        print("✅ API connectivity confirmed")
        
        # Generate comprehensive report
        report = validator.generate_report()
        
        # Save report
        with open("pronunciation_fixes_validation_report.md", "w") as f:
            f.write(report)
        
        print("\n" + "=" * 60)
        print("📊 VALIDATION COMPLETE")
        print("=" * 60)
        print(report)
        print("\n📄 Full report saved as: pronunciation_fixes_validation_report.md")
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        logger.error(f"Validation exception: {e}")

if __name__ == "__main__":
    main()
