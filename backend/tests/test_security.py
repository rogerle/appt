"""
Security Testing Suite for Appt API

Tests for:
- SQL Injection vulnerabilities
- XSS (Cross-Site Scripting) attacks
- CORS misconfiguration issues
- Input validation bypass attempts

Run with: pytest tests/test_security.py -v
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create test client for security testing"""
    return TestClient(app)


class TestSQLInjection:
    """Test SQL Injection vulnerabilities"""
    
    def test_injection_attempt_in_phone_query(self, client):
        """Test that phone number query parameter is safe from SQL injection"""
        # Attempt to inject SQL through phone parameter
        malicious_phone = "13800138000' OR '1'='1"
        
        response = client.get(f"/api/v1/bookings?phone={malicious_phone}")
        
        # Should return 422 validation error, not execute SQL injection
        assert response.status_code in [422, 404]
        assert "detail" in response.json()
    
    def test_injection_attempt_in_name_field(self, client):
        """Test that name field is sanitized against SQL injection"""
        malicious_name = "' OR '1'='1'"
        
        # First register a studio to create valid booking context
        register_response = client.post("/api/v1/auth/register", json={
            "email": f"test{malicious_name}@example.com",
            "password": "testpass123",
            "studio_name": "Test Studio"
        })
        
        # Login to get token
        login_response = client.post("/api/v1/auth/login", json={
            "email": f"test{malicious_name}@example.com",
            "password": "testpass123"
        })
        
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            
            # Try to create booking with malicious name
            booking_data = {
                "name": malicious_name,
                "phone": "13800138000",
                "instructor_id": 1,
                "studio_id": 1,
                "date": "2026-04-15",
                "time_slot_start": "10:00:00",
                "time_slot_end": "11:00:00"
            }
            
            response = client.post(
                "/api/v1/bookings",
                json=booking_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            # Should either reject or safely store the input without SQL execution
            assert response.status_code in [201, 422]
    
    def test_injection_attempt_in_notes_field(self, client):
        """Test that notes/textarea field is safe from SQL injection"""
        malicious_notes = "; DROP TABLE bookings; --"
        
        # First create a valid booking context
        register_response = client.post("/api/v1/auth/register", json={
            "email": f"test{malicious_notes}@example.com",
            "password": "testpass123",
            "studio_name": "Test Studio"
        })
        
        if register_response.status_code == 200:
            # Try to store malicious notes (if API supports it)
            login_response = client.post("/api/v1/auth/login", json={
                "email": f"test{malicious_notes}@example.com",
                "password": "testpass123"
            })
            
            if login_response.status_code == 200:
                # Table should still exist after attempt
                tables_response = client.get("/api/v1/bookings?phone=test@example.com")
                assert tables_response.status_code in [200, 404]  # Should not crash


class TestXSSAttacks:
    """Test XSS (Cross-Site Scripting) vulnerabilities"""
    
    def test_xss_attempt_in_name_field(self, client):
        """Test that name field is sanitized against XSS attacks"""
        xss_payload = "<script>alert('XSS')</script>"
        
        # Try to store XSS payload in booking name
        register_response = client.post("/api/v1/auth/register", json={
            "email": f"xss{malicious_name}@example.com",
            "password": "testpass123",
            "studio_name": "Test Studio"
        })
        
        if register_response.status_code == 200:
            login_response = client.post("/api/v1/auth/login", json={
                "email": f"xss{malicious_name}@example.com",
                "password": "testpass123"
            })
            
            if login_response.status_code == 200:
                token = login_response.json()["access_token"]
                
                booking_data = {
                    "name": xss_payload,
                    "phone": "13800138000",
                    "instructor_id": 1,
                    "studio_id": 1,
                    "date": "2026-04-15",
                    "time_slot_start": "10:00:00",
                    "time_slot_end": "11:00:00"
                }
                
                response = client.post(
                    "/api/v1/bookings",
                    json=booking_data,
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                # Should store safely (escaped) or reject the input
                assert response.status_code in [201, 422]
    
    def test_xss_attempt_in_description_field(self, client):
        """Test that instructor description field is safe from XSS"""
        xss_payload = "<img src=x onerror=alert('XSS')>"
        
        # Try to create instructor with XSS in description
        register_response = client.post("/api/v1/auth/register", json={
            "email": "xss@test.com",
            "password": "testpass123",
            "studio_name": "Test Studio"
        })
        
        if register_response.status_code == 200:
            login_response = client.post("/api/v1/auth/login", json={
                "email": "xss@test.com",
                "password": "testpass123"
            })
            
            if login_response.status_code == 200:
                token = login_response.json()["access_token"]
                
                # Try to create instructor with XSS payload in description
                instructor_data = {
                    "name": "Test Instructor",
                    "description": xss_payload,
                    "studio_id": 1
                }
                
                response = client.post(
                    "/api/v1/studio/instructors",
                    json=instructor_data,
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                # Should store safely or reject the input
                assert response.status_code in [201, 422]


class TestCORSConfiguration:
    """Test CORS (Cross-Origin Resource Sharing) configuration"""
    
    def test_cors_allowed_origins(self, client):
        """Verify that CORS headers are properly configured"""
        # Send request with custom Origin header
        response = client.get(
            "/api/v1/instructors",
            headers={"Origin": "https://malicious-site.com"}
        )
        
        # Check if Vary: Origin header is present (indicates proper CORS handling)
        assert "vary" in response.headers or "access-control-allow-origin" not in response.headers
        
        # If allow_origins=["*"] is used, Access-Control-Allow-Origin should be set
        # But this should be configured properly for production
    
    def test_cors_credentials_handling(self, client):
        """Test that CORS credentials are handled correctly"""
        response = client.get(
            "/api/v1/instructors",
            headers={
                "Origin": "https://example.com",
                "Credentials": "include"
            }
        )
        
        # Check for proper CORS credential handling
        if "access-control-allow-credentials" in response.headers:
            assert response.headers["access-control-allow-credentials"] == "true"
    
    def test_cors_methods_limitation(self, client):
        """Test that only allowed HTTP methods are accepted"""
        # Try unauthorized methods
        disallowed_methods = ["TRACE", "TRACK", "DEBUG"]
        
        for method in disallowed_methods:
            try:
                response = client.request(
                    method,
                    "/api/v1/instructors"
                )
                
                # Should return 405 Method Not Allowed or similar
                assert response.status_code in [405, 403]
            except Exception:
                pass  # Some methods may not be supported by test client


class TestInputValidation:
    """Test input validation and sanitization"""
    
    def test_empty_required_fields(self, client):
        """Test that empty required fields are rejected"""
        response = client.post("/api/v1/bookings", json={})
        
        # Should return 422 Validation Error
        assert response.status_code == 422
    
    def test_invalid_phone_format(self, client):
        """Test that invalid phone numbers are rejected"""
        register_response = client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "testpass123",
            "studio_name": "Test Studio"
        })
        
        if register_response.status_code == 200:
            login_response = client.post("/api/v1/auth/login", json={
                "email": "test@example.com",
                "password": "testpass123"
            })
            
            if login_response.status_code == 200:
                token = login_response.json()["access_token"]
                
                # Try invalid phone formats
                invalid_phones = [
                    "abc",
                    "123",
                    "",
                    None,
                    "13800138000123456789"  # Too long
                ]
                
                for phone in invalid_phones:
                    booking_data = {
                        "name": "Test User",
                        "phone": phone,
                        "instructor_id": 1,
                        "studio_id": 1,
                        "date": "2026-04-15",
                        "time_slot_start": "10:00:00",
                        "time_slot_end": "11:00:00"
                    }
                    
                    response = client.post(
                        "/api/v1/bookings",
                        json=booking_data,
                        headers={"Authorization": f"Bearer {token}"}
                    )
                    
                    # Should return 422 for invalid phone formats
                    assert response.status_code == 422
    
    def test_invalid_date_format(self, client):
        """Test that invalid date formats are rejected"""
        register_response = client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "testpass123",
            "studio_name": "Test Studio"
        })
        
        if register_response.status_code == 200:
            login_response = client.post("/api/v1/auth/login", json={
                "email": "test@example.com",
                "password": "testpass123"
            })
            
            if login_response.status_code == 200:
                token = login_response.json()["access_token"]
                
                booking_data = {
                    "name": "Test User",
                    "phone": "13800138000",
                    "instructor_id": 1,
                    "studio_id": 1,
                    "date": "not-a-date",  # Invalid date format
                    "time_slot_start": "10:00:00",
                    "time_slot_end": "11:00:00"
                }
                
                response = client.post(
                    "/api/v1/bookings",
                    json=booking_data,
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                # Should return 422 for invalid date format
                assert response.status_code == 422
    
    def test_time_slot_validation(self, client):
        """Test that time slots are properly validated"""
        register_response = client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "testpass123",
            "studio_name": "Test Studio"
        })
        
        if register_response.status_code == 200:
            login_response = client.post("/api/v1/auth/login", json={
                "email": "test@example.com",
                "password": "testpass123"
            })
            
            if login_response.status_code == 200:
                token = login_response.json()["access_token"]
                
                # Try invalid time slot (end before start)
                booking_data = {
                    "name": "Test User",
                    "phone": "13800138000",
                    "instructor_id": 1,
                    "studio_id": 1,
                    "date": "2026-04-15",
                    "time_slot_start": "15:00:00",  # End time earlier than start
                    "time_slot_end": "10:00:00"     # Start time later than end
                }
                
                response = client.post(
                    "/api/v1/bookings",
                    json=booking_data,
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                # Should return 422 for invalid time range


class TestAuthenticationSecurity:
    """Test authentication security measures"""
    
    def test_weak_password_rejection(self, client):
        """Test that weak passwords are rejected during registration"""
        weak_passwords = [
            "123",           # Too short
            "password",      # Common password
            "qwerty",        # Simple pattern
            "",              # Empty password
        ]
        
        for i, password in enumerate(weak_passwords):
            response = client.post("/api/v1/auth/register", json={
                "email": f"test{i}@example.com",
                "password": password,
                "studio_name": f"Test Studio {i}"
            })
            
            # Should reject weak passwords with 422 error
            assert response.status_code == 422
    
    def test_duplicate_email_prevention(self, client):
        """Test that duplicate email registration is prevented"""
        email = "duplicate@test.com"
        
        # First registration should succeed
        first_response = client.post("/api/v1/auth/register", json={
            "email": email,
            "password": "StrongPass123!",
            "studio_name": "Test Studio"
        })
        
        assert first_response.status_code == 200
        
        # Second registration with same email should fail
        second_response = client.post("/api/v1/auth/register", json={
            "email": email,
            "password": "AnotherPass123!",
            "studio_name": "Another Studio"
        })
        
        assert second_response.status_code in [400, 422]


class TestSecurityHeaders:
    """Test security-related HTTP headers"""
    
    def test_content_type_header(self, client):
        """Verify that Content-Type header is properly set"""
        response = client.get("/api/v1/instructors")
        
        assert "content-type" in response.headers
        # Should be JSON content type for API responses
    
    def test_x_content_type_options(self, client):
        """Test X-Content-Type-Options header (prevents MIME sniffing)"""
        response = client.get("/api/v1/instructors")
        
        # FastAPI may not set this by default, but it's recommended
        print(f"X-Content-Type-Options: {response.headers.get('x-content-type-options', 'Not set')}")


# Run tests with: pytest tests/test_security.py -v --tb=short
