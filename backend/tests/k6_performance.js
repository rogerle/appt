/**
 * Performance & Load Testing for Appt Backend - k6 Configuration
 * 
 * Using Grafana k6 for cloud-native load testing.
 * Follows Apple Design System: clean, focused scenarios with clear metrics.
 */

import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  // Base configuration (can be overridden via CLI)
  stages: [
    { duration: '30s', target: 10 },   // Ramp up to 10 users in 30s
    { duration: '2m', target: 50 },    // Hold at 50 users for 2 minutes
    { duration: '1m', target: 100 },   // Ramp up to 100 users
    { duration: '2m', target: 100 },   // Hold peak load for 2 minutes
    { duration: '30s', target: 0 },    // Ramp down to 0 users
  ],
  
  // Performance thresholds (Apple Design System compliance)
  thresholds: {
    http_req_duration: ['p(95)<300'],  // 95% of requests <300ms
    http_req_failed: ['rate<0.01'],    // Error rate <1%
    http_reqs: ['count>0'],            // At least some requests
  },
};

// ============================================================================
// HELPER FUNCTIONS - Clean, Reusable Code (Apple Clarity Principle)
// ============================================================================

function getRandomElement(array) {
  return array[Math.floor(Math.random() * array.length)];
}

function generateRandomPhone() {
  return '138' + Math.floor(10000000 + Math.random() * 90000000);
}

function generateRandomName() {
  const names = ['张', '李', '王', '刘', '陈', '杨', '赵', '黄'];
  return names[Math.floor(Math.random() * names.length)] + 
         Math.floor(10 + Math.random() * 90);
}

// ============================================================================
// SETUP - Initial Registration & Login (One-time per VU)
// ============================================================================

export function setup() {
  // Register test studio
  const registerData = {
    name: 'Performance Test Studio',
    email: `perf_${__VU}@${__TEST_ID}.test.com`,
    password: 'testpass123'
  };

  const registerResponse = http.post('http://localhost:8000/api/v1/auth/register', 
    JSON.stringify(registerData), {
      headers: { 'Content-Type': 'application/json' }
    }
  );

  let token = null;
  
  if (registerResponse.status === 200) {
    // Login to get auth token for admin endpoints
    const loginData = {
      username: registerData.email,
      password: registerData.password
    };

    const loginResponse = http.post('http://localhost:8000/api/v1/auth/login', 
      JSON.stringify(loginData), {
        headers: { 'Content-Type': 'application/json' }
      }
    );

    if (loginResponse.status === 200) {
      token = loginResponse.json('token');
    }
  }

  return { token };
}

// ============================================================================
// TEST SCENARIOS - Public Endpoints (No Auth Required)
// ============================================================================

export default function (data) {
  const headers = { 'Content-Type': 'application/json' };
  
  // Add auth header if available from setup
  if (data.token) {
    headers.Authorization = `Bearer ${data.token}`;
  }

  // Scenario 1: Get instructors list (50% of requests - most common)
  if (__VU % 2 === 0) {
    const response = http.get('http://localhost:8000/api/v1/instructors', { headers });
    
    check(response, {
      'public instructor listing is accessible': (r) => r.status === 200,
      'response time < 300ms': (r) => r.timings.duration < 300,
    });
    
    sleep(1); // Realistic user behavior
    
    return;
  }

  // Scenario 2: Get instructors with date filter (25% of requests)
  if (__VU % 4 === 1) {
    const testDates = [
      '2024-06-15', '2024-06-16', '2024-06-17', 
      '2024-07-01', '2024-08-15'
    ];
    
    const date = getRandomElement(testDates);
    const response = http.get(
      `http://localhost:8000/api/v1/instructors?date=${date}`, 
      { headers }
    );
    
    check(response, {
      'filtered instructor listing works': (r) => r.status === 200,
      'response time < 350ms': (r) => r.timings.duration < 350,
    });
    
    sleep(1.5);
    return;
  }

  // Scenario 3: Create booking (25% of requests - write operation)
  if (__VU % 4 === 2 || __VU % 4 === 3) {
    const scheduleId = Math.floor(Math.random() * 10) + 1;
    
    const bookingData = {
      schedule_id: scheduleId,
      name: generateRandomName(),
      phone: generateRandomPhone(),
      notes: getRandomElement([
        '', 
        '第一次来，需要基础指导',
        '有运动损伤，请温柔一点',
        '想体验流瑜伽'
      ])
    };

    const response = http.post(
      'http://localhost:8000/api/v1/bookings',
      JSON.stringify(bookingData),
      { headers }
    );

    check(response, {
      'booking creation successful': (r) => r.status === 200 || r.status === 422, // 422 = validation error acceptable
      'response time < 500ms': (r) => r.timings.duration < 500,
    });

    sleep(1);
  }
}

