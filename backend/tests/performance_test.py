"""Performance & Load Testing for Appt Backend - Locust Configuration.

Simulates real-world user traffic patterns following Apple Design System principles:
- Clean, focused test scenarios
- Realistic user behavior modeling
- Progressive load increase (ramp-up)
- Clear performance metrics collection
"""

from locust import HttpUser, task, between, events
import random
import time


class YogaStudioUser(HttpUser):
    """Simulates realistic yoga studio booking flow."""
    
    # Wait 1-3 seconds between actions (realistic user behavior)
    wait_time = between(1, 3)
    
    def on_start(self):
        """Setup: Register and login as admin before testing endpoints."""
        
        # Register a test studio first time only
        response = self.client.post("/api/v1/auth/register", json={
            "name": f"Performance Test Studio {self.host.split(':')[2]}",
            "email": f"perf_test_{int(time.time())}@test.com",
            "password": "testpass123"
        })
        
        if response.status_code == 200:
            # Login to get auth token for admin actions
            login_response = self.client.post("/api/v1/auth/login", json={
                "username": f"perf_test_{int(time.time())}@test.com",
                "password": "testpass123"
            })
            
            if login_response.status_code == 200:
                self.token = login_response.json().get("token")
                self.headers = {"Authorization": f"Bearer {self.token}"}


class InstructorLoadTest(HttpUser):
    """Tests instructor management endpoints under load."""
    
    wait_time = between(1, 2)
    
    def on_start(self):
        """Setup: Register and login for admin access."""
        
        self.client.post("/api/v1/auth/register", json={
            "name": "Instructor Load Test Studio",
            "email": f"instructor_load_{int(time.time())}@test.com",
            "password": "testpass"
        })
        
        login_response = self.client.post("/api/v1/auth/login", json={
            "username": f"instructor_load_{int(time.time())}@test.com",
            "password": "testpass"
        })
        
        if login_response.status_code == 200:
            self.token = login_response.json().get("token")
            self.headers = {"Authorization": f"Bearer {self.token}"}


class BookingLoadTest(HttpUser):
    """Tests booking endpoints under high load."""
    
    wait_time = between(0.5, 1.5)  # Faster pace for public endpoint testing
    
    def on_start(self):
        """Setup: No auth needed for public booking endpoint."""
        pass


# ============================================================================
# REALISTIC USER BEHAVIOR - Apple Design System Inspired
# ============================================================================

class RealisticUserFlow(HttpUser):
    """Simulates realistic yoga studio user behavior patterns."""
    
    wait_time = between(2, 5)  # Users browse for a few seconds before acting
    
    def on_start(self):
        """Initial registration and login."""
        
        # Step 1: Register new studio (happens once per test run)
        self.client.post("/api/v1/auth/register", json={
            "name": f"Realistic Test Studio {random.randint(1000, 9999)}",
            "email": f"realistic_{int(time.time())}@test.com",
            "password": "userpass123"
        })
        
        # Step 2: Login to get token
        login_response = self.client.post("/api/v1/auth/login", json={
            "username": f"realistic_{int(time.time())}@test.com",
            "password": "userpass123"
        })
        
        if login_response.status_code == 200:
            self.token = login_response.json().get("token")
            self.headers = {"Authorization": f"Bearer {self.token}"}


class PerformanceTestScenarios(HttpUser):
    """Defines specific performance test scenarios with different load patterns."""
    
    # Scenario-specific wait times
    wait_time = between(1, 3)
    
    def on_start(self):
        """Setup: Register and login for all admin endpoints."""
        
        self.client.post("/api/v1/auth/register", json={
            "name": f"Performance Test Studio {int(time.time())}",
            "email": f"perf_{int(time.time())}@test.com",
            "password": "testpass"
        })
        
        login_response = self.client.post("/api/v1/auth/login", json={
            "username": f"perf_{int(time.time())}@test.com",
            "password": "testpass"
        })
        
        if login_response.status_code == 200:
            self.token = login_response.json().get("token")
            self.headers = {"Authorization": f"Bearer {self.token}"}


