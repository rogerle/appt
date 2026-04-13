"""
Appt Backend - FastAPI Application Entry Point

Main application file that sets up routing, middleware, and API documentation.
"""

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.auth import router as auth_router
from app.api.v1.instructors import router as instructors_router
from app.api.v1.schedules import router as schedules_router
from app.api.v1.bookings import router as bookings_router


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management."""
    
    # Startup events
    logger.info("🚀 Appt Backend is starting...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    
    yield
    
    # Shutdown events
    logger.info("🛑 Appt Backend shutting down...")


# Create FastAPI application instance
app = FastAPI(
    title="Appt Yoga Studio Booking API",
    description="RESTful API for yoga studio class scheduling and reservations",
    version="1.0.0",
    lifespan=lifespan,
    
    # OpenAPI documentation configuration
    docs_url="/docs",           # Swagger UI
    redoc_url="/redoc",         # ReDoc documentation
    openapi_url="/openapi.json"
)

# Add CORS middleware (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS or ["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)


# Register API routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(instructors_router, prefix="/api/v1")
app.include_router(schedules_router, prefix="/api/v1")
app.include_router(bookings_router, prefix="/api/v1")


@app.get("/health", tags=["Health Check"])
async def health_check():
    """Health check endpoint for Docker/Kubernetes."""
    return {
        "status": "healthy",
        "service": "appt-backend",
        "version": "1.0.0"
    }


@app.get("/", tags=["Root"])
async def root():
    """API Root endpoint with documentation links."""
    return {
        "name": "Appt Yoga Studio Booking API",
        "version": "1.0.0",
        "docs": "/docs",      # Swagger UI
        "redoc": "/redoc"     # ReDoc documentation
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting Appt Backend...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "development" else False
    )
