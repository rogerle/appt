"""Admin Dashboard API Endpoints - Requires admin role."""

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_current_admin_user
from app.db.database import get_db
from app.db.models.user import User
from app.db.models.instructor import Instructor
from app.db.models.schedule import Schedule
from app.db.models.booking import Booking
from app.schemas.admin import DashboardStats, RecentBookingResponse


router = APIRouter(prefix="/dashboard", tags=["Admin - Dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: Session = Depends(get_db), user: User = Depends(get_current_admin_user)):
    """Get dashboard statistics."""
    
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    days_since_monday = now.weekday()
    week_start = today_start - timedelta(days=days_since_monday)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    total_bookings_today = db.query(Booking).join(Schedule).filter(
        Schedule.schedule_date >= today_start.date(), Booking.status == "confirmed").count()
    
    total_bookings_week = db.query(Booking).join(Schedule).filter(
        Schedule.schedule_date >= week_start.date(), Booking.status == "confirmed").count()

    total_bookings_month = db.query(Booking).join(Schedule).filter(
        Schedule.schedule_date >= month_start.date(), Booking.status == "confirmed").count()

    active_instructors = db.query(Instructor).filter(Instructor.is_active == True).count()

    today_date = now.date()
    # Get future schedules (no status field in Schedule model)
    future_schedules = db.query(Schedule).filter(
        Schedule.schedule_date >= today_date).all()

    available_slots_count = 0
    for schedule in future_schedules:
        booked_count = db.query(Booking).filter(
            Booking.schedule_id == schedule.id, Booking.status == "confirmed").count()
        # Use max_bookings instead of max_participants
        if booked_count < schedule.max_bookings:
            available_slots_count += (schedule.max_bookings - booked_count)

    return DashboardStats(
        total_bookings_today=total_bookings_today, total_bookings_week=total_bookings_week,
        total_bookings_month=total_bookings_month, active_instructors=active_instructors,
        available_slots=available_slots_count, revenue_this_month=0.0)


@router.get("/recent-bookings", response_model=List[RecentBookingResponse])
async def get_recent_bookings(limit: int = 10, offset: int = 0, db: Session = Depends(get_db), user: User = Depends(get_current_admin_user)):
    """Get recent bookings."""
    
    if limit > 100:
        raise HTTPException(status_code=400, detail="Limit cannot exceed 100")

    bookings = db.query(Booking).options(joinedload(Booking.schedule).joinedload(Schedule.instructor)).order_by(desc(Booking.created_at)).offset(offset).limit(limit).all()

    result = []
    for booking in bookings:
        schedule = booking.schedule
        instructor_name = schedule.instructor.name if schedule and schedule.instructor else "Unknown"
        
        result.append(RecentBookingResponse(
            id=booking.id, customer_name=booking.customer_name, customer_phone=booking.customer_phone,
            booking_date=schedule.schedule_date if schedule else None,
            start_time=schedule.start_time if schedule else None,
            end_time=schedule.end_time if schedule else None,
            class_type=f"{instructor_name}'s Class",  # Derived from instructor
            instructor_name=instructor_name, status=booking.status,
            created_at=booking.created_at, notes=booking.notes or ""))

    return result


@router.get("/bookings-chart-data")
async def get_bookings_chart_data(days: int = 30, db: Session = Depends(get_db), user: User = Depends(get_current_admin_user)):
    """Get booking data for chart."""
    
    if days < 1 or days > 365:
        raise HTTPException(status_code=400, detail="Days must be between 1 and 365")

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days-1)

    bookings = db.query(Booking).join(Schedule).filter(
        Schedule.schedule_date >= start_date, Schedule.schedule_date <= end_date, Booking.status == "confirmed").all()

    daily_counts = {}
    for booking in bookings:
        date_str = booking.schedule.schedule_date.strftime("%Y-%m-%d")
        daily_counts[date_str] = daily_counts.get(date_str, 0) + 1

    chart_data = []
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        chart_data.append({"date": date_str, "bookings": daily_counts.get(date_str, 0)})
        current_date += timedelta(days=1)

    return {"data": chart_data}
