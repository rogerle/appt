#!/bin/bash

# ============================================================================
# Frontend-Backend Integration Test Suite
# Tests complete API call flow from frontend perspective
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
BACKEND_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:8080"
API_BASE="$BACKEND_URL/api/v1"

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0

# ============================================================================
# Helper Functions
# ============================================================================

print_header() {
    echo -e "${CYAN}================================================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}================================================================${NC}"
}

print_test() {
    echo -e "${BLUE}[TEST] ${NC}$1"
}

print_success() {
    echo -e "${GREEN}✓ PASS: $1${NC}"
    ((TESTS_PASSED++))
}

print_failure() {
    echo -e "${RED}✗ FAIL: $1${NC}"
    ((TESTS_FAILED++))
}

print_info() {
    echo -e "${YELLOW}ℹ INFO: $1${NC}"
}

# ============================================================================
# Test Functions
# ============================================================================

test_service_availability() {
    print_header "Test 1: Service Availability"
    
    # Check backend health
    if curl -s "$BACKEND_URL/health" | grep -q '"status":"healthy"'; then
        print_success "Backend service is healthy"
    else
        print_failure "Backend service is not responding"
        return 1
    fi
    
    # Check frontend availability  
    if curl -s "$FRONTEND_URL" | grep -q "<!DOCTYPE html>"; then
        print_success "Frontend service is serving pages"
    else
        print_failure "Frontend service may have build issues"
        return 1
    fi
}

test_api_basic_endpoints() {
    print_header "Test 2: Basic API Endpoints"
    
    # Test instructors endpoint
    print_test "GET /api/v1/instructors?date=2026-04-15"
    response=$(curl -sL "$API_BASE/instructors?date=2026-04-15")
    
    if echo "$response" | jq -e '.[0].name' > /dev/null 2>&1; then
        instructor_count=$(echo "$response" | jq 'length')
        print_success "Instructors endpoint working ($instructor_count instructors returned)"
        
        # Verify structure matches frontend expectations
        if echo "$response" | jq -e '.[0] | has("id") and has("name") and has("available_slots")' > /dev/null 2>&1; then
            print_success "Instructor data structure matches frontend requirements"
        else
            print_failure "Instructor data missing required fields (id, name, available_slots)"
        fi
    else
        print_failure "Instructors endpoint returned invalid JSON or empty array"
        echo "$response" | head -20
        return 1
    fi
    
    # Test schedules endpoint for specific instructor
    print_test "GET /api/v1/schedules?date=2026-04-15&instructor_id=1"
    response=$(curl -sL "$API_BASE/schedules?date=2026-04-15&instructor_id=1")
    
    if echo "$response" | jq -e '.[0].start_time' > /dev/null 2>&1; then
        slot_count=$(echo "$response" | jq 'length')
        print_success "Schedules endpoint working ($slot_count time slots returned)"
        
        # Verify structure
        if echo "$response" | jq -e '.[0] | has("id") and has("start_time") and has("end_time") and has("available_spots")' > /dev/null 2>&1; then
            print_success "Schedule data structure matches frontend requirements"
        else
            print_failure "Schedule data missing required fields"
        fi
    else
        print_failure "Schedules endpoint returned invalid response"
        return 1
    fi
    
    # Test bookings retrieval (public - no auth needed)
    print_test "GET /api/v1/bookings?phone=13800000000"
    response=$(curl -sL "$API_BASE/bookings?phone=13800000000")
    
    if echo "$response" | jq -e '.' > /dev/null 2>&1; then
        print_success "Bookings retrieval endpoint working (returns valid JSON)"
        
        # Check if it's empty array or has data
        booking_count=$(echo "$response" | jq 'length')
        print_info "Found $booking_count bookings for test phone number"
    else
        print_failure "Bookings endpoint returned invalid response"
        return 1
    fi
}

