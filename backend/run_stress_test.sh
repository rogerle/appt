#!/bin/bash

# Stress Test Runner Script
# Executes 50 concurrent booking request simulation

set -e

echo "=============================================="
echo "🚀 Appt Yoga Studio - Stress Test Runner"
echo "=============================================="
echo ""

BASE_URL="${1:-http://localhost:8000}"
NUM_USERS="${2:-50}"

echo "Configuration:"
echo "   Base URL: $BASE_URL"
echo "   Concurrent Users: $NUM_USERS"
echo ""

# Check if server is running
echo "Checking if API server is running..."
if ! curl -s --max-time 3 "$BASE_URL/health" > /dev/null 2>&1; then
    echo "❌ Error: API server not responding at $BASE_URL"
    echo ""
    echo "Please start the server first:"
    echo "  cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    exit 1
fi

echo "✅ Server is running"
echo ""

# Run stress test
echo "Starting stress test with $NUM_USERS concurrent users..."
echo ""

cd "$(dirname "$0")"
python tests/stress_test_50_concurrent.py --url "$BASE_URL" --users "$NUM_USERS"

echo ""
echo "=============================================="
echo "✅ Stress test completed!"
echo "=============================================="
