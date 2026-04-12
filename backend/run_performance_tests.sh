#!/bin/bash
# Performance & Load Testing Runner Script for Appt Backend
# Following Apple Design System: clean, focused execution with clear metrics

set -e  # Exit on error

echo "🧪 Running Appt Backend Performance Tests"
echo "=========================================="

# Change to backend directory
cd "$(dirname "$0")"

# Check if running in development mode (localhost) or production
HOST="${HOST:-http://localhost:8000}"

echo ""
echo "📊 Test Configuration:"
echo "   Target Host: $HOST"
echo "   Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# ============================================================================
# PHASE 1: Basic Locust Load Test (Unit Testing Performance)
# ============================================================================

echo "🚀 Phase 1: Basic Load Test (10 users, 60 seconds)"
echo "---------------------------------------------------"

if [ -f "/home/claw/.openclaw/workspace-rogers/projects/appt/backend/tests/performance_test.py" ]; then
    
    # Run locust in headless mode with basic configuration
    cd /home/claw/.openclaw/workspace-rogers/projects/appt/backend
    
    # Install performance dependencies if needed
    pip install -q -r tests/requirements-performance.txt 2>/dev/null || true
    
    echo "Running Locust load test..."
    
    locust \
        -f tests/performance_test.py \
        --headless \
        -u 10 \
        -r 1 \
        --run-time 60s \
        --host $HOST \
        --logfile /tmp/locust_basic.log 2>&1 | tee /tmp/locust_basic_output.log || true
    
    echo ""
    echo "✅ Phase 1 Complete: Basic Load Test"
    
else
    echo "⚠️  Performance test file not found. Skipping Phase 1."
fi

# ============================================================================
# PHASE 2: Ramp-up Stress Test (Gradually Increase Load)
# ============================================================================

echo ""
echo "📈 Phase 2: Ramp-up Stress Test (50 users over 3 minutes)"
echo "--------------------------------------------------------"

if [ -f "/home/claw/.openclaw/workspace-rogers/projects/appt/backend/tests/performance_test.py" ]; then
    
    echo "Running Locust ramp-up test..."
    
    locust \
        -f tests/performance_test.py \
        --headless \
        -u 50 \
        -r 5 \
        --run-time 180s \
        --host $HOST \
        --logfile /tmp/locust_rampup.log 2>&1 | tee /tmp/locust_rampup_output.log || true
    
    echo ""
    echo "✅ Phase 2 Complete: Ramp-up Stress Test"
    
else
    echo "⚠️  Performance test file not found. Skipping Phase 2."
fi

# ============================================================================
# PHASE 3: k6 Load Testing (Alternative Framework)
# ============================================================================

echo ""
echo "🔧 Phase 3: k6 Cloud-Native Load Test"
echo "--------------------------------------"

if command -v k6 &> /dev/null; then
    
    echo "Running k6 load test..."
    
    cd /home/claw/.openclaw/workspace-rogers/projects/appt/backend/tests
    
    k6 run \
        --vus 25 \
        --duration 2m \
        --thresholds 'http_req_duration=p(95)<300ms' \
        --thresholds 'http_req_failed=rate<0.01' \
        k6_performance.js 2>&1 | tee /tmp/k6_output.log || true
    
    echo ""
    echo "✅ Phase 3 Complete: k6 Load Test"
    
else
    echo "⚠️  k6 not installed (install via: https://k6.io/docs/getting-started/installation/)"
    echo "   Skipping Phase 3."
fi

# ============================================================================
# PHASE 4: Performance Metrics Summary
# ============================================================================

echo ""
echo "📊 Performance Metrics Collection"
echo "----------------------------------"

# Check if any log files were generated
if [ -f "/tmp/locust_basic_output.log" ] || [ -f "/tmp/k6_output.log" ]; then
    
    echo "Analyzing performance metrics..."
    
    # Extract key metrics from logs (simplified extraction)
    total_requests=0
    avg_response_time="N/A"
    failure_rate="N/A"
    
    if [ -f "/tmp/locust_basic_output.log" ]; then
        # Parse Locust output for basic stats
        total_requests=$(grep "Total requests:" /tmp/locust_basic_output.log 2>/dev/null | head -1 || echo "0")
        avg_response_time=$(grep "Average response time:" /tmp/locust_basic_output.log 2>/dev/null | head -1 || echo "N/A")
    fi
    
    if [ -f "/tmp/k6_output.log" ]; then
        # Parse k6 output for metrics
        k6_total=$(grep "Total Requests:" /tmp/k6_output.log 2>/dev/null | grep -oP '\d+' | head -1 || echo "0")
        k6_avg=$(grep "Average:" /tmp/k6_output.log 2>/dev/null | grep -oP '[\d.]+(?=ms)' | head -1 || echo "N/A")
        
        if [ "$k6_total" != "" ]; then
            total_requests=$k6_total
        fi
        
        if [ "$k6_avg" != "N/A" ]; then
            avg_response_time="$k6_avg ms average"
        fi
    fi
    
    echo ""
    echo "📈 Performance Summary:"
    echo "   Total Requests: ${total_requests:-0}"
    echo "   Average Response Time: ${avg_response_time}"
    
else
    echo "⚠️  No performance test logs found. Run tests first."
fi

# ============================================================================
# FINAL REPORT - Apple Design System Recommendations
# ============================================================================

echo ""
echo "🍎 Apple Design System Performance Analysis"
echo "-------------------------------------------"

if [ "$total_requests" != "0" ] && [ "$avg_response_time" != "N/A" ]; then
    
    # Extract numeric value from response time string
    avg_ms=$(echo "$avg_response_time" | grep -oP '[\d.]+' || echo "0")
    
    if command -v bc &> /dev/null; then
        
        # Compare against Apple Design System targets
        if [ $(echo "$avg_ms < 100" | bc -l) -eq 1 ]; then
            echo "✅ Response times are excellent (<100ms)"
        elif [ $(echo "$avg_ms < 300" | bc -l) -eq 1 ]; then
            echo "⚠️  Response times acceptable (100-300ms)"
        else
            echo "❌ Performance needs optimization (>300ms, avg: ${avg_response_time})"
        fi
        
    else
        echo "ℹ️  bc not installed. Manual performance analysis required."
    fi
    
else
    echo "⚠️  No metrics available for analysis."
fi

echo ""
echo "=========================================="
echo "✅ Performance Testing Complete!"
echo "=========================================="
echo ""
echo "📁 Output Files Generated:"
echo "   • /tmp/locust_basic_output.log"
echo "   • /tmp/locust_rampup_output.log"  
echo "   • /tmp/k6_output.log (if k6 available)"
echo ""
