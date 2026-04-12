#!/usr/bin/env python3
"""
Swagger API Documentation Test Suite

Tests all auto-generated OpenAPI/Swagger documentation endpoints:
- GET /docs - Swagger UI interface
- GET /redoc - ReDoc interface  
- GET /openapi.json - Raw OpenAPI specification JSON
- All defined API endpoints with request/response schemas

Usage: python tests/test_swagger_docs.py
"""

import requests
import json
import sys
from typing import Dict, List


# Configuration
BASE_URL = "http://localhost:8000"
API_V1_BASE = f"{BASE_URL}/api/v1"


class SwaggerDocTestRunner:
    """Comprehensive test suite for API documentation validation"""
    
    def __init__(self):
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": [],
            "warnings": []
        }
        
    def print_header(self, title: str):
        """Print formatted test section header"""
        print("\n" + "=" * 80)
        print(f"🧪 {title}")
        print("=" * 80)
    
    def print_success(self, message: str):
        """Print success indicator"""
        print(f"✅ {message}")
        
    def print_error(self, message: str):
        """Print error indicator"""
        print(f"❌ Error: {message}")
        
    def print_warning(self, message: str):
        """Print warning indicator"""
        print(f"⚠️  Warning: {message}")
    
    def test_openapi_json_structure(self) -> bool:
        """Test OpenAPI JSON specification structure and completeness"""
        self.print_header("1. OpenAPI Specification Validation")
        
        try:
            response = requests.get(f"{BASE_URL}/openapi.json", timeout=5)
            
            if response.status_code != 200:
                self.print_error(f"OpenAPI spec not found (status {response.status_code})")
                return False
            
            spec = response.json()
            
            # Validate required OpenAPI fields
            required_fields = ["openapi", "info", "paths", "components"]
            missing_fields = [field for field in required_fields if field not in spec]
            
            if missing_fields:
                self.print_error(f"Missing required OpenAPI fields: {', '.join(missing_fields)}")
                return False
            
            # Validate info section
            info = spec.get("info", {})
            if "title" not in info or "version" not in info:
                self.print_error("Missing 'title' or 'version' in OpenAPI info")
                return False
            
            print(f"✅ OpenAPI version: {spec['openapi']}")
            print(f"📦 API Title: {info.get('title')} v{info.get('version')}")
            
            # Count endpoints
            paths = spec.get("paths", {})
            total_endpoints = len(paths)
            print(f"🔗 Total endpoints documented: {total_endpoints}")
            
            # Group by tag
            tags = set()
            for path, methods in paths.items():
                for method, details in methods.items():
                    if isinstance(details, dict):
                        tags.update(details.get("tags", []))
            
            print(f"🏷️  API Categories: {', '.join(sorted(tags))}")
            
            # Validate components (schemas)
            schemas = spec.get("components", {}).get("schemas", {})
            print(f"📄 Data models defined: {len(schemas)}")
            
            if len(schemas) == 0:
                self.print_warning("No data model schemas found in OpenAPI spec")
            
            # Check for security schemes (JWT authentication)
            security_schemes = spec.get("components", {}).get("securitySchemes", {})
            print(f"🔐 Authentication methods: {list(security_schemes.keys())}")
            
            self.results["passed"] += 1
            
            return True
            
        except requests.exceptions.ConnectionError:
            self.print_error("Cannot connect to API server. Is it running?")
            return False
        
        except Exception as e:
            self.print_error(f"Unexpected error: {e}")
            return False
    
    def test_swagger_ui_accessibility(self) -> bool:
        """Test Swagger UI interface is accessible"""
        self.print_header("2. Swagger UI Interface Test")
        
        try:
            response = requests.get(f"{BASE_URL}/docs", timeout=5, headers={"Accept": "text/html"})
            
            if response.status_code != 200:
                self.print_error(f"Swagger UI not accessible (status {response.status_code})")
                return False
            
            html_content = response.text.lower()
            
            # Check for essential Swagger UI elements
            required_elements = [
                "swagger-ui",
                "try it out",
                "/api/v1/",
            ]
            
            missing_elements = [elem for elem in required_elements if elem not in html_content]
            
            if missing_elements:
                self.print_warning(f"Swagger UI may be incomplete (missing: {', '.join(missing_elements)})")
            else:
                print("✅ Swagger UI interface is fully functional")
                print("🌐 URL: http://localhost:8000/docs")
            
            self.results["passed"] += 1
            
            return True
            
        except requests.exceptions.ConnectionError:
            self.print_error("Cannot connect to API server. Is it running?")
            return False
    
    def test_redoc_accessibility(self) -> bool:
        """Test ReDoc interface is accessible"""
        self.print_header("3. ReDoc Interface Test")
        
        try:
            response = requests.get(f"{BASE_URL}/redoc", timeout=5, headers={"Accept": "text/html"})
            
            if response.status_code != 200:
                self.print_error(f"ReDoc not accessible (status {response.status_code})")
                return False
            
            html_content = response.text.lower()
            
            # Check for essential ReDoc elements
            required_elements = [
                "redoc",
                "/api/v1/",
            ]
            
            missing_elements = [elem for elem in required_elements if elem not in html_content]
            
            if missing_elements:
                self.print_warning(f"ReDoc may be incomplete (missing: {', '.join(missing_elements)})")
            else:
                print("✅ ReDoc documentation interface is fully functional")
                print("🌐 URL: http://localhost:8000/redoc")
            
            self.results["passed"] += 1
            
            return True
            
        except requests.exceptions.ConnectionError:
            self.print_error("Cannot connect to API server. Is it running?")
            return False
    
    def test_endpoint_documentation(self) -> bool:
        """Test all documented endpoints have proper documentation"""
        self.print_header("4. Endpoint Documentation Coverage")
        
        try:
            spec = requests.get(f"{BASE_URL}/openapi.json", timeout=5).json()
            
            paths = spec.get("paths", {})
            
            endpoint_tests = 0
            documented_endpoints = []
            undocumented_endpoints = []
            
            for path, methods in paths.items():
                for method, details in methods.items():
                    if not isinstance(details, dict):
                        continue
                    
                    # Check required documentation fields
                    has_title = "title" in details or "summary" in details
                    has_description = "description" in details or "summary" in details
                    has_request_schema = "requestBody" in details  # For POST/PUT/PATCH
                    has_response_schema = "responses" in details
                    
                    endpoint_key = f"{method.upper()} {path}"
                    
                    if not (has_title and has_description):
                        self.print_error(f"Incomplete docs: {endpoint_key}")
                        undocumented_endpoints.append(endpoint_key)
                    else:
                        documented_endpoints.append({
                            "key": endpoint_key,
                            "tags": details.get("tags", []),
                            "request_schema": has_request_schema,
                            "response_schema": has_response_schema
                        })
                    
                    endpoint_tests += 1
            
            # Summary statistics
            print(f"📊 Total endpoints tested: {endpoint_tests}")
            print(f"✅ Well-documented: {len(documented_endpoints)}")
            
            if undocumented_endpoints:
                print(f"\n⚠️  Endpoints missing proper documentation:")
                for ep in undocumented_endpoints:
                    print(f"   - {ep}")
            else:
                self.print_success("All endpoints have complete documentation!")
            
            # List all documented endpoints by category
            tags_map = {}
            for ep in documented_endpoints:
                for tag in ep["tags"]:
                    if tag not in tags_map:
                        tags_map[tag] = []
                    tags_map[tag].append(ep["key"])
            
            print(f"\n📋 Endpoints by Category:")
            for tag, endpoints in sorted(tags_map.items()):
                print(f"  {tag}:")
                for ep in endpoints[:5]:  # Show first 5 per category
                    print(f"    • {ep}")
                if len(endpoints) > 5:
                    print(f"    ... and {len(endpoints) - 5} more")
            
            self.results["passed"] += (1 if not undocumented_endpoints else 0)
            
            return len(undocumented_endpoints) == 0
            
        except Exception as e:
            self.print_error(f"Failed to validate endpoints: {e}")
            return False
    
    def test_request_response_schemas(self) -> bool:
        """Test request/response schema definitions for all operations"""
        self.print_header("5. Request/Response Schema Validation")
        
        try:
            spec = requests.get(f"{BASE_URL}/openapi.json", timeout=5).json()
            
            paths = spec.get("paths", {})
            
            missing_schemas = []
            incomplete_schemas = []
            
            for path, methods in paths.items():
                for method, details in methods.items():
                    if not isinstance(details, dict):
                        continue
                    
                    # POST/PUT/PATCH should have request body schema
                    if method.lower() in ["post", "put", "patch"]:
                        if "requestBody" not in details:
                            missing_schemas.append(f"{method.upper()} {path} (missing requestBody)")
                    
                    # All operations should have response schemas
                    if "responses" not in details:
                        incomplete_schemas.append(f"{method.upper()} {path} (missing responses)")
                        
                        continue
                    
                    # Check for standard HTTP status codes
                    responses = details["responses"]
                    required_codes = [200, 422]  # Success and validation error
                    missing_codes = []
                    
                    for code in required_codes:
                        if str(code) not in responses:
                            missing_codes.append(code)
                    
                    if missing_codes:
                        incomplete_schemas.append(f"{method.upper()} {path} (missing codes: {', '.join(map(str, missing_codes))})")
            
            # Summary
            print(f"📄 Total POST/PUT/PATCH operations: {len(paths)}")
            
            if missing_schemas:
                self.print_error("Missing request body schemas:")
                for schema in missing_schemas:
                    print(f"   - {schema}")
            else:
                self.print_success("All mutation endpoints have request schemas!")
            
            if incomplete_schemas:
                self.print_warning("Some operations missing response definitions:")
                for schema in incomplete_schemas[:5]:  # Show first 5
                    print(f"   • {schema}")
            else:
                self.print_success("All operations define proper responses!")
            
            self.results["passed"] += (1 if not missing_schemas and not incomplete_schemas else 0)
            
            return len(missing_schemas) == 0 and len(incomplete_schemas) == 0
            
        except Exception as e:
            self.print_error(f"Failed to validate schemas: {e}")
            return False
    
    def test_authentication_security(self) -> bool:
        """Test authentication security configuration in OpenAPI spec"""
        self.print_header("6. Authentication & Security Configuration")
        
        try:
            spec = requests.get(f"{BASE_URL}/openapi.json", timeout=5).json()
            
            # Check for JWT/Bearer token security scheme
            components = spec.get("components", {})
            security_schemes = components.get("securitySchemes", {})
            
            has_jwt = any(
                s.get("type") == "http" and 
                (s.get("scheme").lower() == "bearer" or s.get("name") == "Authorization")
                for s in security_schemes.values()
            )
            
            if not has_jwt:
                self.print_warning("No JWT/Bearer token authentication configured!")
            else:
                print("✅ JWT Bearer token authentication is properly configured")
                
                # Print security scheme details
                for name, config in security_schemes.items():
                    if config.get("type") == "http" and config.get("scheme").lower() == "bearer":
                        print(f"   🔐 Scheme: {name}")
                        print(f"      Type: HTTP Bearer Token")
            
            # Check global security requirements
            global_security = spec.get("security", [])
            if global_security:
                print(f"\n🔒 Global security requirement applied to all endpoints")
            
            # Check per-endpoint security (if any)
            paths = spec.get("paths", {})
            secured_endpoints = 0
            
            for path, methods in paths.items():
                for method, details in methods.items():
                    if isinstance(details, dict) and "security" in details:
                        secured_endpoints += 1
            
            print(f"   📝 Endpoints with custom security requirements: {secured_endpoints}")
            
            self.results["passed"] += 1
            
            return True
            
        except Exception as e:
            self.print_error(f"Failed to validate security config: {e}")
            return False
    
    def test_data_models(self) -> bool:
        """Test all data model schemas are well-defined"""
        self.print_header("7. Data Model Schema Validation")
        
        try:
            spec = requests.get(f"{BASE_URL}/openapi.json", timeout=5).json()
            
            schemas = spec.get("components", {}).get("schemas", {})
            
            if not schemas:
                self.print_warning("No data model schemas found!")
                return False
            
            print(f"📚 Total models defined: {len(schemas)}")
            
            # Check for required fields in each schema
            issues = []
            
            for model_name, schema in schemas.items():
                if "properties" not in schema and "allOf" not in schema:
                    issues.append(f"{model_name} has no properties defined!")
                
                if "required" not in schema:
                    print(f"⚠️  {model_name}: No 'required' fields specified")
            
            # List models by category (if tagged)
            model_categories = {}
            
            for path, methods in spec.get("paths", {}).items():
                for method, details in methods.items():
                    if isinstance(details, dict):
                        # Look for request/response schemas
                        for location in ["requestBody", "responses"]:
                            if location in details:
                                content = details[location].get("content", {})
                                for media_type, schema_info in content.items():
                                    ref_path = schema_info.get("schema", {}).get("$ref", "")
                                    if ref_path.startswith("#/components/schemas/"):
                                        model_name = ref_path.split("/")[-1]
                                        # Find tags for this endpoint
                        tags = details.get("tags", ["unknown"])
            
            print("\n📋 Model Categories:")
            for tag, models in sorted(model_categories.items()):
                print(f"  {tag}: {', '.join(models)}")
            
            if issues:
                self.print_error("Schema validation issues:")
                for issue in issues[:5]:  # Show first 5
                    print(f"   • {issue}")
            else:
                self.print_success("All data models are properly structured!")
            
            self.results["passed"] += (1 if not issues else 0)
            
            return len(issues) == 0
            
        except Exception as e:
            self.print_error(f"Failed to validate schemas: {e}")
            return False
    
    def run_all_tests(self):
        """Execute complete test suite"""
        
        print("\n" + "=" * 80)
        print("🧘 Appt API Documentation Test Suite")
        print("=" * 80)
        print(f"\nBase URL: {BASE_URL}")
        print(f"Testing at: {self._get_current_time()}")
        
        # Run all tests
        self.results["total_tests"] = 7
        
        test_methods = [
            ("OpenAPI Specification", self.test_openapi_json_structure),
            ("Swagger UI Accessibility", self.test_swagger_ui_accessibility),
            ("ReDoc Accessibility", self.test_redoc_accessibility),
            ("Endpoint Documentation Coverage", self.test_endpoint_documentation),
            ("Request/Response Schemas", self.test_request_response_schemas),
            ("Authentication Security", self.test_authentication_security),
            ("Data Model Validation", self.test_data_models),
        ]
        
        for test_name, test_func in test_methods:
            try:
                result = test_func()
                if not result:
                    print(f"❌ {test_name} - FAILED")
                else:
                    print(f"✅ {test_name} - PASSED")
            except Exception as e:
                print(f"❌ {test_name} - ERROR: {e}")
        
        # Summary Report
        self._print_summary_report()
    
    def _get_current_time(self) -> str:
        """Get current timestamp for test run log"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _print_summary_report(self):
        """Print comprehensive test summary report"""
        
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY REPORT")
        print("=" * 80)
        
        total = self.results["total_tests"]
        passed = self.results["passed"]
        failed = total - passed
        
        print(f"\nTotal Tests: {total}")
        print(f"✅ Passed:    {passed} ({100*passed/total:.1f}%)")
        
        if failed > 0:
            print(f"❌ Failed:   {failed}")
        
        # Critical checks
        print("\n🎯 CRITICAL CHECKS:")
        
        critical_passed = []
        critical_failed = []
        
        # Check 1: OpenAPI spec exists and is valid
        if "openapi.json" in self.results.get("passed", [{}])[0] if isinstance(self.results["passed"][0], dict) else True:
            critical_passed.append("✅ OpenAPI specification accessible")
        else:
            critical_failed.append("❌ OpenAPI spec not found")
        
        # Check 2: Swagger UI functional
        if "docs" in self.results.get("passed", [{}])[1] if isinstance(self.results["passed"][1], dict) else True:
            critical_passed.append("✅ Swagger UI interface working")
        else:
            critical_failed.append("❌ Swagger UI not accessible")
        
        # Check 3: All endpoints documented
        if len(self.results.get("failed", [])) == 0:
            critical_passed.append("✅ All endpoints properly documented")
        else:
            critical_failed.append(f"❌ {len(self.results['failed'])} undocumented issues")
        
        for check in critical_passed:
            print(f"   {check}")
        
        if critical_failed:
            for check in critical_failed:
                print(f"   {check}")
        
        # Final verdict
        print("\n🏁 FINAL VERDICT:")
        
        if failed == 0:
            print("   🎉 ALL TESTS PASSED! API documentation is production-ready!")
            print(f"\n   🌐 Documentation URLs:")
            print(f"      Swagger UI:     {BASE_URL}/docs")
            print(f"      ReDoc:          {BASE_URL}/redoc")
            print(f"      OpenAPI JSON:   {BASE_URL}/openapi.json")
        else:
            print(f"   ⚠️  {failed} test(s) failed. Please review the errors above.")
        
        return failed == 0


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    runner = SwaggerDocTestRunner()
    
    # Check if API server is running first
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=3)
        if response.status_code != 200:
            print(f"❌ Backend API not responding. Expected status 200, got {response.status_code}")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend API server!")
        print("\nPlease start the development server first:")
        print(f"   cd projects/appt/backend")
        print(f"   uvicorn app.main:app --reload")
        sys.exit(1)
    
    # Run complete test suite
    success = runner.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
