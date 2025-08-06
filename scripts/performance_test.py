#!/usr/bin/env python3
"""
Performance testing script for Pokemon Translation Web App
Measures API response times, throughput, and system performance
"""

import asyncio
import aiohttp
import time
import statistics
import json
import sys
from typing import List, Dict, Any
import argparse

class PerformanceTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = []
        
    async def test_health_endpoint(self, num_requests: int = 100) -> Dict[str, Any]:
        """Test health endpoint performance"""
        print(f"Testing health endpoint with {num_requests} requests...")
        
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            response_times = []
            
            for i in range(num_requests):
                request_start = time.time()
                try:
                    async with session.get(f"{self.base_url}/api/v2/health") as response:
                        await response.json()
                        response_time = time.time() - request_start
                        response_times.append(response_time)
                        
                        if (i + 1) % 10 == 0:
                            print(f"  Completed {i + 1}/{num_requests} requests")
                            
                except Exception as e:
                    print(f"  Error on request {i + 1}: {e}")
                    response_times.append(float('inf'))
            
            total_time = time.time() - start_time
            
            return {
                "endpoint": "health",
                "total_requests": num_requests,
                "total_time": total_time,
                "requests_per_second": num_requests / total_time,
                "avg_response_time": statistics.mean(response_times),
                "median_response_time": statistics.median(response_times),
                "min_response_time": min(response_times),
                "max_response_time": max(response_times),
                "p95_response_time": statistics.quantiles(response_times, n=20)[18] if len(response_times) > 1 else 0,
                "p99_response_time": statistics.quantiles(response_times, n=100)[98] if len(response_times) > 1 else 0,
                "error_rate": response_times.count(float('inf')) / num_requests * 100
            }
    
    async def test_summarize_endpoint(self, test_urls: List[str], num_requests_per_url: int = 5) -> Dict[str, Any]:
        """Test summarize endpoint performance"""
        print(f"Testing summarize endpoint with {len(test_urls)} URLs, {num_requests_per_url} requests each...")
        
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            response_times = []
            cache_hits = 0
            errors = 0
            
            for url in test_urls:
                print(f"  Testing URL: {url}")
                for i in range(num_requests_per_url):
                    request_start = time.time()
                    try:
                        payload = {"url": url}
                        async with session.post(
                            f"{self.base_url}/api/v2/summarize",
                            json=payload,
                            headers={"Content-Type": "application/json"}
                        ) as response:
                            if response.status == 200:
                                data = await response.json()
                                response_time = time.time() - request_start
                                response_times.append(response_time)
                                
                                # Check if response was cached (faster response time)
                                if response_time < 1.0:  # Assuming cached responses are under 1 second
                                    cache_hits += 1
                                    
                            else:
                                errors += 1
                                print(f"    Error: {response.status}")
                                
                    except Exception as e:
                        errors += 1
                        print(f"    Exception: {e}")
            
            total_time = time.time() - start_time
            total_requests = len(test_urls) * num_requests_per_url
            
            return {
                "endpoint": "summarize",
                "total_requests": total_requests,
                "total_time": total_time,
                "requests_per_second": total_requests / total_time,
                "avg_response_time": statistics.mean(response_times) if response_times else 0,
                "median_response_time": statistics.median(response_times) if response_times else 0,
                "min_response_time": min(response_times) if response_times else 0,
                "max_response_time": max(response_times) if response_times else 0,
                "p95_response_time": statistics.quantiles(response_times, n=20)[18] if len(response_times) > 1 else 0,
                "p99_response_time": statistics.quantiles(response_times, n=100)[98] if len(response_times) > 1 else 0,
                "cache_hit_rate": (cache_hits / total_requests * 100) if total_requests > 0 else 0,
                "error_rate": (errors / total_requests * 100) if total_requests > 0 else 0
            }
    
    async def test_concurrent_requests(self, num_concurrent: int = 10, num_requests: int = 100) -> Dict[str, Any]:
        """Test concurrent request handling"""
        print(f"Testing {num_concurrent} concurrent requests, {num_requests} total...")
        
        async def make_request(session: aiohttp.ClientSession, request_id: int) -> float:
            start_time = time.time()
            try:
                async with session.get(f"{self.base_url}/api/v2/health") as response:
                    await response.json()
                    return time.time() - start_time
            except Exception as e:
                print(f"  Concurrent request {request_id} failed: {e}")
                return float('inf')
        
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            
            # Create semaphore to limit concurrent requests
            semaphore = asyncio.Semaphore(num_concurrent)
            
            async def limited_request(request_id: int) -> float:
                async with semaphore:
                    return await make_request(session, request_id)
            
            # Run concurrent requests
            tasks = [limited_request(i) for i in range(num_requests)]
            response_times = await asyncio.gather(*tasks)
            
            total_time = time.time() - start_time
            valid_times = [t for t in response_times if t != float('inf')]
            
            return {
                "test_type": "concurrent",
                "concurrent_requests": num_concurrent,
                "total_requests": num_requests,
                "total_time": total_time,
                "requests_per_second": num_requests / total_time,
                "avg_response_time": statistics.mean(valid_times) if valid_times else 0,
                "median_response_time": statistics.median(valid_times) if valid_times else 0,
                "min_response_time": min(valid_times) if valid_times else 0,
                "max_response_time": max(valid_times) if valid_times else 0,
                "error_rate": (len(response_times) - len(valid_times)) / len(response_times) * 100
            }
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/v2/metrics") as response:
                    if response.status == 200:
                        return await response.json()
        except Exception as e:
            print(f"Failed to get system metrics: {e}")
        
        return {}
    
    def print_results(self, results: List[Dict[str, Any]]):
        """Print formatted test results"""
        print("\n" + "="*80)
        print("PERFORMANCE TEST RESULTS")
        print("="*80)
        
        for result in results:
            print(f"\n{result.get('endpoint', result.get('test_type', 'Unknown')).upper()} ENDPOINT:")
            print("-" * 50)
            
            if 'total_requests' in result:
                print(f"Total Requests: {result['total_requests']}")
                print(f"Total Time: {result['total_time']:.2f}s")
                print(f"Requests/Second: {result['requests_per_second']:.2f}")
                print(f"Average Response Time: {result['avg_response_time']*1000:.2f}ms")
                print(f"Median Response Time: {result['median_response_time']*1000:.2f}ms")
                print(f"Min Response Time: {result['min_response_time']*1000:.2f}ms")
                print(f"Max Response Time: {result['max_response_time']*1000:.2f}ms")
                print(f"95th Percentile: {result['p95_response_time']*1000:.2f}ms")
                print(f"99th Percentile: {result['p99_response_time']*1000:.2f}ms")
                
                if 'cache_hit_rate' in result:
                    print(f"Cache Hit Rate: {result['cache_hit_rate']:.1f}%")
                
                if 'error_rate' in result:
                    print(f"Error Rate: {result['error_rate']:.1f}%")
        
        # Print system metrics if available
        if hasattr(self, 'system_metrics') and self.system_metrics:
            print(f"\nSYSTEM METRICS:")
            print("-" * 50)
            metrics = self.system_metrics
            if 'system' in metrics:
                sys_metrics = metrics['system']
                print(f"CPU Usage: {sys_metrics.get('cpu_percent', 'N/A')}%")
                print(f"Memory Usage: {sys_metrics.get('memory_percent', 'N/A')}%")
                print(f"Process Memory: {sys_metrics.get('process_memory_mb', 'N/A'):.1f}MB")
            
            if 'redis' in metrics and 'error' not in metrics['redis']:
                redis_metrics = metrics['redis']
                print(f"Redis Memory: {redis_metrics.get('used_memory_mb', 'N/A'):.1f}MB")
                print(f"Redis Clients: {redis_metrics.get('connected_clients', 'N/A')}")
    
    def save_results(self, results: List[Dict[str, Any]], filename: str = "performance_results.json"):
        """Save results to JSON file"""
        with open(filename, 'w') as f:
            json.dump({
                "timestamp": time.time(),
                "results": results,
                "system_metrics": getattr(self, 'system_metrics', {})
            }, f, indent=2)
        print(f"\nResults saved to {filename}")

