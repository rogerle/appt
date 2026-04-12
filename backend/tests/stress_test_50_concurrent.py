"""
Stress Test: 50 Concurrent Booking Request Simulation

This script simulates exactly 50 concurrent users making booking requests
to test the system's capacity and performance under load.

Following Apple Design System principles:
- Clean, focused test scenarios
- Precise concurrency control  
- Comprehensive metrics collection
- Performance target validation (<200ms response time)
"""

import asyncio
import aiohttp
import time
import json
from typing import List, Dict, Any
from dataclasses import dataclass
from statistics import mean, stdev


@dataclass
class TestResult:
    """Single request result tracking."""
    endpoint: str
    status_code: int
    response_time_ms: float
    success: bool
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "endpoint": self.endpoint,
            "status_code": self.status_code,
            "response_time_ms": round(self.response_time_ms, 2),
            "success": self.success
        }


class ConcurrentBookingStressTest:
    """50 concurrent booking request stress test."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results: List[TestResult] = []
        self.auth_token: str = None
        
    async def register_test_studio(self, session: aiohttp.ClientSession) -> bool:
        """Register a test studio for authentication."""
        
        email = f"stress_test_{int(time.time())}@yoga.com"
        payload = {
            "name": "压力测试瑜伽馆",
            "email": email,
            "password": "TestPass123!"
        }
        
        try:
            async with session.post(
                f"{self.base_url}/api/v1/auth/register",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    # Auto-login after registration
                    login_payload = {
                        "username": email,
                        "password": "TestPass123!"
                    }
                    
                    async with session.post(
                        f"{self.base_url}/api/v1/auth/login",
                        json=login_payload,
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as login_response:
                        if login_response.status == 200:
                            data = await login_response.json()
                            self.auth_token = data.get("token")
                            return True
        except Exception as e:
            print(f"Registration/Login error: {e}")
        
        return False
    
    async def create_test_schedule(self, session: aiohttp.ClientSession) -> int:
        """Create a test schedule for booking."""
        
        if not self.auth_token:
            await self.register_test_studio(session)
        
        payload = {
            "instructor_id": 1,
            "date": "2024-06-20",
            "start_time": "10:00:00",
            "end_time": "11:30:00",
            "title": "压力测试瑜伽课"
        }
        
        headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
        
        try:
            async with session.post(
                f"{self.base_url}/api/v1/studio/schedules",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status in [200, 201]:
                    data = await response.json()
                    return data.get("id")
        except Exception as e:
            print(f"Schedule creation error: {e}")
        
        return None
    
    async def make_booking_request(
        self, 
        session: aiohttp.ClientSession, 
        schedule_id: int,
        user_index: int
    ) -> TestResult:
        """Make a single booking request."""
        
        start_time = time.time()
        
        payload = {
            "schedule_id": schedule_id,
            "name": f"测试用户{user_index}",
            "phone": f"138{str(user_index).zfill(8)}",
            "notes": ""
        }
        
        try:
            async with session.post(
                f"{self.base_url}/api/v1/bookings",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                
                response_time = (time.time() - start_time) * 1000
                
                result = TestResult(
                    endpoint="/api/v1/bookings",
                    status_code=response.status,
                    response_time_ms=response_time,
                    success=response.status in [200, 201]
                )
                
                self.results.append(result)
                return result
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            
            result = TestResult(
                endpoint="/api/v1/bookings",
                status_code=0,
                response_time_ms=response_time,
                success=False
            )
            
            self.results.append(result)
            return result
    
    async def run_concurrent_test(self, num_users: int = 50):
        """Run stress test with exactly N concurrent users."""
        
        print(f"\n{'='*80}")
        print(f"🚀 STRESS TEST: {num_users} Concurrent Booking Requests")
        print(f"{'='*80}\n")
        
        # Register and create test schedule first
        async with aiohttp.ClientSession() as session:
            success = await self.register_test_studio(session)
            
            if not success:
                print("❌ Failed to register studio, using public endpoints only\n")
            
            schedule_id = await self.create_test_schedule(session)
        
        # If no schedule created, use a dummy ID (will likely fail validation, but tests load)
        if not schedule_id:
            schedule_id = 9999
        
        # Run concurrent booking requests
        print(f"📊 Starting {num_users} concurrent booking requests...\n")
        
        start_time_total = time.time()
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            
            for i in range(1, num_users + 1):
                task = self.make_booking_request(session, schedule_id, i)
                tasks.append(task)
            
            # Execute all requests concurrently
            results = await asyncio.gather(*tasks)
        
        total_time = (time.time() - start_time_total) * 1000
        
        print(f"\n✅ Test completed in {total_time:.2f}ms\n")
    
    def generate_report(self):
        """Generate comprehensive test report."""
        
        if not self.results:
            print("⚠️ No results to report")
            return
        
        total_requests = len(self.results)
        successful = sum(1 for r in self.results if r.success)
        failed = total_requests - successful
        failure_rate = (failed / total_requests * 100) if total_requests > 0 else 0
        
        response_times = [r.response_time_ms for r in self.results]
        
        # Calculate statistics
        avg_response_time = mean(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        std_dev = stdev(response_times) if len(response_times) > 1 else 0
        
        # Percentiles
        sorted_times = sorted(response_times)
        p50_idx = int(len(sorted_times) * 0.50)
        p95_idx = int(len(sorted_times) * 0.95)
        p99_idx = int(len(sorted_times) * 0.99)
        
        p50 = sorted_times[p50_idx] if p50_idx < len(sorted_times) else sorted_times[-1]
        p95 = sorted_times[p95_idx] if p95_idx < len(sorted_times) else sorted_times[-1]
        p99 = sorted_times[p99_idx] if p99_idx < len(sorted_times) else sorted_times[-1]
        
        # Status code distribution
        status_distribution: Dict[int, int] = {}
        for r in self.results:
            status_distribution[r.status_code] = status_distribution.get(r.status_code, 0) + 1
        
        print(f"\n{'='*80}")
        print("📊 STRESS TEST REPORT - 50 Concurrent Users")
        print(f"{'='*80}\n")
        
        print("🎯 Overall Statistics:")
        print(f"   Total Requests: {total_requests}")
        print(f"   Successful: {successful} ({(successful/total_requests*100):.2f}%)")
        print(f"   Failed: {failed} ({failure_rate:.2f}%)")
        print()
        
        print("⏱️  Response Time Analysis:")
        print(f"   Average: {avg_response_time:.2f}ms")
        print(f"   Minimum: {min_response_time:.2f}ms")
        print(f"   Maximum: {max_response_time:.2f}ms")
        print(f"   Standard Deviation: {std_dev:.2f}ms")
        print()
        
        print("📈 Percentiles:")
        print(f"   P50 (Median): {p50:.2f}ms")
        print(f"   P95: {p95:.2f}ms")
        print(f"   P99: {p99:.2f}ms")
        print()
        
        print("🔢 Status Code Distribution:")
        for status, count in sorted(status_distribution.items()):
            percentage = (count / total_requests * 100)
            print(f"   HTTP {status}: {count} ({percentage:.2f}%)")
        print()
        
        # Performance validation against Apple Design System targets
        print("🍎 Performance Target Validation:")
        print(f"   {'✅' if avg_response_time < 200 else '❌'} Average Response Time: {avg_response_time:.2f}ms (Target: <200ms)")
        print(f"   {'✅' if p95 < 300 else '❌'} P95 Response Time: {p95:.2f}ms (Target: <300ms)")
        print(f"   {'✅' if failure_rate < 1 else '❌'} Failure Rate: {failure_rate:.2f}% (Target: <1%)")
        print()
        
        # Detailed results for failed requests
        failed_results = [r for r in self.results if not r.success]
        if failed_results:
            print(f"⚠️  Failed Requests ({len(failed_results)}):")
            for i, result in enumerate(failed_results[:10], 1):
                print(f"   {i}. Status: {result.status_code}, Time: {result.response_time_ms:.2f}ms")
            
            if len(failed_results) > 10:
                print(f"   ... and {len(failed_results) - 10} more failed requests")
            print()
        
        # Recommendations based on Apple Design System principles
        print("💡 Performance Recommendations:")
        
        if avg_response_time < 100:
            print("   ✅ Excellent performance! Response times are optimal.")
        elif avg_response_time < 200:
            print("   ⚠️  Good performance, but could be optimized further.")
        else:
            print(f"   ❌ Performance needs optimization (avg: {avg_response_time:.2f}ms)")
            print("      Consider:")
            print("      - Adding database indexes")
            print("      - Implementing query caching")
            print("      - Optimizing N+1 queries with eager loading")
        
        if failure_rate > 5:
            print(f"   ⚠️  High failure rate detected ({failure_rate:.2f}%)")
            print("      Investigate error causes and add retry logic.")
        
        print("\n" + "="*80)
    
    def save_results(self, filename: str = "stress_test_results.json"):
        """Save test results to JSON file."""
        
        report_data = {
            "test_type": "50_concurrent_booking_requests",
            "total_requests": len(self.results),
            "successful": sum(1 for r in self.results if r.success),
            "failed": sum(1 for r in self.results if not r.success),
            "failure_rate_percent": (sum(1 for r in self.results if not r.success) / len(self.results) * 100) if self.results else 0,
            "response_time_stats": {
                "average_ms": round(mean([r.response_time_ms for r in self.results]), 2),
                "min_ms": round(min([r.response_time_ms for r in self.results]), 2),
                "max_ms": round(max([r.response_time_ms for r in self.results]), 2),
                "std_dev_ms": round(stdev([r.response_time_ms for r in self.results]), 2) if len(self.results) > 1 else 0,
                "p50_ms": sorted([r.response_time_ms for r in self.results])[int(len(self.results)*0.5)] if self.results else 0,
                "p95_ms": sorted([r.response_time_ms for r in self.results])[int(len(self.results)*0.95)] if self.results else 0,
                "p99_ms": sorted([r.response_time_ms for r in self.results])[int(len(self.results)*0.99)] if self.results else 0,
            },
            "status_code_distribution": {},
            "individual_results": [r.to_dict() for r in self.results]
        }
        
        # Calculate status code distribution
        for r in self.results:
            status = r.status_code
            report_data["status_code_distribution"][str(status)] = \
                report_data["status_code_distribution"].get(str(status), 0) + 1
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📁 Results saved to: {filename}")


async def main():
    """Main test runner."""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Stress Test: 50 Concurrent Booking Requests")
    parser.add_argument(
        "--url", 
        default="http://localhost:8000",
        help="Base URL of the API server (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--users", 
        type=int, 
        default=50,
        help="Number of concurrent users (default: 50)"
    )
    parser.add_argument(
        "--output", 
        default="stress_test_results.json",
        help="Output filename for results JSON (default: stress_test_results.json)"
    )
    
    args = parser.parse_args()
    
    # Run the stress test
    tester = ConcurrentBookingStressTest(base_url=args.url)
    
    try:
        await tester.run_concurrent_test(num_users=args.users)
        tester.generate_report()
        tester.save_results(args.output)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        if tester.results:
            tester.generate_report()
            tester.save_results(args.output)


if __name__ == "__main__":
    asyncio.run(main())
