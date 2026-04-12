"""
CORS Configuration for Appt API

Provides production-ready CORS settings with security best practices.

Usage:
    from app.core.cors_config import get_cors_middleware
    
    app.add_middleware(CORSMiddleware, **get_cors_middleware())
"""

from typing import List, Optional


def get_allowed_origins(production_mode: bool = True) -> List[str]:
    """
    Get allowed CORS origins based on environment.
    
    Args:
        production_mode: If True, use restrictive production settings.
                        If False, allow all origins (development mode).
    
    Returns:
        List of allowed origin URLs
    
    Security Notes:
        - Production: Only allow known, trusted domains
        - Development: Allow localhost and test origins for convenience
    """
    
    if production_mode:
        # Production: Restrict to specific trusted domains
        return [
            "https://your-production-domain.com",      # Main production domain
            "https://www.your-production-domain.com",  # www subdomain
            "https://admin.your-production-domain.com", # Admin portal
        ]
    else:
        # Development: Allow localhost and common test origins
        return [
            "http://localhost:3000",       # Frontend development server
            "http://localhost:5173",       # Vite dev server (default)
            "http://127.0.0.1:3000",       # Alternative localhost
            "http://127.0.0.1:5173",       # Vite on 127.0.0.1
            "https://localhost:3000",      # HTTPS localhost (if configured)
        ]


def get_cors_middleware(production_mode: bool = True,
                        allowed_origins: Optional[List[str]] = None,
                        allow_credentials: bool = True,
                        max_age: int = 600) -> dict:
    """
    Get CORS middleware configuration with security best practices.
    
    Args:
        production_mode: Use production-restrictive settings (recommended for production)
        allowed_origins: Custom list of allowed origins (overrides auto-selection)
        allow_credentials: Whether to allow cookies/auth headers in cross-origin requests
        max_age: Cache duration for preflight responses in seconds (default: 600s = 10min)
    
    Returns:
        Dictionary configuration for FastAPI CORSMiddleware
    
    Security Best Practices:
        ✅ Never use allow_origins=["*"] with credentials enabled
        ✅ Specify exact origin URLs instead of wildcards
        ✅ Limit allowed methods to only necessary ones (GET, POST, PUT, DELETE)
        ✅ Set appropriate max_age to reduce preflight overhead
        ✅ Enable credentials only if frontend actually needs cookies/auth
    
    Example Usage:
        ```python
        from fastapi.middleware.cors import CORSMiddleware
        
        app.add_middleware(
            CORSMiddleware,
            **get_cors_middleware(production_mode=True)
        )
        ```
    
    References:
        - OWASP CORS Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html
        - MDN CORS Configuration: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
    """
    
    if allowed_origins is None:
        allowed_origins = get_allowed_origins(production_mode)
    
    # Security-conscious configuration
    return {
        "allow_origins": allowed_origins,
        "allow_credentials": allow_credentials,
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Only necessary methods
        "allow_headers": [
            "Authorization",
            "Content-Type",
            "Accept",
            "X-Requested-With",
            "X-Request-ID",
        ],
        "expose_headers": [
            "X-Response-Time",  # Performance monitoring header
            "X-Total-Count",    # Pagination support
        ],
        "max_age": max_age,
    }


def validate_cors_config(allowed_origins: List[str], allow_credentials: bool) -> tuple[bool, str]:
    """
    Validate CORS configuration for security issues.
    
    Args:
        allowed_origins: List of origins to validate
        allow_credentials: Whether credentials are enabled
    
    Returns:
        Tuple of (is_valid, warning_message)
        
    Security Checks:
        - Warns if allow_origins=["*"] with credentials=True (SECURITY RISK!)
        - Warns about wildcard subdomains (*.example.com not supported by CORS spec)
        - Suggests using specific domain patterns instead
    
    Example Usage:
        from app.core.cors_config import validate_cors_config
        
        is_valid, message = validate_cors_config(allowed_origins=["*"], allow_credentials=True)
        if not is_valid:
            print(f"CORS Configuration Issue: {message}")
    """
    
    warnings = []
    
    # Critical security issue: wildcard with credentials
    if "*" in allowed_origins and allow_credentials:
        return False, "CRITICAL: Cannot use allow_origins=['*'] with credentials=True. This is a security vulnerability!"
    
    # Warn about wildcard without credentials (acceptable but less secure)
    if "*" in allowed_origins and not allow_credentials:
        warnings.append("WARNING: Using wildcard origin with credentials=False. Consider restricting to specific domains for better security.")
    
    # Check for subdomain wildcards (not standard-compliant)
    for origin in allowed_origins:
        if origin.startswith("*.") or origin.endswith(".*"):
            warnings.append(f"WARNING: Subdomain wildcards like '{origin}' are not CORS-standard. Use specific domains instead.")
    
    return len(warnings) == 0, "; ".join(warnings)


def get_production_cors_recommendations() -> dict:
    """
    Get recommended CORS configuration for production deployment.
    
    Returns comprehensive security recommendations including:
        - Allowed origins (example pattern)
        - Method restrictions
        - Header whitelist
        - Additional security headers
    
    Usage:
        from app.core.cors_config import get_production_cors_recommendations
        
        config = get_production_cors_recommendations()
        print(config['cors_settings'])
    """
    
    return {
        "recommended_origins": [
            "https://your-domain.com",
            "https://www.your-domain.com",
            "https://api.your-domain.com"  # If API is on separate subdomain
        ],
        "cors_settings": get_cors_middleware(production_mode=True),
        "security_headers": {
            "X-Content-Type-Options": "nosniff",
            "X-XSS-Protection": "1; mode=block",
            "Content-Security-Policy": "default-src 'self'; object-src 'none'",
            "X-Frame-Options": "DENY"
        },
        "additional_recommendations": [
            "Use HTTPS only for all CORS-enabled endpoints",
            "Implement proper authentication for all protected routes",
            "Enable CSRF protection if using session-based auth",
            "Monitor CORS errors in browser console and server logs",
            "Regularly audit allowed origins to remove unused domains"
        ]
    }