async def main():
    parser = argparse.ArgumentParser(description="Performance testing for Pokemon Translation Web App")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL of the API")
    parser.add_argument("--health-requests", type=int, default=100, help="Number of health endpoint requests")
    parser.add_argument("--concurrent", type=int, default=10, help="Number of concurrent requests")
    parser.add_argument("--concurrent-requests", type=int, default=100, help="Total concurrent requests")
    parser.add_argument("--test-urls", nargs="+", help="URLs to test with summarize endpoint")
    parser.add_argument("--requests-per-url", type=int, default=5, help="Requests per test URL")
    parser.add_argument("--output", default="performance_results.json", help="Output file for results")
    
    args = parser.parse_args()
    
    tester = PerformanceTester(args.url)
    results = []
    
    try:
        # Test health endpoint
        health_result = await tester.test_health_endpoint(args.health_requests)
        results.append(health_result)
        
        # Test concurrent requests
        concurrent_result = await tester.test_concurrent_requests(args.concurrent, args.concurrent_requests)
        results.append(concurrent_result)
        
        # Test summarize endpoint if URLs provided
        if args.test_urls:
            summarize_result = await tester.test_summarize_endpoint(args.test_urls, args.requests_per_url)
            results.append(summarize_result)
        
        # Get system metrics
        tester.system_metrics = await tester.get_system_metrics()
        
        # Print and save results
        tester.print_results(results)
        tester.save_results(results, args.output)
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 