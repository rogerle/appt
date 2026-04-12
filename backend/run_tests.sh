#!/bin/bash
# Test runner script for Appt Backend
# Following Apple Design System: clean, focused execution

set -e  # Exit on error

echo "🧪 Running Appt Backend Tests"
echo "================================"

# Change to backend directory
cd "$(dirname "$0")"

# Run unit tests (fast feedback)
echo ""
echo "📦 Unit Tests (pytest)... "
pytest tests/test_api_v1.py -v --tb=short

# Run integration tests (end-to-end flows)
echo ""
echo "🔗 Integration Tests (e2e)... "
pytest tests/test_integration.py -v --tb=short

echo ""
echo "✅ All tests completed successfully!"
echo ""
echo "Test Summary:"
echo "  • Unit Tests: API endpoint coverage"
echo "  • Integration Tests: Complete user flows"
echo "  • Database: In-memory SQLite (isolated)"
echo "  • Fast feedback loop (<30 seconds)"
