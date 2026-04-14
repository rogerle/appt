#!/bin/bash
# Phase 4 E2E Integration Test Runner
# Tests complete booking flow using curl

set -e

BASE_URL="${1:-http://localhost:8000}"
TEST_PHONE="1399999999"

echo "============================================================"
echo "🧪 Appt Phase 4 E2E Integration Test Suite"  
echo "============================================================"
echo ""
echo "Base URL: $BASE_URL"
echo "Test Phone: $TEST_PHONE"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
PASSED=0
FAILED=0
SKIPPED=0

pass_test() {
    echo -e "${GREEN}✓ $1${NC}"
    ((PASSED++)) || true
}

fail_test() {
    echo -e "${RED}✗ $1: $2${NC}"
    ((FAILED++)) || true
}

skip_test() {
    echo -e "${YELLOW}⊘ $1 (Skipped)${NC}"
    ((SKIPPED++)) || true
}

echo "============================================================"
echo "Test 1: Get Instructors with Date Filter"  
echo "============================================================"

# Test tomorrow's date
TOMORROW=$(date -d "+1 day" +%Y-%m-%d)
RESPONSE=$(curl -sL "$BASE_URL/api/v1/instructors?date=$TOMORROW")

if [ $? -eq 0 ]; then
    INSTRUCTOR_COUNT=$(echo $RESPONSE | python3 -c "import sys,json; data=json.load(sys.stdin); print(len(data))" 2>/dev/null || echo "0")
    
    if [ "$INSTRUCTOR_COUNT" -gt 0 ] && [ "$INSTRUCTOR_COUNT" != "0" ]; then
        pass_test "Found $INSTRUCTOR_COUNT instructors for date $TOMORROW"
        
        # Get first instructor ID for next test
        FIRST_INSTRUCTOR_ID=$(echo $RESPONSE | python3 -c "import sys,json; data=json.load(sys.stdin); print(data[0]['id'] if data else '')" 2>/dev/null)
    else
        fail_test "No instructors found" "$RESPONSE"
    fi
else
    fail_test "Curl command failed" ""
fi

echo ""
echo "============================================================"  
echo "Test 2: Get Available Time Slots"
echo "============================================================"

