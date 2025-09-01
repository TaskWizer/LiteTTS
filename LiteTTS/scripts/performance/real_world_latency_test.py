#!/usr/bin/env python3
"""
Real-World Latency Test for LiteTTS
Tests actual API response times to identify real bottlenecks
"""

import asyncio
import aiohttp
import time
import json
import logging
import statistics
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import numpy as np

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class RealWorldLatencyResult:
    """Real-world latency test results"""
    test_name: str
    avg_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    min_latency_ms: float
    max_latency_ms: float
    success_rate: float
    throughput_rps: float
    cold_start_latency_ms: Optional[float] = None
    warm_latency_ms: Optional[float] = None

class RealWorldLatencyTester:
    """
    Real-world latency tester using actual API calls
    """
    
    def __init__(self, base_url: str = "http://localhost:8355"):
        self.base_url = base_url
        self.test_texts = [
            "Hello world.",
            "This is a test.",
            "How are you today?",
            "This is a medium length sentence for testing.",
            "This is a longer sentence that will help us understand latency characteristics."
        ]
        
        logger.info(f"Real-World Latency Tester initialized for {base_url}")
    
    async def test_health_endpoint(self) -> RealWorldLatencyResult:
        """Test health endpoint latency"""
        logger.info("🔍 Testing health endpoint latency...")
        
        latencies = []
        successful_requests = 0
        total_requests = 20
        
        async with aiohttp.ClientSession() as session:
            for i in range(total_requests):
                try:
                    start_time = time.perf_counter()
                    async with session.get(f"{self.base_url}/health") as response:
                        await response.text()
                        end_time = time.perf_counter()
                        
                        if response.status == 200:
                            latency_ms = (end_time - start_time) * 1000
                            latencies.append(latency_ms)
                            successful_requests += 1
                        
                except Exception as e:
                    logger.warning(f"Health endpoint request {i} failed: {e}")
        
        if latencies:
            return RealWorldLatencyResult(
                test_name="Health Endpoint",
                avg_latency_ms=statistics.mean(latencies),
                p95_latency_ms=np.percentile(latencies, 95),
                p99_latency_ms=np.percentile(latencies, 99),
                min_latency_ms=min(latencies),
                max_latency_ms=max(latencies),
                success_rate=successful_requests / total_requests,
                throughput_rps=successful_requests / (max(latencies) / 1000) if latencies else 0
            )
        else:
            return RealWorldLatencyResult(
                test_name="Health Endpoint",
                avg_latency_ms=0,
                p95_latency_ms=0,
                p99_latency_ms=0,
                min_latency_ms=0,
                max_latency_ms=0,
                success_rate=0,
                throughput_rps=0
            )
    
    async def test_tts_endpoint_cold_start(self) -> RealWorldLatencyResult:
        """Test TTS endpoint cold start latency"""
        logger.info("🔍 Testing TTS endpoint cold start latency...")
        
        # Wait a bit to ensure cold start
        await asyncio.sleep(2)
        
        payload = {
            "input": "Hello world, this is a cold start test.",
            "voice": "af_heart",
            "response_format": "mp3"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                start_time = time.perf_counter()
                async with session.post(
                    f"{self.base_url}/v1/audio/speech",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    await response.read()
                    end_time = time.perf_counter()
                    
                    cold_start_latency = (end_time - start_time) * 1000
                    success = response.status == 200
                    
                    logger.info(f"Cold start latency: {cold_start_latency:.1f}ms")
                    
                    return RealWorldLatencyResult(
                        test_name="TTS Cold Start",
                        avg_latency_ms=cold_start_latency,
                        p95_latency_ms=cold_start_latency,
                        p99_latency_ms=cold_start_latency,
                        min_latency_ms=cold_start_latency,
                        max_latency_ms=cold_start_latency,
                        success_rate=1.0 if success else 0.0,
                        throughput_rps=1.0 / (cold_start_latency / 1000) if cold_start_latency > 0 else 0,
                        cold_start_latency_ms=cold_start_latency
                    )
                    
        except Exception as e:
            logger.error(f"Cold start test failed: {e}")
            return RealWorldLatencyResult(
                test_name="TTS Cold Start",
                avg_latency_ms=0,
                p95_latency_ms=0,
                p99_latency_ms=0,
                min_latency_ms=0,
                max_latency_ms=0,
                success_rate=0,
                throughput_rps=0,
                cold_start_latency_ms=None
            )
    
    async def test_tts_endpoint_warm_requests(self) -> RealWorldLatencyResult:
        """Test TTS endpoint warm request latency"""
        logger.info("🔍 Testing TTS endpoint warm request latency...")
        
        latencies = []
        successful_requests = 0
        total_requests = 10
        
        async with aiohttp.ClientSession() as session:
            for i, text in enumerate(self.test_texts * 2):  # Test each text twice
                if i >= total_requests:
                    break
                    
                payload = {
                    "input": text,
                    "voice": "af_heart",
                    "response_format": "mp3"
                }
                
                try:
                    start_time = time.perf_counter()
                    async with session.post(
                        f"{self.base_url}/v1/audio/speech",
                        json=payload,
                        headers={"Content-Type": "application/json"}
                    ) as response:
                        audio_data = await response.read()
                        end_time = time.perf_counter()
                        
                        if response.status == 200 and len(audio_data) > 0:
                            latency_ms = (end_time - start_time) * 1000
                            latencies.append(latency_ms)
                            successful_requests += 1
                            logger.debug(f"Request {i}: {latency_ms:.1f}ms for '{text[:30]}...'")
                        else:
                            logger.warning(f"Request {i} failed with status {response.status}")
                            
                except Exception as e:
                    logger.warning(f"Warm request {i} failed: {e}")
                
                # Small delay between requests
                await asyncio.sleep(0.1)
        
        if latencies:
            return RealWorldLatencyResult(
                test_name="TTS Warm Requests",
                avg_latency_ms=statistics.mean(latencies),
                p95_latency_ms=np.percentile(latencies, 95),
                p99_latency_ms=np.percentile(latencies, 99),
                min_latency_ms=min(latencies),
                max_latency_ms=max(latencies),
                success_rate=successful_requests / total_requests,
                throughput_rps=successful_requests / (sum(latencies) / 1000) if latencies else 0,
                warm_latency_ms=statistics.mean(latencies)
            )
        else:
            return RealWorldLatencyResult(
                test_name="TTS Warm Requests",
                avg_latency_ms=0,
                p95_latency_ms=0,
                p99_latency_ms=0,
                min_latency_ms=0,
                max_latency_ms=0,
                success_rate=0,
                throughput_rps=0,
                warm_latency_ms=None
            )
    
    async def test_concurrent_requests(self) -> RealWorldLatencyResult:
        """Test concurrent request handling"""
        logger.info("🔍 Testing concurrent request latency...")
        
        concurrent_requests = 5
        latencies = []
        successful_requests = 0
        
        async def make_request(session, text, request_id):
            payload = {
                "input": text,
                "voice": "af_heart",
                "response_format": "mp3"
            }
            
            try:
                start_time = time.perf_counter()
                async with session.post(
                    f"{self.base_url}/v1/audio/speech",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    await response.read()
                    end_time = time.perf_counter()
                    
                    if response.status == 200:
                        latency_ms = (end_time - start_time) * 1000
                        return latency_ms, True
                    else:
                        return 0, False
                        
            except Exception as e:
                logger.warning(f"Concurrent request {request_id} failed: {e}")
                return 0, False
        
        async with aiohttp.ClientSession() as session:
            # Create concurrent tasks
            tasks = []
            for i in range(concurrent_requests):
                text = self.test_texts[i % len(self.test_texts)]
                task = make_request(session, text, i)
                tasks.append(task)
            
            # Execute concurrently
            results = await asyncio.gather(*tasks)
            
            for latency, success in results:
                if success:
                    latencies.append(latency)
                    successful_requests += 1
        
        if latencies:
            return RealWorldLatencyResult(
                test_name="Concurrent Requests",
                avg_latency_ms=statistics.mean(latencies),
                p95_latency_ms=np.percentile(latencies, 95),
                p99_latency_ms=np.percentile(latencies, 99),
                min_latency_ms=min(latencies),
                max_latency_ms=max(latencies),
                success_rate=successful_requests / concurrent_requests,
                throughput_rps=successful_requests / (max(latencies) / 1000) if latencies else 0
            )
        else:
            return RealWorldLatencyResult(
                test_name="Concurrent Requests",
                avg_latency_ms=0,
                p95_latency_ms=0,
                p99_latency_ms=0,
                min_latency_ms=0,
                max_latency_ms=0,
                success_rate=0,
                throughput_rps=0
            )
    
    async def check_server_availability(self) -> bool:
        """Check if the server is available"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health", timeout=aiohttp.ClientTimeout(total=5)) as response:
                    return response.status == 200
        except Exception:
            return False
    
    async def run_comprehensive_test(self) -> Dict[str, RealWorldLatencyResult]:
        """Run comprehensive real-world latency test"""
        logger.info("🚀 Starting comprehensive real-world latency test...")
        
        # Check server availability
        if not await self.check_server_availability():
            logger.error("❌ Server is not available. Please start the LiteTTS server first.")
            return {}
        
        logger.info("✅ Server is available, proceeding with tests...")
        
        results = {}
        
        # Test 1: Health endpoint
        results["health"] = await self.test_health_endpoint()
        
        # Test 2: Cold start
        results["cold_start"] = await self.test_tts_endpoint_cold_start()
        
        # Test 3: Warm requests
        results["warm_requests"] = await self.test_tts_endpoint_warm_requests()
        
        # Test 4: Concurrent requests
        results["concurrent"] = await self.test_concurrent_requests()
        
        logger.info("✅ Comprehensive real-world latency test completed")
        
        return results

def generate_report(results: Dict[str, RealWorldLatencyResult]) -> str:
    """Generate comprehensive latency report"""
    report = []
    report.append("# Real-World Latency Test Report")
    report.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    if not results:
        report.append("❌ **No test results available - server may not be running**")
        return "\n".join(report)
    
    # Executive Summary
    report.append("## Executive Summary")
    
    cold_start = results.get("cold_start")
    warm_requests = results.get("warm_requests")
    
    if cold_start and cold_start.cold_start_latency_ms:
        report.append(f"**Cold Start Latency:** {cold_start.cold_start_latency_ms:.1f}ms")
    
    if warm_requests and warm_requests.warm_latency_ms:
        report.append(f"**Warm Request Latency:** {warm_requests.warm_latency_ms:.1f}ms")
        
        # Determine if latency targets are met
        target_met = warm_requests.warm_latency_ms < 500
        status = "✅ MEETS TARGET" if target_met else "❌ EXCEEDS TARGET"
        report.append(f"**Latency Target (500ms):** {status}")
    
    report.append("")
    
    # Detailed Results
    report.append("## Detailed Test Results")
    report.append("| Test | Avg Latency | P95 | P99 | Min | Max | Success Rate | Throughput |")
    report.append("|------|-------------|-----|-----|-----|-----|--------------|------------|")
    
    for test_name, result in results.items():
        if result.avg_latency_ms > 0:
            report.append(f"| {result.test_name} | {result.avg_latency_ms:.1f}ms | {result.p95_latency_ms:.1f}ms | {result.p99_latency_ms:.1f}ms | {result.min_latency_ms:.1f}ms | {result.max_latency_ms:.1f}ms | {result.success_rate:.1%} | {result.throughput_rps:.2f} RPS |")
        else:
            report.append(f"| {result.test_name} | Failed | - | - | - | - | {result.success_rate:.1%} | 0 RPS |")
    
    report.append("")
    
    # Analysis
    report.append("## Analysis")
    
    if cold_start and warm_requests:
        if cold_start.cold_start_latency_ms and warm_requests.warm_latency_ms:
            cold_warm_diff = cold_start.cold_start_latency_ms - warm_requests.warm_latency_ms
            report.append(f"**Cold Start Penalty:** {cold_warm_diff:.1f}ms")
            
            if cold_warm_diff > 1000:
                report.append("⚠️ **High cold start penalty detected** - model preloading may not be working effectively")
            elif cold_warm_diff > 500:
                report.append("⚠️ **Moderate cold start penalty** - consider optimizing model loading")
            else:
                report.append("✅ **Low cold start penalty** - model warm-up is working well")
    
    # Recommendations
    report.append("")
    report.append("## Recommendations")
    
    if warm_requests and warm_requests.warm_latency_ms:
        if warm_requests.warm_latency_ms > 500:
            report.append("1. **Optimize warm request latency** - current latency exceeds 500ms target")
            report.append("2. **Profile model inference** - identify bottlenecks in the processing pipeline")
            report.append("3. **Consider model optimization** - quantization or hardware acceleration")
        else:
            report.append("1. **Latency performance is good** - meets 500ms target")
    
    if cold_start and cold_start.cold_start_latency_ms and cold_start.cold_start_latency_ms > 2000:
        report.append("2. **Implement aggressive model preloading** - reduce cold start latency")
        report.append("3. **Consider model caching strategies** - keep models in memory")
    
    concurrent = results.get("concurrent")
    if concurrent and concurrent.success_rate < 1.0:
        report.append("4. **Improve concurrent request handling** - some requests are failing")
    
    return "\n".join(report)

async def main():
    """Main function"""
    tester = RealWorldLatencyTester()
    results = await tester.run_comprehensive_test()
    
    # Generate report
    report = generate_report(results)
    
    # Save report
    with open("real_world_latency_test_report.md", 'w') as f:
        f.write(report)
    
    # Save JSON results
    json_results = {name: {
        "test_name": result.test_name,
        "avg_latency_ms": result.avg_latency_ms,
        "p95_latency_ms": result.p95_latency_ms,
        "p99_latency_ms": result.p99_latency_ms,
        "min_latency_ms": result.min_latency_ms,
        "max_latency_ms": result.max_latency_ms,
        "success_rate": result.success_rate,
        "throughput_rps": result.throughput_rps,
        "cold_start_latency_ms": result.cold_start_latency_ms,
        "warm_latency_ms": result.warm_latency_ms
    } for name, result in results.items()}
    
    with open("real_world_latency_test_results.json", 'w') as f:
        json.dump(json_results, f, indent=2)
    
    print(report)
    logger.info("📊 Real-world latency test report saved to: real_world_latency_test_report.md")

if __name__ == "__main__":
    asyncio.run(main())
