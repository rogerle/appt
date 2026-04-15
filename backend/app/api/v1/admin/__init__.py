"""
Admin API Router - Aggregates all admin-specific routes.

All endpoints in this module require admin role authentication.
"""

from fastapi import APIRouter

from app.api.v1.admin.dashboard import router as dashboard_router
from app.api.v1.admin.instructors import router as instructors_router
from app.api.v1.admin.schedules import router as schedules_router
from app.api.v1.admin.users import router as users_router

admin_router = APIRouter(prefix="/admin", tags=["Admin"])

# Include all admin routers
admin_router.include_router(dashboard_router)
admin_router.include_router(instructors_router)
admin_router.include_router(schedules_router)
admin_router.include_router(users_router)


__all__ = ["admin_router"]