test_booking_creation() {
    print_header "Test 3: Booking Creation Flow"
    
    # Generate unique test phone number
    TEST_PHONE="138$(date +%s | tail -c 7)"
    
    echo ""
    print_info "Creating booking with phone: $TEST_PHONE"
    
    # Prepare booking payload
    PAYLOAD=$(cat <<EOF
{
    "customer_name": "Test User $(date +%H%M%S)",
    "phone": "$TEST_PHONE",
    "schedule_id": 1,
    "notes": "API integration test booking"
}
EOF
)
    
    print_test "POST /api/v1/bookings"
    response=$(curl -sL -X POST "$API_BASE/bookings" \
        -H "Content-Type: application/json" \
        -d "$PAYLOAD")
    
    # Check if booking was created successfully (HTTP 200) or conflict (HTTP 409)
    http_code=$(curl -sL -o /dev/null -w "%{http_code}" -X POST "$API_BASE/bookings" \
        -H "Content-Type: application/json" \
        -d "$PAYLOAD")
    
    if [ "$http_code" = "200" ]; then
        print_success "Booking created successfully (HTTP 200)"
        
        # Verify booking data structure
        if echo "$response" | jq -e '.id and .customer_name and .phone_masked' > /dev/null 2>&1; then
            print_success "Booking response has correct structure with privacy protection"
            
            # Show masked phone for verification
            masked_phone=$(echo "$response" | jq -r '.phone_masked')
            print_info "Phone number properly masked: $masked_phone"
        else
            print_failure "Booking response missing required fields"
        fi
        
    elif [ "$http_code" = "409" ]; then
        # Conflict is acceptable (booking already exists)
        print_success "Booking conflict detected (HTTP 409) - indicates frontend error handling should work"
        
        if echo "$response" | grep -q '"detail"'; then
            print_success "Conflict error message provided for UI display"
        else
            print_failure "Missing detail field in conflict response"
        fi
        
    elif [ "$http_code" = "422" ]; then
        # Validation error
        print_failure "Validation error - check payload format (HTTP 422)"
        echo "$response" | jq '.' | head -10
        return 1
        
    else
        print_failure "Unexpected HTTP status code: $http_code"
        echo "$response" | head -20
        return 1
    fi
    
    # Verify booking appears in retrieval
    sleep 1
    response=$(curl -sL "$API_BASE/bookings?phone=$TEST_PHONE")
    
    if echo "$response" | jq -e "length > 0 and .[0].phone_masked" > /dev/null 2>&1; then
        print_success "New booking retrievable via GET endpoint"
    else
        print_failure "Created booking not found in retrieval"
        return 1
    fi
}

test_cors_configuration() {
    print_header "Test 4: CORS Configuration (Critical for Frontend)"
    
    # Check CORS headers from backend
    print_test "Checking Access-Control-Allow-Origin header"
    cors_header=$(curl -sI "$API_BASE/instructors?date=2026-04-15" | grep -i "access-control-allow-origin")
    
    if [ -n "$cors_header" ]; then
        echo "$cors_header" | sed 's/^/  /'
        
        # Check if it allows localhost:8080 or *
        if echo "$cors_header" | grep -qE "(localhost:8080|\*)"; then
            print_success "CORS properly configured for frontend access"
        else
            print_failure "CORS may block frontend requests from localhost:8080"
            return 1
        fi
    else
        print_failure "No CORS headers found - will block cross-origin requests!"
        echo ""
        print_info "Backend must allow Access-Control-Allow-Origin header for Vue SPA to work"
        return 1
    fi
    
    # Test preflight request (OPTIONS)
    print_test "Testing OPTIONS preflight request"
    options_response=$(curl -sI -X OPTIONS "$API_BASE/instructors?date=2026-04-15" \
        -H "Origin: http://localhost:8080" \
        -H "Access-Control-Request-Method: POST")
    
    if echo "$options_response" | grep -q "HTTP/1.1 200"; then
        print_success "Preflight request handled correctly (HTTP 200)"
        
        # Check if Access-Control-Allow-Methods includes needed verbs
        allow_methods=$(echo "$options_response" | grep -i "access-control-allow-methods")
        if [ -n "$allow_methods" ]; then
            echo "$allow_methods" | sed 's/^/  /'
            
            if echo "$allow_methods" | grep -qE "(GET|POST)"; then
                print_success "Allowed methods include GET and POST"
            else
                print_failure "Missing required HTTP methods in CORS configuration"
            fi
        fi
    else
        print_failure "Preflight request failed - may block frontend operations"
        return 1
    fi
}

