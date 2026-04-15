#!/usr/bin/env python3
"""
Database Seed Script - Populate with Sample Data

Creates test data for development and demonstration:
- Sample yoga studio
- Instructor profiles with diverse specialties  
- Weekly schedule templates (next 7 days)
- Some existing bookings to demonstrate availability

Usage:
    python scripts/seed_data.py
    
Or from Docker:
    docker exec appt-backend python /app/scripts/seed_data.py
"""

import sys
from datetime import date, datetime, timedelta, time
from datetime import time as time_obj
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.core.config import settings
from app.db.database import DatabaseManager, init_db
from app.db.models.studio import Studio
from app.db.models.instructor import Instructor
from app.db.models.schedule import Schedule
from app.db.models.booking import Booking
from app.db.models.user import User
# Use string literal instead of enum
BOOKING_STATUS_CONFIRMED = 'confirmed'


def create_studio(session: Session) -> Studio:
    """Create sample yoga studio."""
    
    # Check if already exists
    existing = session.query(Studio).filter_by(name="Appt 阳光瑜伽馆").first()
    if existing:
        print(f"✓ Studio 'Appt 阳光瑜伽馆' already exists (id={existing.id})")
        return existing
    
    studio = Studio(
        name="Appt 阳光瑜伽馆",
        phone="13800138000",
        address="北京市朝阳区瑜伽大道 88 号"
    )
    
    session.add(studio)
    session.commit()
    session.refresh(studio)
    
    print(f"✓ Created studio: {studio.name} (id={studio.id})")
    return studio


def create_instructors(session: Session, studio_id: int) -> list[Instructor]:
    """Create sample instructor profiles."""
    
    instructors_data = [
        {
            "name": "张伟",
            "bio": "资深流瑜伽教练，拥有 8 年教学经验。RYT500 认证，擅长帮助学员提升体式和呼吸控制。",
            "specialties": ["流瑜伽", "阿斯汤加", "高级体式"],
            "avatar_url": None,
        },
        {
            "name": "李娜", 
            "bio": "阴瑜伽专家，6 年教学经验。注重冥想和身心平衡，帮助学员缓解压力和改善睡眠。",
            "specialties": ["阴瑜伽", "冥想", "修复瑜伽"],
            "avatar_url": None,
        },
        {
            "name": "王强",
            "bio": "空中瑜伽创始人，10 年教学经验。独创的空中拉伸技法深受学员喜爱。",
            "specialties": ["空中瑜伽", "力量训练", "核心强化"],
            "avatar_url": None,
        },
    ]
    
    created = []
    for instr_data in instructors_data:
        # Check if already exists
        existing = session.query(Instructor).filter_by(
            name=instr_data["name"], 
            studio_id=studio_id
        ).first()
        
        if existing:
            print(f"✓ Instructor '{instr_data['name']}' already exists (id={existing.id})")
            created.append(existing)
            continue
        
        instructor = Instructor(
            name=instr_data["name"],
            description=instr_data["bio"],  # Model field is 'description' not 'bio'
            studio_id=studio_id,
            is_active=True,
            avatar_url=instr_data.get("avatar_url")
        )
        
        session.add(instructor)
        created.append(instructor)
        print(f"✓ Created instructor: {instructor.name} (id={instructor.id})")
    
    session.commit()
    return created


def create_schedules(session: Session, instructors: list[Instructor]) -> int:
    """Create weekly schedule for all instructors (next 7 days)."""
    
    time_slots = [
        ((8, 0), (9, 0), 60),      # Morning flow
        ((10, 0), (11, 0), 60),    # Late morning
        ((14, 0), (15, 30), 90),   # Afternoon intensive
        ((16, 0), (17, 0), 60),    # Evening prep
        ((19, 0), (20, 30), 90),   # Prime time class
    ]
    
    created_count = 0
    
    for instructor in instructors:
        for day_offset in range(7):  # Next 7 days
            schedule_date = date.today() + timedelta(days=day_offset)
            
            # Skip weekends for some instructors (realistic scheduling)
            if schedule_date.weekday() >= 5 and instructor.id in [1, 3]:
                continue
            
            for start_time_tuple, end_time_tuple, duration in time_slots:
                start_time = time_obj(*start_time_tuple)
                end_time = time_obj(*end_time_tuple)
                
                # Check if already exists
                existing = session.query(Schedule).filter_by(
                    instructor_id=instructor.id,
                    schedule_date=schedule_date,
                    start_time=start_time
                ).first()
                
                if existing:
                    continue
                
                # Calculate max bookings based on duration
                max_bookings = 12 if duration >= 90 else 8
                
                schedule = Schedule(
                    instructor_id=instructor.id,
                    schedule_date=schedule_date,
                    start_time=start_time,
                    end_time=end_time,
                    max_bookings=max_bookings
                )
                
                session.add(schedule)
                created_count += 1
    
    session.commit()
    print(f"✓ Created {created_count} new schedule slots for next 7 days")
    return created_count