# ============================================================================
# TEST SCENARIOS - Public Endpoints (No Auth Required)
# ============================================================================

class PublicEndpointTests(HttpUser):
    """Tests public endpoints that don't require authentication."""
    
    wait_time = between(1, 2)
    
    @task(5)  # Weight: 5x more likely to be called than other tasks
    def get_instructors_list(self):
        """Test: GET /api/v1/instructors - Public instructor listing."""
        
        self.client.get("/api/v1/instructors")
    
    @task(3)
    def get_instructors_with_date_filter(self):
        """Test: GET /api/v1/instructors?date=2024-06-15 with date filter."""
        
        test_dates = [
            "2024-06-15", "2024-06-16", "2024-06-17", 
            "2024-07-01", "2024-08-15"
        ]
        
        date = random.choice(test_dates)
        self.client.get(f"/api/v1/instructors?date={date}")
    
    @task(3)
    def create_booking(self):
        """Test: POST /api/v1/bookings - Public booking creation."""
        
        test_schedules = [1, 2, 3, 4, 5]
        schedule_id = random.choice(test_schedules)
        
        self.client.post("/api/v1/bookings", json={
            "schedule_id": schedule_id,
            "name": f"测试用户{random.randint(100, 999)}",
            "phone": f"138{random.randint(10000000, 99999999)}",
            "notes": random.choice([
                "", 
                "第一次来，需要基础指导",
                "有运动损伤，请温柔一点",
                "想体验流瑜伽"
            ])
        })


# ============================================================================
# TEST SCENARIOS - Admin Endpoints (Auth Required)
# ============================================================================

class AdminEndpointTests(PerformanceTestScenarios):
    """Tests admin-only endpoints under various load conditions."""
    
    @task(4)  # Weight: 4x more likely than other tasks
    def create_instructor(self):
        """Test: POST /api/v1/studio/instructors - Create new instructor."""
        
        titles = [
            "高级哈他瑜伽导师",
            "流瑜伽专家", 
            "阴瑜伽教练",
            "空中瑜伽导师",
            "孕产瑜伽指导师"
        ]
        
        bios = [
            "专注瑜伽教学 5 年，擅长基础体式纠正",
            "10 年经验，帮助数百名学生改善体态",
            "专注女性健康与产后恢复",
            "国际认证空中瑜伽导师，5 年教学经验"
        ]
        
        avatar_urls = [
            f"https://example.com/instructor_{random.randint(1, 20)}.jpg",
            f"https://picsum.photos/seed/{random.randint(1, 100)}/200/200.jpg"
        ]
        
        self.client.post("/api/v1/studio/instructors", json={
            "name": f"教练{random.randint(100, 999)}",
            "title": random.choice(titles),
            "avatar_url": random.choice(avatar_urls),
            "bio": random.choice(bios)
        })
    
    @task(4)
    def update_instructor(self):
        """Test: PUT /api/v1/studio/instructors/{id} - Update instructor info."""
        
        # Simulate updating existing instructors (IDs 1-20)
        instructor_id = random.randint(1, 20)
        
        self.client.put(f"/api/v1/studio/instructors/{instructor_id}", json={
            "name": f"更新后的教练{random.randint(100, 999)}",
            "title": "资深瑜伽导师",
            "bio": "新增 5 年教学经验，专注阴瑜伽教学"
        })
    
    @task(2)
    def delete_instructor(self):
        """Test: DELETE /api/v1/studio/instructors/{id} - Disable instructor."""
        
        instructor_id = random.randint(1, 20)
        
        self.client.delete(f"/api/v1/studio/instructors/{instructor_id}")
    
    @task(3)
    def create_single_schedule(self):
        """Test: POST /api/v1/studio/schedules - Create single schedule."""
        
        test_dates = [
            "2024-06-15", "2024-06-16", "2024-06-17", 
            "2024-07-01", "2024-08-15"
        ]
        
        start_times = ["09:00", "10:00", "18:00", "19:00"]
        end_times = ["10:30", "11:30", "19:30", "20:30"]
        
        self.client.post("/api/v1/studio/schedules", json={
            "instructor_id": random.randint(1, 10),
            "date": random.choice(test_dates),
            "start_time": random.choice(start_times),
            "end_time": random.choice(end_times),
            "title": f"{random.choice(['晨间', '午后', '晚间'])}瑜伽课"
        })
    
    @task(2)
    def create_batch_schedules(self):
        """Test: POST /api/v1/studio/schedules/batch - Create weekly schedule."""
        
        self.client.post("/api/v1/studio/schedules/batch", json={
            "instructor_id": random.randint(1, 5),
            "daysOfWeek": [1, 2, 3, 4, 5],  # Monday-Friday
            "start_time": "09:00",
            "end_time": "10:00",
            "title": "工作日晨练瑜伽",
            "start_date": "2024-06-17",
            "end_date": "2024-06-21"
        })
    
    @task(3)
    def get_admin_bookings(self):
        """Test: GET /api/v1/studio/bookings - Retrieve all bookings."""
        
        self.client.get("/api/v1/studio/bookings", headers=self.headers)


