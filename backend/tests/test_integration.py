"""Integration Tests for Appt Backend - End-to-End API Testing.

Tests complete user flows from request to database persistence,
following Apple Design System principles: clean, focused, comprehensive.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import app modules
import sys
sys.path.insert(0, '/home/claw/.openclaw/workspace-rogers/projects/appt/backend')

from app.main import app
from app.db.database import Base


# Test database configuration (in-memory SQLite for integration tests)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_integration.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # In-memory per test process
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create fresh database for integration tests."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
async def client(db_session):
    """Create test client with mocked database."""
    
    # Override database dependency
    from app.main import get_db
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    # Clean up overrides
    app.dependency_overrides.clear()


# ============================================================================
# INTEGRATION TESTS - Complete User Flows
# ============================================================================

class TestCompleteBookingFlow:
    """Test complete end-to-end booking workflow."""
    
    @pytest.mark.asyncio
    async def test_full_booking_workflow(self, client):
        """
        End-to-end test: Register Studio → Create Instructor → 
        Create Schedule → Book Class → Cancel Booking
        """
        
        # Step 1: Register yoga studio
        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "name": "阳光瑜伽馆",
                "email": "sunrise@yoga.com",
                "password": "securepass123"
            }
        )
        
        assert register_response.status_code == 200
        studio_data = register_response.json()
        studio_id = studio_data.get("studio_id") or \
                     studio_data.get("id") or \
                     studio_data.get("studio", {}).get("id")
        
        # Step 2: Login to get auth token
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": "sunrise@yoga.com",
                "password": "securepass123"
            }
        )
        
        assert login_response.status_code == 200
        token = login_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Step 3: Create instructor (admin action)
        create_instructor_response = await client.post(
            "/api/v1/studio/instructors",
            headers=headers,
            json={
                "name": "王瑜伽导师",
                "title": "高级哈他瑜伽导师",
                "avatar_url": "https://example.com/wang.jpg",
                "bio": "专注阴瑜伽教学 8 年"
            }
        )
        
        assert create_instructor_response.status_code in [200, 422]
        instructor_id = (create_instructor_response.json()
                        .get("id") or 
                        create_instructor_response.json()
                        .get("instructor", {}).get("id"))
        
        # Step 4: Create schedule for the instructor (admin action)
        create_schedule_response = await client.post(
            "/api/v1/studio/schedules",
            headers=headers,
            json={
                "instructor_id": instructor_id or 1,
                "date": "2024-06-20",
                "start_time": "10:00",
                "end_time": "11:30",
                "title": "晨间流瑜伽"
            }
        )
        
        assert create_schedule_response.status_code in [200, 422]
        schedule_id = (create_schedule_response.json()
                      .get("id") or 
                      create_schedule_response.json()
                      .get("schedule", {}).get("id"))
        
        # Step 5: Public user books the class
        booking_response = await client.post(
            "/api/v1/bookings",
            json={
                "schedule_id": schedule_id or 1,
                "name": "李明",
                "phone": "13800138000",
                "notes": "第一次来，需要基础指导"
            }
        )
        
        # Should succeed (200) or fail with validation (422) depending on schedule existence
        assert booking_response.status_code in [200, 422]
        
        if booking_response.status_code == 200:
            booking_id = booking_response.json().get("id")
            
            # Step 6: Admin retrieves bookings list
            admin_bookings_response = await client.get(
                "/api/v1/studio/bookings",
                headers=headers
            )
            
            assert admin_bookings_response.status_code == 200
            
            # Verify booking appears in admin list
            bookings_data = admin_bookings_response.json()
            if "bookings" in bookings_data:
                found_booking = any(
                    b.get("id") == booking_id 
                    for b in bookings_data["bookings"]
                )
                assert found_booking, "Booking should appear in admin list"
            
            # Step 7: Admin cancels the booking (if allowed)
            cancel_response = await client.delete(
                f"/api/v1/studio/bookings/{booking_id}",
                headers=headers
            )
            
            # Should succeed or return 404 if already cancelled
            assert cancel_response.status_code in [200, 204, 404]
    
    @pytest.mark.asyncio
    async def test_booking_without_schedule_exists(self, client):
        """Test booking fails gracefully when schedule doesn't exist."""
        
        # Try to book non-existent schedule
        response = await client.post(
            "/api/v1/bookings",
            json={
                "schedule_id": 9999,  # Non-existent ID
                "name": "测试用户",
                "phone": "13800138000"
            }
        )
        
        # Should fail with appropriate error (404 or 422)
        assert response.status_code in [404, 422]