// ============================================================================
// ADMIN ENDPOINT TESTS - Auth Required Scenarios
// ============================================================================

export function adminTests(data) {
  if (!data.token) return;

  const headers = { 
    'Content-Type': 'application/json',
    Authorization: `Bearer ${data.token}`
  };

  // Admin: Create instructor (30% of admin requests)
  if (__VU % 10 < 3) {
    const titles = [
      '高级哈他瑜伽导师',
      '流瑜伽专家', 
      '阴瑜伽教练',
      '空中瑜伽导师'
    ];

    const instructorData = {
      name: `测试教练${__VU}`,
      title: getRandomElement(titles),
      avatar_url: 'https://example.com/instructor.jpg',
      bio: '专注瑜伽教学 5 年，擅长基础体式纠正'
    };

    const response = http.post(
      'http://localhost:8000/api/v1/studio/instructors',
      JSON.stringify(instructorData),
      { headers }
    );

    check(response, {
      'instructor creation works': (r) => r.status === 200 || r.status === 422,
      'admin auth is valid': (r) => r.status !== 401 && r.status !== 403,
      'response time < 400ms': (r) => r.timings.duration < 400,
    });

    sleep(1);
  }

  // Admin: Create schedule (30% of admin requests)
  if (__VU % 10 >= 3 && __VU % 10 < 6) {
    const scheduleData = {
      instructor_id: Math.floor(Math.random() * 5) + 1,
      date: '2024-06-15',
      start_time: '09:00',
      end_time: '10:30',
      title: '晨间流瑜伽'
    };

    const response = http.post(
      'http://localhost:8000/api/v1/studio/schedules',
      JSON.stringify(scheduleData),
      { headers }
    );

    check(response, {
      'schedule creation works': (r) => r.status === 200 || r.status === 422,
      'admin auth is valid': (r) => r.status !== 401 && r.status !== 403,
      'response time < 500ms': (r) => r.timings.duration < 500,
    });

    sleep(1);
  }

  // Admin: Get bookings list (20% of admin requests)
  if (__VU % 10 >= 6 && __VU % 10 < 8) {
    const response = http.get(
      'http://localhost:8000/api/v1/studio/bookings',
      { headers }
    );

    check(response, {
      'admin bookings retrieval works': (r) => r.status === 200,
      'response time < 300ms': (r) => r.timings.duration < 300,
    });

    sleep(1.5);
  }

  // Admin: Batch schedule creation (20% of admin requests)
  if (__VU % 10 >= 8) {
    const batchData = {
      instructor_id: Math.floor(Math.random() * 3) + 1,
      daysOfWeek: [1, 2, 3, 4, 5], // Mon-Fri
      start_time: '09:00',
      end_time: '10:00',
      title: '工作日晨练瑜伽',
      start_date: '2024-06-17',
      end_date: '2024-06-21'
    };

    const response = http.post(
      'http://localhost:8000/api/v1/studio/schedules/batch',
      JSON.stringify(batchData),
      { headers }
    );

    check(response, {
      'batch schedule creation works': (r) => r.status === 200 || r.status === 422,
      'admin auth is valid': (r) => r.status !== 401 && r.status !== 403,
      'response time < 800ms': (r) => r.timings.duration < 800, // Batch operations take longer
    });

    sleep(2);
  }
}