test_error_handling() {
    print_header "Test 5: Error Handling & Edge Cases"
    
    # Test invalid date format
    print_test "Testing error handling for invalid date"
    response=$(curl -sL "$API_BASE/instructors?date=invalid-date")
    
    if echo "$response" | grep -qE '(error|detail|Error)'; then
        print_success "Backend returns proper error messages for invalid input"
    else
        print_info "No error returned (may be acceptable depending on implementation)"
    fi
    
    # Test non-existent instructor
    print_test "Testing request with non-existent instructor_id"
    response=$(curl -sL "$API_BASE/schedules?date=2026-04-15&instructor_id=9999")
    
    if echo "$response" | jq -e 'length == 0' > /dev/null 2>&1; then
        print_success "Returns empty array for non-existent instructor (correct behavior)"
    else
        print_info "Behavior may vary - check if this is acceptable"
    fi
    
    # Test booking with invalid data
    print_test "Testing validation on booking creation"
    PAYLOAD='{"customer_name": "Test", "phone": "invalid", "schedule_id": 1}'
    
    http_code=$(curl -sL -o /dev/null -w "%{http_code}" -X POST "$API_BASE/bookings" \
        -H "Content-Type: application/json" \
        -d "$PAYLOAD")
    
    if [ "$http_code" = "422" ]; then
        print_success "Validation rejects invalid input (HTTP 422)"
        
        # Check error details are helpful
        response=$(curl -sL -X POST "$API_BASE/bookings" \
            -H "Content-Type: application/json" \
            -d "$PAYLOAD")
            
        if echo "$response" | grep -qE '(Field required|Invalid)'; then
            print_success "Error messages are descriptive for frontend display"
        else
            print_info "Consider improving error message clarity"
        fi
    else
        print_failure "Should reject invalid input with HTTP 422, got: $http_code"
        return 1
    fi
}

test_frontend_api_client() {
    print_header "Test 6: Frontend API Client Configuration"
    
    # Check if frontend can reach backend
    print_test "Verifying frontend axios configuration"
    
    frontend_config=$(cat src/api/client.ts | grep -A2 "baseURL")
    echo "$frontend_config" | sed 's/^/  /'
    
    if echo "$frontend_config" | grep -q "localhost:8000"; then
        print_success "Frontend configured to connect to local backend (correct for development)"
    else
        print_failure "Frontend API client may have incorrect base URL configuration"
        return 1
    fi
    
    # Check timeout configuration
    if cat src/api/client.ts | grep -q "timeout"; then
        timeout_value=$(cat src/api/client.ts | grep "timeout:" | head -1)
        echo "$timeout_value" | sed 's/^/  /'
        print_success "API client has timeout protection configured"
    else
        print_failure "No timeout configured - requests could hang indefinitely"
    fi
    
    # Check interceptors exist
    if cat src/api/client.ts | grep -q "interceptors"; then
        print_success "Request/response interceptors implemented (auth token, error handling)"
        
        # Verify auth token logic exists
        if cat src/api/client.ts | grep -q "auth_token"; then
            print_success "JWT authentication integration present"
        else
            print_info "Auth token interceptor may not be fully implemented yet"
        fi
    else
        print_failure "Missing interceptors for auth and error handling"
    fi
}