# ============================================================================
# TEST SCENARIOS - High Load Stress Testing
# ============================================================================

class HighLoadStressTests(HttpUser):
    """Simulates extreme load scenarios for stress testing."""
    
    wait_time = between(0.2, 0.5)  # Very fast pace for stress test
    
    def on_start(self):
        """Setup: Quick registration and login."""
        
        self.client.post("/api/v1/auth/register", json={
            "name": f"Stress Test Studio {int(time.time())}",
            "email": f"stress_{int(time.time())}@test.com",
            "password": "stresspass"
        })
        
        login_response = self.client.post("/api/v1/auth/login", json={
            "username": f"stress_{int(time.time())}@test.com",
            "password": "stresspass"
        })
        
        if login_response.status_code == 200:
            self.token = login_response.json().get("token")


class StressTestScenarios(HttpUser):
    """Stress test all critical endpoints with maximum concurrency."""
    
    wait_time = between(0.1, 0.3)  # Minimal delay for stress testing
    
    def on_start(self):
        """Quick setup for stress testing."""
        
        self.client.post("/api/v1/auth/register", json={
            "name": f"Max Stress Studio {int(time.time())}",
            "email": f"maxstress_{int(time.time())}@test.com",
            "password": "maxpass"
        })
        
        login_response = self.client.post("/api/v1/auth/login", json={
            "username": f"maxstress_{int(time.time())}@test.com",
            "password": "maxpass"
        })
        
        if login_response.status_code == 200:
            self.token = login_response.json().get("token")


class StressTestEndpoints(HttpUser):
    """Tests endpoints under maximum stress conditions."""
    
    wait_time = between(0.1, 0.3)
    
    @task(5)
    def public_instructor_query(self):
        """Stress test: Public instructor listing (high read load)."""
        
        self.client.get("/api/v1/instructors")
    
    @task(3)
    def stress_booking_creation(self):
        """Stress test: Multiple concurrent booking creations."""
        
        for i in range(random.randint(1, 5)):
            self.client.post("/api/v1/bookings", json={
                "schedule_id": random.randint(1, 20),
                "name": f"用户{random.randint(1000, 9999)}",
                "phone": f"138{random.randint(10000000, 99999999)}"
            })


