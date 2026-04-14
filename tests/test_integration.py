#!/usr/bin/env python3
"""
Phase 4 Integration Tests - Complete Booking Flow Verification

Tests the complete user journey from browsing instructors to creating a booking.
Uses pytest + httpx for end-to-end API testing.

Run with: pytest tests/test_integration.py -xvs
"""

import pytest
from datetime import date, timedelta
from httpx import AsyncClient


# Test configuration
BASE_URL = "http://localhost:8000"  # Default to local development server
TEST_PHONE_BASE = "13999999"  # Base for generating unique phone numbers


@pytest.fixture(scope="module")
async def client():
    """Create async HTTP client for all tests in module."""
    async with AsyncClient(base_url=BASE_URL, timeout=10.0) as ac:
        yield ac


class TestInstructorAPI:
    """Test instructor listing and filtering."""

    @pytest.mark.asyncio
    async def test_get_instructors_with_date_filter(self, client):
        """P4-03: Verify instructors returned with available slots for a date."""
        target_date = (date.today() + timedelta(days=1)).isoformat()
        
        response = await client.get("/api/v1/instructors", params={"date": target_date})
        
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Should return at least one instructor
        assert isinstance(data, list), "Response should be a list"
        assert len(data) >= 1, "Should have at least one instructor"
        
        # Check structure of first instructor
        if len(data) > 0:
            instructor = data[0]
            assert "id" in instructor
            assert "name" in instructor
            assert "available_slots" in instructor
            
            print(f"✓ Found {len(data)} instructors for date {target_date}")


class TestScheduleAPI:
    """Test schedule availability queries."""

    @pytest.mark.asyncio
    async def test_get_available_slots_by_instructor(self, client):
        """P4-04: Verify time slots returned with correct availability info."""
        target_date = (date.today() + timedelta(days=1)).isoformat()
        
        # First get any instructor ID
        instructors_response = await client.get("/api/v1/instructors", params={"date": target_date})
        assert instructors_response.status_code == 200
        
        if not instructors_response.json():
            pytest.skip("No instructors available for testing")
            
        instructor_id = instructors_response.json()[0]["id"]
        
        # Now query schedules for that instructor
        response = await client.get(
            "/api/v1/schedules", 
            params={"date": target_date, "instructor_id": instructor_id}
        )
        
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert isinstance(data, list), "Response should be a list"
        
        # Check slot structure if we have any
        if len(data) > 0:
            slot = data[0]
            assert "id" in slot
            assert "start_time" in slot
            assert "end_time" in slot
            assert "available_spots" in slot
            
            print(f"✓ Found {len(data)} time slots for instructor {instructor_id}")


