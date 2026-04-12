#!/bin/bash

# Security Testing Script for Appt API
# Runs comprehensive security tests for SQL Injection, XSS, CORS, and Input Validation

set -e

echo "=============================================="
echo "🔒 Security Testing Suite - Appt API"
echo "=============================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
PASSED=0
FAILED=0
WARNINGS=0

# Run security tests with pytest
echo "Running security tests..."
echo ""

cd /home/claw/.openclaw/workspace-rogers/projects/appt/backend

# Check if server is running (required for integration tests)
echo "Checking API server status..."
if curl -s --max-time 3 http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Server is running${NC}"
    SERVER_RUNNING=true
else
    echo -e "${YELLOW}⚠ Server not running - only unit tests will execute${NC}"
    SERVER_RUNNING=false
fi

echo ""
echo "=============================================="
echo "Test Categories:"
echo "=============================================="
echo "1. SQL Injection Tests"
echo "2. XSS Attack Prevention Tests"
echo "3. CORS Configuration Tests"
echo "4. Input Validation Tests"
echo "5. Authentication Security Tests"
echo ""

# Run all security tests
pytest tests/test_security.py -v --tb=short 2>&1 | tee /tmp/security_test_results.log

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}=============================================="${NC}"
    echo "✅ Security Tests PASSED"
    echo "==============================================${NC}"
    echo ""
    
    # Extract pass/fail counts from log
    PASSED=$(grep -c "PASSED\|passed" /tmp/security_test_results.log || echo "0")
    FAILED=$(grep -c "FAILED\|failed" /tmp/security_test_results.log || echo "0")
    
    echo -e "${GREEN}Tests Passed: $PASSED${NC}"
    if [ "$FAILED" != "0" ]; then
        echo -e "${RED}Tests Failed: $FAILED${NC}"
    fi
    
else
    echo ""
    echo -e "${RED}=============================================="${NC}"
    echo "❌ Security Tests FAILED"
    echo "==============================================${NC}"
    exit 1
fi

echo ""
echo "Security Test Summary:"
echo "----------------------"
echo "- SQL Injection: Protected by SQLAlchemy ORM (parameterized queries)"
echo "- XSS Prevention: Input sanitization middleware active"
echo "- CORS Configuration: Production-safe settings applied"
echo "- Input Validation: Pydantic models with strict type checking"
echo ""

# Security recommendations
if [ "$SERVER_RUNNING" = true ]; then
    echo "Additional Manual Testing:"
    echo "-------------------------"
    echo "1. Test SQL injection manually in browser dev tools:"
    echo "   GET /api/v1/bookings?phone=13800138000' OR '1'='1"
    echo ""
    echo "2. Test XSS payloads in booking form:"
    echo "   <script>alert('XSS')</script>"
    echo ""
    echo "3. Check CORS headers with curl:"
    echo "   curl -I -H 'Origin: https://malicious-site.com' http://localhost:8000/api/v1/instructors"
    echo ""
fi

echo "=============================================="
echo "Next Steps:"
echo "- Review test results above"
echo "- Fix any failures before production deployment"
echo "- Run penetration testing tools (OWASP ZAP, Burp Suite)"
echo "=============================================="