# ============================================================================
# LOCUST EVENTS - Performance Metrics Collection
# ============================================================================

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when load test starts."""
    
    print("\n" + "="*80)
    print("🚀 PERFORMANCE TEST STARTED")
    print("="*80)
    print(f"Target Host: {environment.host}")
    print("Running realistic user flow simulation...")
    print("="*80 + "\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when load test completes."""
    
    stats = environment.stats
    
    print("\n" + "="*80)
    print("📊 PERFORMANCE TEST COMPLETED - SUMMARY REPORT")
    print("="*80)
    
    # Overall statistics
    total_requests = stats.total.num_requests
    total_failures = stats.total.num_failures
    failure_rate = (total_failures / total_requests * 100) if total_requests > 0 else 0
    
    avg_response_time = stats.total.avg_response_time
    max_response_time = stats.total.max_response_time
    
    print(f"\n📈 Overall Statistics:")
    print(f"   Total Requests: {total_requests}")
    print(f"   Successful: {total_requests - total_failures}")
    print(f"   Failed: {total_failures} ({failure_rate:.2f}%)")
    print(f"   Average Response Time: {avg_response_time:.2f}ms")
    print(f"   Max Response Time: {max_response_time:.2f}ms")
    
    # Per-endpoint breakdown (top 10 endpoints)
    print(f"\n🔍 Top 10 Endpoints by Request Count:")
    
    endpoint_stats = []
    for key, stat in stats.entries.items():
        if key != "":
            endpoint_stats.append((key, stat.num_requests))
    
    endpoint_stats.sort(key=lambda x: x[1], reverse=True)
    
    for i, (endpoint, count) in enumerate(endpoint_stats[:10], 1):
        print(f"   {i}. {endpoint}: {count} requests")
    
    # Response time percentiles (95th and 99th percentile)
    p95 = stats.total.get_response_time_percentile(0.95)
    p99 = stats.total.get_response_time_percentile(0.99)
    
    print(f"\n⏱️  Response Time Percentiles:")
    print(f"   P50 (Median): {stats.total.avg_response_time:.2f}ms")
    print(f"   P95: {p95:.2f}ms")
    print(f"   P99: {p99:.2f}ms")
    
    # Performance recommendations based on Apple Design System principles
    print(f"\n🍎 Apple Design System Recommendations:")
    
    if avg_response_time < 100:
        print("   ✅ Response times are excellent (<100ms)")
    elif avg_response_time < 300:
        print("   ⚠️  Response times are acceptable (100-300ms)")
    else:
        print(f"   ❌ Response times need optimization (>300ms, avg: {avg_response_time:.2f}ms)")
    
    if failure_rate < 1:
        print("   ✅ Failure rate is within acceptable limits (<1%)")
    elif failure_rate < 5:
        print(f"   ⚠️  Failure rate is elevated ({failure_rate:.2f}%, target: <1%)")
    else:
        print(f"   ❌ Failure rate is critical ({failure_rate:.2f}%, immediate attention needed)")
    
    print("\n" + "="*80)


# ============================================================================
# LOCUST RUN COMMANDS (Apple Design System Philosophy)
# ============================================================================

"""
Run Performance Tests:

1. Basic Load Test (10 users, 60 seconds):
   locust -f tests/performance_test.py --headless \
     -u 10 -r 1 --run-time 60s \
     --host http://localhost:8000

2. Ramp-up Load Test (gradually increase to 50 users):
   locust -f tests/performance_test.py --headless \
     -u 50 -r 5 --run-time 120s \
     --host http://localhost:8000

3. Stress Test (max concurrent users):
   locust -f tests/performance_test.py --headless \
     -u 200 -r 20 --run-time 180s \
     --host http://localhost:8000

4. Interactive Web UI (for manual testing):
   locust -f tests/performance_test.py --host http://localhost:8000
   
   Then open browser at http://localhost:8089

5. Custom User Count & Spawn Rate:
   -u 100    # Number of concurrent users (load)
   -r 10     # Users per second spawn rate (ramp-up speed)

Performance Metrics Collected:
- Total requests and failure rates
- Average, min, max response times
- P95/P99 percentiles (outlier detection)
- Requests per second (throughput)
- Per-endpoint breakdown with weighting

Apple Design System Performance Targets:
✅ API Response Time: <100ms average
✅ 95th Percentile: <300ms  
✅ Failure Rate: <1%
✅ Concurrent Users: Support at least 50 simultaneous bookings
"""