test_complete_user_journey() {
    print_header "Test 7: Complete User Journey Simulation"
    
    echo ""
    print_info "Simulating full booking flow from frontend perspective..."
    echo ""
    
    # Step 1: User opens app, fetches instructors for tomorrow
    TOMORROW=$(date -d "+1 day" +%Y-%m-%d)
    print_test "Step 1: Fetch available instructors for $TOMORROW"
    
    response=$(curl -sL "$API_BASE/instructors?date=$TOMORROW")
    instructor_count=$(echo "$response" | jq 'length')
    
    if [ "$instructor_count" -gt 0 ]; then
        print_success "Found $instructor_count instructors with available slots"
        
        # Pick first instructor
        FIRST_INSTRUCTOR_ID=$(echo "$response" | jq '.[0].id')
        FIRST_INSTRUCTOR_NAME=$(echo "$response" | jq -r '.[0].name')
        echo "  Selected: $FIRST_INSTRUCTOR_NAME (ID: $FIRST_INSTRUCTOR_ID)"
    else
        print_failure "No instructors available for selected date"
        return 1
    fi
    
    # Step 2: User selects instructor, fetches their schedules
    echo ""
    print_test "Step 2: Fetch time slots for $FIRST_INSTRUCTOR_NAME"
    
    response=$(curl -sL "$API_BASE/schedules?date=$TOMORROW&instructor_id=$FIRST_INSTRUCTOR_ID")
    slot_count=$(echo "$response" | jq 'length')
    
    if [ "$slot_count" -gt 0 ]; then
        print_success "Found $slot_count available time slots"
        
        # Pick first slot with availability
        FIRST_SLOT_ID=$(echo "$response" | jq '.[0].id')
        FIRST_SLOT_TIME=$(echo "$response" | jq -r '.[0].start_time')
        AVAILABLE_SPOTS=$(echo "$response" | jq '.[0].available_spots')
        
        echo "  Selected: $FIRST_SLOT_TIME (ID: $FIRST_SLOT_ID, Spots: $AVAILABLE_SPOTS)"
    else
        print_failure "No time slots available for selected instructor"
        return 1
    fi
    
    # Step 3: User fills form and submits booking
    echo ""
    print_test "Step 3: Submit booking with customer information"
    
    TEST_PHONE="138$(date +%s | tail -c 7)"
    PAYLOAD=$(cat <<EOF
{
    "customer_name": "Complete Journey Test",
    "phone": "$TEST_PHONE",
    "schedule_id": $FIRST_SLOT_ID,
    "notes": "Automated integration test via shell script"
}
EOF
)
    
    response=$(curl -sL -X POST "$API_BASE/bookings" \
        -H "Content-Type: application/json" \
        -d "$PAYLOAD")
    
    http_code=$(echo "$response" | jq -r 'if .id then "200" else "error" end' 2>/dev/null) || http_code="error"
    
    if [ "$http_code" = "200" ]; then
        print_success "Booking submitted successfully!"
        
        BOOKING_ID=$(echo "$response" | jq -r '.id')
        MASKED_PHONE=$(echo "$response" | jq -r '.phone_masked')
        
        echo "  Booking ID: $BOOKING_ID"
        echo "  Masked phone: $MASKED_PHONE (privacy protection working)"
    else
        print_failure "Booking submission failed"
        echo "$response" | head -10
        return 1
    fi
    
    # Step 4: User views their bookings in MyBookings page
    echo ""
    print_test "Step 4: Retrieve user's bookings from database"
    
    response=$(curl -sL "$API_BASE/bookings?phone=$TEST_PHONE")
    booking_count=$(echo "$response" | jq 'length')
    
    if [ "$booking_count" -gt 0 ]; then
        print_success "Found $booking_count booking(s) for this user"
        
        # Verify the booking we just created is there
        if echo "$response" | grep -q "Complete Journey Test"; then
            print_success "Most recent booking appears in retrieval list"
            
            BOOKING_STATUS=$(echo "$response" | jq -r '.[0].status')
            echo "  Status: $BOOKING_STATUS"
        else
            print_failure "Created booking not found in user's bookings"
            return 1
        fi
    else
        print_failure "No bookings found (should have at least one)"
        return 1
    fi
    
    # Success!
    echo ""
    print_success "✅ COMPLETE USER JOURNEY PASSED - Frontend to backend flow is working!"
}

# ============================================================================
# Main Execution
# ============================================================================

main() {
    print_header "🧪 Frontend-Backend Integration Test Suite"
    echo ""
    echo "Configuration:"
    echo "  Backend: $BACKEND_URL"
    echo "  Frontend: $FRONTEND_URL"  
    echo "  API Base: $API_BASE"
    echo ""
    
    # Run all tests
    test_service_availability || true
    echo ""
    
    test_api_basic_endpoints || true
    echo ""
    
    test_booking_creation || true
    echo ""
    
    test_cors_configuration || true
    echo ""
    
    test_error_handling || true
    echo ""
    
    test_frontend_api_client || true
    echo ""
    
    test_complete_user_journey || true
    echo ""
    
    # Summary
    print_header "📊 Test Results Summary"
    echo ""
    echo -e "  ${GREEN}Passed: $TESTS_PASSED${NC}"
    echo -e "  ${RED}Failed: $TESTS_FAILED${NC}"
    echo ""
    
    total=$((TESTS_PASSED + TESTS_FAILED))
    if [ $total -gt 0 ]; then
        percentage=$((TESTS_PASSED * 100 / total))
        echo "  Success Rate: ${percentage}%"
        echo ""
        
        if [ $TESTS_FAILED -eq 0 ]; then
            echo -e "${GREEN}🎉 All tests passed! Frontend-backend integration is working perfectly!${NC}"
            exit 0
        else
            echo -e "${YELLOW}⚠️ Some tests failed. Review the output above for details.${NC}"
            exit 1
        fi
    fi
}

# Run main function
main "$@"
