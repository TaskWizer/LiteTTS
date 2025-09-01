#!/usr/bin/env python3
"""
Comprehensive System Audit for Kokoro TTS API
Validates all components, endpoints, and integrations
"""

import requests
import json
import time
import sys
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8354"

class SystemAuditor:
    """Comprehensive system auditor"""
    
    def __init__(self):
        self.results = {
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "server_status": {},
            "api_endpoints": {},
            "openwebui_integration": {},
            "performance": {},
            "code_quality": {},
            "configuration": {},
            "security": {},
            "overall_score": 0
        }
        self.total_checks = 0
        self.passed_checks = 0
    
    def audit_server_status(self) -> Dict[str, Any]:
        """Audit basic server status and health"""
        logger.info("🔍 Auditing server status...")
        
        checks = {
            "server_running": False,
            "health_endpoint": False,
            "response_time": 0.0,
            "memory_usage": "unknown",
            "cpu_usage": "unknown"
        }
        
        try:
            # Test server connectivity
            start_time = time.time()
            response = requests.get(f"{BASE_URL}/health", timeout=10)
            response_time = time.time() - start_time
            
            checks["server_running"] = True
            checks["response_time"] = response_time
            
            if response.status_code == 200:
                checks["health_endpoint"] = True
                health_data = response.json()
                logger.info(f"   ✅ Server healthy: {health_data.get('status', 'unknown')}")
            else:
                logger.warning(f"   ⚠️ Health endpoint returned {response.status_code}")
                
        except Exception as e:
            logger.error(f"   ❌ Server connectivity failed: {e}")
        
        # Try to get system metrics
        try:
            import psutil
            process = None
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if 'python' in proc.info['name'] and any('app.py' in arg for arg in proc.info['cmdline']):
                    process = proc
                    break
            
            if process:
                checks["memory_usage"] = f"{process.memory_info().rss / 1024 / 1024:.1f} MB"
                checks["cpu_usage"] = f"{process.cpu_percent():.1f}%"
                
        except ImportError:
            logger.debug("psutil not available for system metrics")
        except Exception as e:
            logger.debug(f"Could not get system metrics: {e}")
        
        self.total_checks += 2
        if checks["server_running"]:
            self.passed_checks += 1
        if checks["health_endpoint"]:
            self.passed_checks += 1
            
        return checks
    
    def audit_api_endpoints(self) -> Dict[str, Any]:
        """Audit all API endpoints"""
        logger.info("🔍 Auditing API endpoints...")
        
        endpoints_to_test = [
            {
                "name": "Health Check",
                "method": "GET",
                "url": "/health",
                "expected_status": 200
            },
            {
                "name": "Voice List",
                "method": "GET", 
                "url": "/v1/voices",
                "expected_status": 200
            },
            {
                "name": "TTS Speech",
                "method": "POST",
                "url": "/v1/audio/speech",
                "payload": {"input": "Test", "voice": "af_heart"},
                "expected_status": 200,
                "expected_content_type": "audio/mp3"
            },
            {
                "name": "TTS Stream",
                "method": "POST",
                "url": "/v1/audio/stream",
                "payload": {"input": "Test stream", "voice": "af_heart"},
                "expected_status": 200
            },
            {
                "name": "OpenWebUI Compatibility",
                "method": "POST",
                "url": "/v1/audio/stream/audio/speech",
                "payload": {"input": "Test compat", "voice": "af_heart"},
                "expected_status": 200
            }
        ]
        
        results = {}
        
        for endpoint in endpoints_to_test:
            logger.info(f"   Testing {endpoint['name']}...")
            
            try:
                start_time = time.time()
                
                if endpoint["method"] == "GET":
                    response = requests.get(f"{BASE_URL}{endpoint['url']}", timeout=30)
                else:
                    response = requests.post(
                        f"{BASE_URL}{endpoint['url']}",
                        json=endpoint.get("payload"),
                        headers={"Content-Type": "application/json"},
                        timeout=30
                    )
                
                response_time = time.time() - start_time
                
                result = {
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "content_type": response.headers.get("content-type", ""),
                    "content_length": len(response.content),
                    "success": response.status_code == endpoint["expected_status"]
                }
                
                # Additional checks
                if "expected_content_type" in endpoint:
                    result["content_type_match"] = endpoint["expected_content_type"] in result["content_type"]
                    result["success"] = result["success"] and result["content_type_match"]
                
                results[endpoint["name"]] = result
                
                if result["success"]:
                    logger.info(f"      ✅ SUCCESS: {response.status_code} in {response_time:.3f}s")
                    self.passed_checks += 1
                else:
                    logger.warning(f"      ❌ FAILED: {response.status_code} (expected {endpoint['expected_status']})")
                
                self.total_checks += 1
                
            except Exception as e:
                logger.error(f"      ❌ EXCEPTION: {e}")
                results[endpoint["name"]] = {
                    "error": str(e),
                    "success": False
                }
                self.total_checks += 1
        
        return results
    
    def audit_openwebui_integration(self) -> Dict[str, Any]:
        """Audit OpenWebUI integration specifically"""
        logger.info("🔍 Auditing OpenWebUI integration...")
        
        # Test various User-Agent strings
        user_agents = [
            "OpenWebUI/1.0",
            "Mozilla/5.0 OpenWebUI",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
            "Mozilla/5.0 (Android 12; Mobile; rv:109.0) Gecko/109.0 Firefox/109.0"
        ]
        
        results = {
            "user_agent_compatibility": {},
            "mobile_support": True,
            "streaming_support": True,
            "compatibility_routes": {}
        }
        
        # Test each user agent
        for ua in user_agents:
            try:
                response = requests.post(
                    f"{BASE_URL}/v1/audio/speech",
                    json={"input": "OpenWebUI test", "voice": "af_heart"},
                    headers={
                        "Content-Type": "application/json",
                        "User-Agent": ua
                    },
                    timeout=30
                )
                
                results["user_agent_compatibility"][ua] = {
                    "status": response.status_code,
                    "success": response.status_code == 200,
                    "content_length": len(response.content)
                }
                
                if response.status_code == 200:
                    self.passed_checks += 1
                
                self.total_checks += 1
                
            except Exception as e:
                results["user_agent_compatibility"][ua] = {
                    "error": str(e),
                    "success": False
                }
                self.total_checks += 1
        
        # Test compatibility routes
        compat_routes = [
            "/v1/audio/stream/audio/speech",
            "/v1/audio/speech/audio/speech"
        ]
        
        for route in compat_routes:
            try:
                response = requests.post(
                    f"{BASE_URL}{route}",
                    json={"input": "Compatibility test", "voice": "af_heart"},
                    headers={
                        "Content-Type": "application/json",
                        "User-Agent": "OpenWebUI/1.0"
                    },
                    timeout=30
                )
                
                results["compatibility_routes"][route] = {
                    "status": response.status_code,
                    "success": response.status_code == 200,
                    "content_length": len(response.content)
                }
                
                if response.status_code == 200:
                    self.passed_checks += 1
                
                self.total_checks += 1
                
            except Exception as e:
                results["compatibility_routes"][route] = {
                    "error": str(e),
                    "success": False
                }
                self.total_checks += 1
        
        return results
    
    def audit_performance(self) -> Dict[str, Any]:
        """Audit system performance"""
        logger.info("🔍 Auditing performance...")
        
        # Run a quick RTF benchmark
        try:
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/v1/audio/speech",
                json={
                    "input": "This is a performance test to measure the real-time factor of the TTS system.",
                    "voice": "af_heart"
                },
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            
            synthesis_time = time.time() - start_time
            
            if response.status_code == 200:
                # Estimate audio duration (rough calculation)
                audio_duration = len(response.content) / 24000.0 * 8  # Rough estimate
                rtf = synthesis_time / audio_duration if audio_duration > 0 else float('inf')
                
                performance_rating = "excellent" if rtf < 0.3 else "good" if rtf < 0.5 else "acceptable" if rtf < 1.0 else "poor"
                
                results = {
                    "rtf": rtf,
                    "synthesis_time": synthesis_time,
                    "estimated_audio_duration": audio_duration,
                    "performance_rating": performance_rating,
                    "response_size": len(response.content),
                    "success": True
                }
                
                if rtf < 1.0:  # RTF < 1.0 is real-time
                    self.passed_checks += 1
                
            else:
                results = {
                    "error": f"HTTP {response.status_code}",
                    "success": False
                }
            
            self.total_checks += 1
            
        except Exception as e:
            results = {
                "error": str(e),
                "success": False
            }
            self.total_checks += 1
        
        return results
    
    def audit_configuration(self) -> Dict[str, Any]:
        """Audit system configuration"""
        logger.info("🔍 Auditing configuration...")
        
        results = {
            "config_files": {},
            "environment_variables": {},
            "model_files": {}
        }
        
        # Check configuration files
        config_files = [
            "config.json",
            "override.json"
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r') as f:
                        config_data = json.load(f)
                    
                    results["config_files"][config_file] = {
                        "exists": True,
                        "valid_json": True,
                        "size": os.path.getsize(config_file)
                    }
                    self.passed_checks += 1
                    
                except Exception as e:
                    results["config_files"][config_file] = {
                        "exists": True,
                        "valid_json": False,
                        "error": str(e)
                    }
                
            else:
                results["config_files"][config_file] = {
                    "exists": False
                }
            
            self.total_checks += 1
        
        # Check important environment variables
        env_vars = [
            "OMP_NUM_THREADS",
            "ONNX_DISABLE_SPARSE_TENSORS",
            "ENVIRONMENT"
        ]
        
        for var in env_vars:
            value = os.environ.get(var)
            results["environment_variables"][var] = {
                "set": value is not None,
                "value": value
            }
            
            if value is not None:
                self.passed_checks += 1
            
            self.total_checks += 1
        
        # Check model files
        model_paths = [
            "LiteTTS/models/model_q4.onnx",
            "LiteTTS/voices/combined_voices.npz"
        ]
        
        for model_path in model_paths:
            if os.path.exists(model_path):
                results["model_files"][model_path] = {
                    "exists": True,
                    "size": os.path.getsize(model_path)
                }
                self.passed_checks += 1
            else:
                results["model_files"][model_path] = {
                    "exists": False
                }
            
            self.total_checks += 1
        
        return results
    
    def generate_report(self) -> str:
        """Generate a comprehensive audit report"""
        score = (self.passed_checks / self.total_checks * 100) if self.total_checks > 0 else 0
        self.results["overall_score"] = score
        
        report = f"""
🔍 KOKORO TTS SYSTEM AUDIT REPORT
{'=' * 50}
Timestamp: {self.results['timestamp']}
Overall Score: {score:.1f}% ({self.passed_checks}/{self.total_checks} checks passed)

📊 SUMMARY:
"""
        
        if score >= 90:
            report += "🟢 EXCELLENT - System is operating optimally\n"
        elif score >= 75:
            report += "🟡 GOOD - System is working well with minor issues\n"
        elif score >= 60:
            report += "🟠 ACCEPTABLE - System is functional but needs attention\n"
        else:
            report += "🔴 POOR - System has significant issues requiring immediate attention\n"
        
        return report
    
    def run_full_audit(self) -> Dict[str, Any]:
        """Run complete system audit"""
        logger.info("🚀 Starting comprehensive system audit...")
        
        self.results["server_status"] = self.audit_server_status()
        self.results["api_endpoints"] = self.audit_api_endpoints()
        self.results["openwebui_integration"] = self.audit_openwebui_integration()
        self.results["performance"] = self.audit_performance()
        self.results["configuration"] = self.audit_configuration()
        
        # Generate and print report
        report = self.generate_report()
        print(report)
        
        return self.results

def main():
    """Main audit function"""
    auditor = SystemAuditor()
    results = auditor.run_full_audit()
    
    # Save results to file
    with open("system_audit_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    logger.info("📄 Audit results saved to system_audit_results.json")
    
    # Exit with appropriate code
    if results["overall_score"] >= 75:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