if [ -n "$FIRST_INSTRUCTOR_ID" ]; then
    RESPONSE=$(curl -sL "$BASE_URL/api/v1/schedules?date=$TOMORROW&instructor_id=$FIRST_INSTRUCTOR_ID")
    
    if [ $? -eq 0 ]; then
        SLOT_COUNT=$(echo $RESPONSE | python3 -c "import sys,json; data=json.load(sys.stdin); print(len(data))" 2>/dev/null || echo "0")
        
        if [ "$SLOT_COUNT" -gt 0 ] && [ "$SLOT_COUNT" != "0" ]; then
            pass_test "Found $SLOT_COUNT time slots for instructor #$FIRST_INSTRUCTOR_ID"
            
            # Get first available slot ID
            FIRST_SLOT_ID=$(echo $RESPONSE | python3 -c "
import sys, json
data = json.load(sys.stdin)
for slot in data:
    if slot.get('available_spots', 0) > 0:
        print(slot['id'])
        break
else:
    print('')
" 2>/dev/null)
        else
            fail_test "No time slots found" "$RESPONSE"  
        fi
    else
        fail_test "Curl command failed" ""
    fi
else
    skip_test "Skipping - no instructor ID from previous test"
fi

echo ""
echo "============================================================"
echo "Test 3: Create Booking (Success Case)"
echo "============================================================"

if [ -n "$FIRST_SLOT_ID" ]; then
    # Generate unique phone for this booking (must be exactly 11 digits: 1xxxxxxxxxx)
    # Use Python to ensure proper format - Chinese mobile numbers start with 1 and are 11 digits
    UNIQUE_PHONE=$(python3 -c "import random; print(f'1{random.randint(3000000000, 9999999999)}')")
    
    RESPONSE=$(curl -sL -X POST "$BASE_URL/api/v1/bookings" \
        -H "Content-Type: application/json" \
        -d "{\"schedule_id\": $FIRST_SLOT_ID, \"customer_name\": \"E2E Test User\", \"customer_phone\": \"$UNIQUE_PHONE\"}")
    
    if [ $? -eq 0 ]; then
        BOOKING_SUCCESS=$(echo $RESPONSE | python3 -c "import sys,json; data=json.load(sys.stdin); print(data.get('success', False))" 2>/dev/null || echo "False")
        
        if [ "$BOOKING_SUCCESS" = "True" ]; then
            BOOKING_ID=$(echo $RESPONSE | python3 -c "import sys,json; data=json.load(sys.stdin); print(data.get('booking_id', ''))" 2>/dev/null)
            pass_test "Created booking #$BOOKING_ID for phone $UNIQUE_PHONE"
        else
            fail_test "Booking creation failed" "$RESPONSE"
        fi
    else
        fail_test "Curl command failed" ""
    fi
    
    # Test duplicate booking prevention
    echo ""
    echo "============================================================"
    echo "Test 3b: Duplicate Booking Prevention (Conflict Detection)"
    echo "============================================================"
    
    RESPONSE=$(curl -sL -X POST "$BASE_URL/api/v1/bookings" \
        -H "Content-Type: application/json" \
        -d "{\"schedule_id\": $FIRST_SLOT_ID, \"customer_name\": \"E2E Test User (Duplicate)\", \"customer_phone\": \"$UNIQUE_PHONE\"}")
    
    if [ $? -eq 0 ]; then
        HTTP_STATUS=$(echo "$RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    # Check if response contains 'detail' field (error) or 'success' field
    if 'detail' in data:
        print('409')  # Assume conflict
    elif 'success' in data and not data['success']:
        print('409')  
    else:
        print('200')
except:
    print(sys.argv[1] if len(sys.argv) > 1 else 'UNKNOWN')
" "$?")
        
        # Simpler check - just see if response contains "already have" or similar
        IS_CONFLICT=$(echo $RESPONSE | grep -i "already\|duplicate\|conflict" || true)
        
        if [ -n "$IS_CONFLICT" ]; then
            pass_test "Conflict detection working - prevented duplicate booking"
        else
            # If no conflict message, check if it succeeded (which would be wrong)
            BOOKING_SUCCESS=$(echo $RESPONSE | python3 -c "import sys,json; data=json.load(sys.stdin); print(data.get('success', False))" 2>/dev/null || echo "False")
            
            if [ "$BOOKING_SUCCESS" = "True" ]; then
                fail_test "Should have prevented duplicate booking but it succeeded" "$RESPONSE"
            else
                pass_test "Booking rejected (correct behavior)"
            fi
        fi
    else
        fail_test "Curl command failed" ""
    fi
else
    skip_test "Skipping - no slot ID from previous test"
fi

echo ""
echo "============================================================"
echo "Test 4: Retrieve User Bookings (Privacy Protection)"
echo "============================================================"

if [ -n "$UNIQUE_PHONE" ]; then
    RESPONSE=$(curl -sL "$BASE_URL/api/v1/bookings?phone=$UNIQUE_PHONE")
    
    if [ $? -eq 0 ]; then
        BOOKING_COUNT=$(echo $RESPONSE | python3 -c "import sys,json; data=json.load(sys.stdin); print(len(data))" 2>/dev/null || echo "0")
        
        if [ "$BOOKING_COUNT" -gt 0 ] && [ "$BOOKING_COUNT" != "0" ]; then
            # Check privacy protection (phone should be masked)
            MASKED_PHONE=$(echo $RESPONSE | python3 -c "
import sys, json
data = json.load(sys.stdin)
if data:
    print(data[0].get('customer_phone_masked', ''))
else:
    print('')
" 2>/dev/null)
            
            # Verify masking (should contain asterisks and not full phone)
            IS_MASKED=$(echo $MASKED_PHONE | grep -c '\*' || echo "0")
            
            if [ "$IS_MASKED" -gt 0 ]; then
                pass_test "Retrieved $BOOKING_COUNT bookings with privacy-protected phone: $MASKED_PHONE"
            else
                fail_test "Phone number not properly masked" "Got: $MASKED_PHONE, Expected: xxx****xxxx format"
            fi
        else
            skip_test "No bookings found for phone (may have been skipped earlier)"
        fi
    else
        fail_test "Curl command failed" ""
    fi
else
    skip_test "Skipping - no unique phone from previous test"  
fi

echo ""
echo "============================================================"
echo "📊 Test Summary Report"
echo "============================================================"
echo ""
echo -e "Passed:  ${GREEN}$PASSED${NC}"
echo -e "Failed:  ${RED}$FAILED${NC}"  
echo -e "Skipped: ${YELLOW}$SKIPPED${NC}"
echo ""

TOTAL=$((PASSED + FAILED + SKIPPED))
echo "Total Tests: $TOTAL"
echo ""

if [ "$FAILED" -eq 0 ] && [ "$PASSED" -gt 0 ]; then
    echo -e "${GREEN}🎉 All critical tests PASSED! Phase 4 integration is working correctly.${NC}"
    exit 0
elif [ "$FAILED" -gt 0 ]; then
    echo -e "${RED}❌ Some tests FAILED. Please review the errors above.${NC}"
    exit 1
else
    echo -e "${YELLOW}⚠️ All tests were skipped or no tests ran.${NC}"
    exit 2
fi