def create_sample_bookings(session: Session, schedules: list[Schedule]) -> int:
    """Create some sample bookings to demonstrate availability."""
    
    # Book some slots to show reduced availability
    booking_data = [
        {"customer_name": "刘小红", "customer_phone": "13900139001", "note": "第一次练习，请多关照"},
        {"customer_name": "陈小明", "customer_phone": "13900139002", "note": None},
        {"customer_name": "赵美丽", "customer_phone": "13900139003", "note": "有腰伤，需要注意"},
    ]
    
    created_count = 0
    
    # Book first 3 schedules with sample data
    for i, schedule in enumerate(schedules[:min(3, len(schedules))]):
        if i >= len(booking_data):
            break
            
        booking_info = booking_data[i]
        
        # Create booking
        booking = Booking(
            schedule_id=schedule.id,
            customer_name=booking_info["customer_name"],
            customer_phone=booking_info["customer_phone"],
            status=BOOKING_STATUS_CONFIRMED,
            notes=booking_info.get("note")  # Field is 'notes' not 'note'
        )
        
        session.add(booking)
        created_count += 1
    
    session.commit()
    print(f"✓ Created {created_count} sample bookings")
    return created_count


def create_admin_user(session: Session) -> User:
    """Create initial admin user if not exists."""
    
    # Check if admin already exists
    existing_admin = session.query(User).filter(
        (User.email == "admin@appt.local") |
        (User.username == "admin")
    ).first()
    
    if existing_admin:
        print(f"✓ Admin user already exists: {existing_admin.username}")
        return existing_admin
    
    # Get admin password from environment variable or use default
    admin_password = getattr(settings, 'ADMIN_PASSWORD', 'admin123456')
    
    # Create new admin with hashed password
    admin = User(
        email="admin@appt.local",
        username="admin",
        hashed_password=hash_password(admin_password),
        role="admin",
        is_active=True
    )
    
    session.add(admin)
    session.commit()
    session.refresh(admin)
    
    print(f"✓ Created admin user: {admin.username}")
    print(f"  Email: admin@appt.local")
    print(f"  Password: {admin_password}")
    print(f"  Role: {admin.role}")
    return admin


def main():
    """Main seed function."""
    
    print("=" * 60)
    print("🌱 Appt Database Seed Script")
    print("=" * 60)
    print()
    
    # Initialize database
    from app.db.database import db_manager as global_db_manager
    global_db_manager.connect()
    
    print("✓ Connected to database")
    print()
    
    # Create session (use SessionLocal directly since get_session is a generator)
    session = global_db_manager.SessionLocal()
    try:
        # Step 1: Create studio
        print("📍 Step 1/5: Creating yoga studio...")
        studio = create_studio(session)
        print()
        
        # Step 2: Create instructors  
        print("👨‍🏫 Step 2/5: Creating instructor profiles...")
        instructors = create_instructors(session, studio.id)
        print(f"   Total instructors: {len(instructors)}")
        print()
        
        # Step 3: Create schedules
        print("📅 Step 3/5: Creating weekly schedules...")
        existing_schedules = session.query(Schedule).all()
        new_schedules_count = create_schedules(session, instructors)
        all_schedules = session.query(Schedule).all()
        total_schedules = len(all_schedules)
        print(f"   Total schedule slots now: {total_schedules}")
        print()
        
        # Step 4: Create admin user
        print("🔐 Step 4/6: Creating admin user...")
        create_admin_user(session)
        total_users = session.query(User).count()
        print(f"   Total users: {total_users}")
        print()
        
        # Step 5: Create sample bookings
        print("📝 Step 5/6: Creating sample bookings...")
        create_sample_bookings(session, all_schedules)
        print()
        
        # Step 6: Summary statistics
        print("📊 Step 6/6: Database Statistics")
        print("-" * 40)
        print(f"   Studios:        {session.query(Studio).count()}")
        print(f"   Instructors:    {session.query(Instructor).count()}")
        print(f"   Schedules:      {session.query(Schedule).count()}")
        print(f"   Bookings:       {session.query(Booking).count()}")
        print(f"   Users:          {total_users}")
        print("-" * 40)
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Error during seeding: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        session.close()
    
    print()
    print("=" * 60)
    print("✅ Database seeding completed successfully!")
    print("=" * 60)
    print()
    print("📝 Next steps:")
    print("   1. Visit http://localhost:8080 to see the app")
    print("   2. Click '立即预约' to start booking flow")
    print("   3. You should now see real instructors and time slots!")
    print()


if __name__ == "__main__":
    main()
