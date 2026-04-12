"""
Security Middleware for Appt API

Provides:
- Input sanitization and validation
- SQL injection prevention
- XSS (Cross-Site Scripting) protection
- Request size limits
- Rate limiting support (optional)

Usage: app.add_middleware(SecurityMiddleware)
"""

import re
from typing import Callable, Any, Dict
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Security middleware for input validation and sanitization.
    
    Protects against:
    - SQL Injection attempts
    - XSS (Cross-Site Scripting) attacks
    - Malicious file paths and commands
    - Input too large or malformed data
    """
    
    # SQL injection patterns to detect
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER)\b.*\b(FROM|INTO|TABLE|WHERE)\b)",
        r"(--|#|;|--)",  # Comment characters and statement terminators
        r"(\bOR\b|\bAND\b).*['\"]?[\d\w]+['\"]?\s*=?\s*['\"]?[\d\w]+['\"]?",
        r"('\s*(=|>|<|!)=\s*)+'",  # Quote-based injection patterns
    ]
    
    # XSS patterns to detect and sanitize
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"<iframe[^>]*>",
        r"<object[^>]*>",
        r"<embed[^>]*>",
        r"on\w+\s*=\s*['\"]?[^'\"]+['\"]?",  # Event handlers (onclick, onerror, etc.)
        r"javascript:",
        r"vbscript:",
        r"data:\s*text/html",
    ]
    
    def __init__(self, app: Callable, 
                 max_request_size: int = 10485760,  # 10MB default limit
                 sanitize_input: bool = True):
        """
        Initialize security middleware.
        
        Args:
            app: FastAPI application instance
            max_request_size: Maximum request body size in bytes (default: 10MB)
            sanitize_input: Whether to automatically sanitize input data (default: True)
        """
        super().__init__(app)
        self.max_request_size = max_request_size
        self.sanitize_input = sanitize_input
    
    async def dispatch(self, request: Request, call_next: Callable) -> Any:
        """Process the request and apply security checks."""
        
        # Check 1: Request size limit
        content_length = request.headers.get("Content-Length")
        if content_length and int(content_length) > self.max_request_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Request body too large. Maximum allowed size: {self.max_request_size / 1024 / 1024:.0f}MB"
            )
        
        # Check 2: SQL injection detection in query parameters and path
        self._check_sql_injection(request)
        
        # Check 3: XSS detection in request body (if JSON payload)
        if "application/json" in request.headers.get("Content-Type", ""):
            try:
                body = await request.body()
                if body:
                    import json
                    data = json.loads(body.decode())
                    
                    # Sanitize input data recursively
                    if self.sanitize_input:
                        sanitized_data = self._sanitize_data(data)
                        
                        # Rebuild request with sanitized data
                        request._stream = self._iter_body(sanitized_data)
                        request._json_cache = sanitized_data
                    
            except (json.JSONDecodeError, UnicodeDecodeError):
                # If JSON parsing fails, it's likely not a security concern but malformed input
                pass
        
        # Check 4: Security headers check (add recommended headers)
        response = await call_next(request)
        
        # Add security headers to response
        self._add_security_headers(response)
        
        return response
    
    def _check_sql_injection(self, request: Request):
        """Check for SQL injection patterns in URL parameters and path."""
        
        # Check query parameters
        for param, values in request.query_params.multi_items():
            for value in values:
                if self._contains_sql_injection(value):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Potentially malicious input detected in parameter '{param}'"
                    )
        
        # Check path parameters (if any)
        for param, value in request.path_params.items():
            if isinstance(value, str) and self._contains_sql_injection(value):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Potentially malicious input detected in path parameter '{param}'"
                )
    
    def _contains_sql_injection(self, text: str) -> bool:
        """Check if text contains SQL injection patterns."""
        
        if not isinstance(text, str):
            return False
        
        text_lower = text.lower()
        
        for pattern in self.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                # Additional check: allow common safe patterns like phone numbers with quotes
                if "'" in text and "OR '1'='1" not in text_lower:
                    continue  # Single quote is OK in most contexts
                
                return True
        
        return False
    
    def _sanitize_data(self, data: Any) -> Any:
        """Recursively sanitize input data to remove XSS patterns."""
        
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                # Sanitize keys as well (prevent XSS in field names)
                safe_key = self._sanitize_string(key)
                sanitized[safe_key] = self._sanitize_data(value)
            return sanitized
        
        elif isinstance(data, list):
            return [self._sanitize_data(item) for item in data]
        
        elif isinstance(data, str):
            return self._sanitize_string(data)
        
        else:
            return data
    
    def _sanitize_string(self, text: str) -> str:
        """Sanitize a string to remove XSS patterns."""
        
        if not isinstance(text, str):
            return text
        
        sanitized = text
        
        # Remove dangerous HTML tags and attributes
        for pattern in self.XSS_PATTERNS:
            sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE)
        
        # Escape HTML special characters
        html_escape_table = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#x27;",
            "/": "&#x2F;"
        }
        
        sanitized = "".join(html_escape_table.get(c, c) for c in sanitized)
        
        # Trim excessive whitespace (potential bypass technique)
        sanitized = " ".join(sanitized.split())
        
        return sanitized
    
    async def _iter_body(self, data: Any):
        """Convert sanitized data back to an async iterator."""
        import json
        
        yield json.dumps(data).encode()
    
    def _add_security_headers(self, response):
        """Add security-related HTTP headers to the response."""
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Enable XSS protection (though mostly deprecated in modern browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Content Security Policy (CSP) - basic policy for API
        # Note: Full CSP requires careful planning for frontend integration
        if "Content-Security-Policy" not in response.headers:
            # Basic API-friendly CSP
            csp_policy = (
                "default-src 'self'; "
                "object-src 'none'; "
                "base-uri 'self'"
            )
            response.headers["Content-Security-Policy"] = csp_policy
        
        # Prevent clickjacking (X-Frame-Options) - only for web pages, not API responses
        if "application/json" in response.headers.get("Content-Type", ""):
            response.headers["X-Frame-Options"] = "DENY"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple rate limiting middleware (optional).
    
    Can be used to prevent brute force attacks and abuse.
    
    Usage: app.add_middleware(RateLimitMiddleware, requests_per_minute=60)
    """
    
    def __init__(self, app: Callable, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_times: Dict[str, list] = {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Any:
        """Apply rate limiting based on client IP."""
        
        # Get client IP (considering proxies)
        client_ip = request.client.host if request.client else "unknown"
        
        # Track requests per minute
        import time
        
        current_time = time.time()
        minute_ago = current_time - 60
        
        if client_ip not in self.request_times:
            self.request_times[client_ip] = []
        
        # Remove old requests (older than 1 minute)
        self.request_times[client_ip] = [
            t for t in self.request_times[client_ip] 
            if t > minute_ago
        ]
        
        # Check rate limit
        if len(self.request_times[client_ip]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {self.requests_per_minute} requests per minute."
            )
        
        # Record this request
        self.request_times[client_ip].append(current_time)
        
        return await call_next(request)