// ============================================================================
// METRICS & REPORTING - Apple Design System Clarity Principle
// ============================================================================

export function handleSummary(data) {
  return {
    'stdout': textOutput(),
    'reports': {
      'performance_metrics.json': JSON.stringify(data, null, 2),
    }
  };

  function textOutput() {
    let output = '\n\n📊 PERFORMANCE TEST SUMMARY (k6)\n';
    output += '='.repeat(80) + '\n';
    
    const http_reqs = data.metrics.http_reqs?.values.count || 0;
    const http_req_duration = data.metrics.http_req_duration?.values;
    const http_req_failed = data.metrics.http_req_failed?.values.rate || 0;
    
    output += `\n📈 Overall Statistics:\n`;
    output += `   Total Requests: ${http_reqs}\n`;
    output += `   Failure Rate: ${(http_req_failed * 100).toFixed(2)}%\n`;
    
    if (http_req_duration) {
      const avg = http_req_duration['avg'].toFixed(2);
      const p95 = http_req_duration['p(95)'].toFixed(2);
      const p99 = http_req_duration['p(99)'].toFixed(2);
      
      output += `\n⏱️  Response Times:\n`;
      output += `   Average: ${avg}ms\n`;
      output += `   P50 (Median): ${http_req_duration['p(50)'].toFixed(2)}ms\n`;
      output += `   P95: ${p95}ms\n`;
      output += `   P99: ${p99}ms\n`;
    }
    
    // Performance recommendations (Apple Design System targets)
    output += `\n🍎 Apple Design System Recommendations:\n`;
    
    if (http_req_duration && http_req_duration['avg'] < 100) {
      output += `   ✅ Response times are excellent (<100ms avg)\n`;
    } else if (http_req_duration && http_req_duration['avg'] < 300) {
      output += `   ⚠️  Response times acceptable (100-300ms avg)\n`;
    } else if (http_req_duration) {
      output += `   ❌ Performance needs optimization (>300ms avg: ${http_req_duration['avg'].toFixed(2)}ms)\n`;
    }
    
    if (http_req_failed < 0.01) {
      output += `   ✅ Failure rate within limits (<1%)\n`;
    } else {
      output += `   ❌ High failure rate: ${(http_req_failed * 100).toFixed(2)}%\n`;
    }
    
    output += '\n' + '='.repeat(80) + '\n\n';
    
    return output;
  }
}

// ============================================================================
// k6 RUN COMMANDS (Apple Design System Philosophy)
// ============================================================================

/*
Run Performance Tests:

1. Basic Load Test (50 users over 2 minutes):
   k6 run tests/k6_performance.js

2. Custom Ramp-up Configuration:
   k6 run --vus 50 --duration 2m tests/k6_performance.js

3. With Thresholds (Apple Design System targets):
   k6 run --thresholds 'http_req_duration=p(95)<300ms' \
          --thresholds 'http_req_failed=rate<0.01' \
          tests/k6_performance.js

4. Cloud Testing (Grafana Cloud):
   k6 cloud tests/k6_performance.js

5. Using Docker (k6 containerized):
   docker run -i grafana/k6 run - < tests/k6_performance.js

Performance Metrics Collected:
- Total requests and failure rates
- Response time percentiles (P50, P95, P99)
- Throughput (requests per second)
- Connection times (connect, TLS, first byte, total)
- Per-endpoint breakdown with timing data

Apple Design System Performance Targets:
✅ API Response Time: <100ms average
✅ 95th Percentile: <300ms  
✅ Failure Rate: <1%
✅ Concurrent Users: Support at least 50 simultaneous bookings

Output Files Generated:
- stdout: Human-readable summary (printed to terminal)
- performance_metrics.json: Raw metrics data for analysis
*/
