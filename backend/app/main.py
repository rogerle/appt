"""
Appt - Yoga Studio Scheduler Application

Main FastAPI application entry point with API router mounting.
Includes security middleware and performance monitoring.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time

from db.database import engine, Base
from api.v1.instructors import router as instructors_router
from api.v1.bookings import router as bookings_router


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


# Security Middleware Import
from app.middleware.security_middleware import SecurityMiddleware
from app.core.cors_config import get_cors_middleware, validate_cors_config
class RequestTimingMiddleware:
    """
    Middleware to track API request response times.
    Helps identify slow endpoints for performance optimization.
    Targets: Average <200ms, P95 <300ms (Apple Design System)
    """
    
    async def __call__(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = (time.time() - start_time) * 1000
        
        # Log slow requests (>200ms) for performance monitoring
        if process_time > 200:
            logger.warning(
                f"Slow API request: {request.method} {request.url.path} "
                f"- Process time: {process_time:.2f}ms"
            )
        
        # Add response time header for client visibility
        response.headers["X-Response-Time"] = f"{process_time:.2f}ms"
        
        return call_next(request)


# Create FastAPI application
app = FastAPI(
    title="Appt - Yoga Studio Scheduler",
    description="Yoga studio booking and scheduling system API",
    version="0.1.0"
)

# Configure CORS with security best practices
# Validate CORS configuration before applying
cors_config = get_cors_middleware(production_mode=True)
is_valid, warning_message = validate_cors_config(
    cors_config["allow_origins"], 
    cors_config["allow_credentials"]
)

if not is_valid:
    logger.warning(f"CORS Configuration Issue: {warning_message}")
else:
    logger.info("CORS configuration validated successfully")

app.add_middleware(CORSMiddleware, **cors_config)

# Add security middleware for input validation and XSS/SQL injection protection
app.add_middleware(SecurityMiddleware, sanitize_input=True)
app.add_middleware(RequestTimingMiddleware)


# Database initialization
@app.on_event("startup")
async def startup_db_client():
    """Create database tables on application startup"""
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


@app.on_event("shutdown")
def shutdown_db_client():
    """Close database connection on application shutdown"""
    logger.info("Closing database connection")


# Exception handler for consistent error responses
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# Mount API routers
app.include_router(instructors_router, prefix="/api/v1")
app.include_router(bookings_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Welcome to Appt API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy"}