class TestBookingAPI:
    """Test booking creation and retrieval."""

    @pytest.mark.asyncio
    async def test_create_booking_success(self, client):
        """P4-05: Verify successful booking creation with conflict detection."""
        # Find an available slot
        target_date = (date.today() + timedelta(days=1)).isoformat()
        
        schedules_response = await client.get(
            "/api/v1/schedules", 
            params={"date": target_date}
        )
        
        assert schedules_response.status_code == 200
        
        if not schedules_response.json():
            pytest.skip("No available time slots for testing")
            
        # Use first slot that has availability
        available_slot = next(
            (slot for slot in schedules_response.json() if slot["available_spots"] > 0),
            None
        )
        
        if not available_slot:
            pytest.skip("No slots with available spots found")
            
        # Generate unique phone number to avoid conflicts
        import random
        test_phone = f"{TEST_PHONE_BASE}{random.randint(100, 999)}"
        
        booking_data = {
            "schedule_id": available_slot["id"],
            "customer_name": "Integration Test User",
            "customer_phone": test_phone
        }
        
        response = await client.post("/api/v1/bookings", json=booking_data)
        
        assert response.status_code == 200, f"Booking failed: {response.text}"
        result = response.json()
        
        assert result["success"] is True
        assert "message" in result
        assert "booking_id" in result
        
        print(f"✓ Created booking #{result['booking_id']} for phone {test_phone}")


    @pytest.mark.asyncio  
    async def test_get_bookings_by_phone(self, client):
        """Verify user can retrieve their bookings with privacy protection."""
        # Create a test booking first (reuse from previous test)
        import random
        test_phone = f"{TEST_PHONE_BASE}{random.randint(100, 999)}"
        
        target_date = (date.today() + timedelta(days=1)).isoformat()
        schedules_response = await client.get("/api/v1/schedules", params={"date": target_date})
        
        if not schedules_response.json():
            pytest.skip("No slots available")
            
        # Create booking
        slot = next(
            (s for s in schedules_response.json() if s["available_spots"] > 0),
            None
        )
        
        if not slot:
            pytest.skip("No available slots found")
            
        await client.post("/api/v1/bookings", json={
            "schedule_id": slot["id"],
            "customer_name": "Test User for Retrieval",
            "customer_phone": test_phone
        })
        
        # Now retrieve bookings by phone
        response = await client.get("/api/v1/bookings", params={"phone": test_phone})
        
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Verify privacy protection (masked phone number)
        booking = data[0]
        assert "customer_phone_masked" in booking
        assert booking["customer_phone_masked"] != test_phone  # Should be masked
        
        print(f"✓ Retrieved {len(data)} bookings with privacy-protected phone numbers")


    @pytest.mark.asyncio
    async def test_booking_conflict_detection(self, client):
        """P4-05: Verify duplicate booking prevention."""
        import random
        test_phone = f"{TEST_PHONE_BASE}{random.randint(100, 999)}"
        
        target_date = (date.today() + timedelta(days=1)).isoformat()
        schedules_response = await client.get("/api/v1/schedules", params={"date": target_date})
        
        if not schedules_response.json():
            pytest.skip("No slots available")
            
        slot = next(
            (s for s in schedules_response.json() if s["available_spots"] > 0),
            None
        )
        
        if not slot:
            pytest.skip("No available slots found")
            
        # First booking should succeed
        await client.post("/api/v1/bookings", json={
            "schedule_id": slot["id"],
            "customer_name": "Conflict Test User",
            "customer_phone": test_phone
        })
        
        # Second booking for same slot + phone should fail with 409 CONFLICT
        response = await client.post("/api/v1/bookings", json={
            "schedule_id": slot["id"],
            "customer_name": "Conflict Test User (Duplicate)",
            "customer_phone": test_phone
        })
        
        assert response.status_code == 409, f"Expected conflict error but got: {response.text}"
        
        print("✓ Conflict detection working - prevented duplicate booking")


class TestCompleteFlow:
    """End-to-end booking flow integration test."""

    @pytest.mark.asyncio
    async def test_complete_booking_journey(self, client):
        """P4-12: Simulate complete user journey from browsing to confirmation."""
        import random
        
        # Step 1: User browses instructors for tomorrow
        target_date = (date.today() + timedelta(days=1)).isoformat()
        
        response = await client.get("/api/v1/instructors", params={"date": target_date})
        assert response.status_code == 200, "Failed to load instructors"
        instructors = response.json()
        
        if not instructors:
            pytest.skip("No instructors available for complete flow test")
            
        print(f"\n🎬 Complete Flow Test:")
        print(f"   Step 1: Found {len(instructors)} instructors")
        
        # Step 2: User selects first instructor and views their slots
        selected_instructor = instructors[0]
        response = await client.get(
            "/api/v1/schedules",
            params={"date": target_date, "instructor_id": selected_instructor["id"]}
        )
        
        assert response.status_code == 200
        slots = response.json()
        
        print(f"   Step 2: Loaded {len(slots)} time slots for '{selected_instructor['name']}'")
        
        # Step 3: User finds available slot and books it
        available_slot = next(
            (s for s in slots if s["available_spots"] > 0),
            None
        )
        
        if not available_slot:
            pytest.skip("No available slots to complete flow")
            
        test_phone = f"{TEST_PHONE_BASE}{random.randint(100, 999)}"
        customer_name = "Complete Flow Test User"
        
        response = await client.post("/api/v1/bookings", json={
            "schedule_id": available_slot["id"],
            "customer_name": customer_name,
            "customer_phone": test_phone
        })
        
        assert response.status_code == 200, f"Booking failed: {response.text}"
        result = response.json()
        
        print(f"   Step 3: Successfully created booking #{result['booking_id']}")
        
        # Step 4: User checks their bookings
        response = await client.get("/api/v1/bookings", params={"phone": test_phone})
        assert response.status_code == 200
        
        user_bookings = response.json()
        assert len(user_bookings) >= 1, "Booking should appear in user's list"
        
        print(f"   Step 4: Verified booking appears in user's history ({len(user_bookings)} total)")
        print(f"\n✅ Complete flow test PASSED!")


# Run tests with: pytest -xvs
if __name__ == "__main__":
    pytest.main([__file__, "-xvs"])