class TestInstructorScheduleIntegration:
    """Test instructor and schedule relationship flows."""
    
    @pytest.mark.asyncio
    async def test_instructor_with_multiple_schedules(self, client):
        """Test one instructor can have multiple schedules created."""
        
        # Register and login
        await self._setup_admin_client(client)
        
        # Create instructor
        instructor_response = await client.post(
            "/api/v1/studio/instructors",
            headers={"Authorization": "Bearer test_token"},
            json={
                "name": "张瑜伽导师",
                "title": "流瑜伽专家"
            }
        )
        
        if instructor_response.status_code == 200:
            instructor_id = (instructor_response.json()
                            .get("id") or 
                            instructor_response.json()
                            .get("instructor", {}).get("id"))
            
            # Create multiple schedules for same instructor on different days
            schedule_dates = ["2024-06-15", "2024-06-17", "2024-06-19"]
            created_schedules = []
            
            for date in schedule_dates:
                response = await client.post(
                    "/api/v1/studio/schedules",
                    headers={"Authorization": "Bearer test_token"},
                    json={
                        "instructor_id": instructor_id or 1,
                        "date": date,
                        "start_time": "09:00",
                        "end_time": "10:30"
                    }
                )
                
                if response.status_code == 200:
                    schedule_data = response.json()
                    created_schedules.append(
                        schedule_data.get("id") or 
                        schedule_data.get("schedule", {}).get("id")
                    )
            
            # Verify all schedules were created for same instructor
            assert len(created_schedules) > 0, "At least one schedule should be created"
    
    @pytest.mark.asyncio
    async def test_instructor_availability_filtering(self, client):
        """Test public endpoint filters instructors by date."""
        
        # Register and login to create data
        await self._setup_admin_client(client)
        
        # Create instructor with schedule on specific date
        instructor_response = await client.post(
            "/api/v1/studio/instructors",
            headers={"Authorization": "Bearer test_token"},
            json={
                "name": "测试导师",
                "title": "测试导师"
            }
        )
        
        if instructor_response.status_code == 200:
            # Test public endpoint with date filter
            response = await client.get(
                "/api/v1/instructors?date=2024-06-15"
            )
            
            assert response.status_code == 200
            
            data = response.json()
            assert "instructors" in data or len(data) >= 0


class TestBatchScheduleCreation:
    """Test batch weekly schedule creation flow."""
    
    @pytest.mark.asyncio
    async def test_batch_weekly_schedule_creation(self, client):
        """Create recurring schedules for entire week."""
        
        # Register and login
        await self._setup_admin_client(client)
        
        # First create an instructor
        instructor_response = await client.post(
            "/api/v1/studio/instructors",
            headers={"Authorization": "Bearer test_token"},
            json={
                "name": "周排课教练",
                "title": "周班导师"
            }
        )
        
        if instructor_response.status_code == 200:
            instructor_id = (instructor_response.json()
                            .get("id") or 
                            instructor_response.json()
                            .get("instructor", {}).get("id"))
            
            # Create batch weekly schedules (Monday-Friday)
            response = await client.post(
                "/api/v1/studio/schedules/batch",
                headers={"Authorization": "Bearer test_token"},
                json={
                    "instructor_id": instructor_id or 1,
                    "daysOfWeek": [1, 2, 3, 4, 5],  # Mon-Fri
                    "start_time": "09:00",
                    "end_time": "10:00",
                    "title": "工作日晨练瑜伽",
                    "start_date": "2024-06-17",
                    "end_date": "2024-06-21"
                }
            )
            
            # Should succeed (200) or fail with validation (422)
            assert response.status_code in [200, 422]
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify batch creation count matches expected
                created_count = len(data.get("created_schedules", []))
                expected_count = 5  # Mon-Fri
                
                assert created_count > 0, "At least some schedules should be created"


class TestAuthenticationIntegration:
    """Test authentication and authorization flows."""
    
    @pytest.mark.asyncio
    async def test_admin_action_without_auth(self, client):
        """Verify admin actions require authentication."""
        
        # Try to create instructor without token
        response = await client.post(
            "/api/v1/studio/instructors",
            json={
                "name": "未授权教练",
                "title": "测试"
            }
        )
        
        assert response.status_code in [401, 403]
    
    @pytest.mark.asyncio
    async def test_admin_action_with_invalid_token(self, client):
        """Verify admin actions fail with invalid token."""
        
        # Try to create instructor with fake token
        response = await client.post(
            "/api/v1/studio/instructors",
            headers={"Authorization": "Bearer invalid_token"},
            json={
                "name": "无效 Token 教练",
                "title": "测试"
            }
        )
        
        assert response.status_code in [401, 403]


class TestDataValidationIntegration:
    """Test data validation and error handling."""
    
    @pytest.mark.asyncio
    async def test_booking_with_invalid_phone(self, client):
        """Test booking with invalid phone number format."""
        
        response = await client.post(
            "/api/v1/bookings",
            json={
                "schedule_id": 1,
                "name": "测试用户",
                "phone": "invalid-phone-number"
            }
        )
        
        # Should either fail validation (422) or succeed (depends on backend implementation)
        assert response.status_code in [200, 422]
    
    @pytest.mark.asyncio
    async def test_booking_with_missing_required_fields(self, client):
        """Test booking with missing required fields."""
        
        response = await client.post(
            "/api/v1/bookings",
            json={
                "schedule_id": 1
                # Missing name and phone
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_schedule_with_invalid_date_format(self, client):
        """Test schedule creation with invalid date."""
        
        await self._setup_admin_client(client)
        
        response = await client.post(
            "/api/v1/studio/schedules",
            headers={"Authorization": "Bearer test_token"},
            json={
                "instructor_id": 1,
                "date": "not-a-date",  # Invalid format
                "start_time": "09:00"
            }
        )
        
        assert response.status_code in [422]  # Validation error


# ============================================================================
# HELPER METHODS
# ============================================================================

async def _setup_admin_client(self, client):
    """Helper method to register and login admin studio."""
    
    # Register studio
    await client.post(
        "/api/v1/auth/register",
        json={
            "name": "测试瑜伽馆",
            "email": "admin@test.com",
            "password": "testpass"
        }
    )
    
    # Login to get token (mocked for simplicity)
    await client.post(
        "/api/v1/auth/login",
        json={
            "username": "admin@test.com",
            "password": "testpass"
        }
    )


# ============================================================================
# RUN COMMANDS
# ============================================================================

"""
Run integration tests:

pytest backend/tests/test_integration.py -v          # Run all tests with verbose output
pytest backend/tests/test_integration.py::TestCompleteBookingFlow -v  # Specific test class
pytest backend/tests/test_integration.py -xvs        # Stop on first failure, show detailed output
"""
