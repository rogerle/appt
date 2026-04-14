#!/usr/bin/env python3
"""Simple SQL Seed Script - Direct database insertion."""

import os
from datetime import date, timedelta

# Database connection info from environment
DB_HOST = os.getenv('POSTGRES_HOST', 'postgres')
DB_PORT = os.getenv('POSTGRES_PORT', '5432')
DB_NAME = os.getenv('POSTGRES_DB', 'appt')
DB_USER = os.getenv('POSTGRES_USER', 'appt_user')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'change_me_in_production')

import psycopg2

def execute_sql(sql: str, params=None):
    """Execute SQL and return results."""
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT,
        database=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )
    cur = conn.cursor()
    try:
        cur.execute(sql, params)
        if sql.strip().upper().startswith('SELECT'):
            results = cur.fetchall()
        else:
            conn.commit()
            results = cur.rowcount
        return results
    finally:
        cur.close()
        conn.close()

def main():
    print("=" * 60)
    print("🌱 Simple Database Seed Script")  
    print("=" * 60)
    print()
    
    # Step 1: Create studio
    print("📍 Creating yoga studio...")
    execute_sql("""
        INSERT INTO studio (name, phone, address, description, created_at)
        VALUES (%s, %s, %s, %s, NOW())
        ON CONFLICT DO NOTHING
    """, ("Appt 阳光瑜伽馆", "13800138000", 
          "北京市朝阳区瑜伽大道 88 号", 
          "专业瑜伽馆，提供流瑜伽、阴瑜伽、空中瑜伽等多种课程"))
    print("✓ Studio created")
    
    # Get studio_id
    studio_id = execute_sql("SELECT id FROM studio WHERE name = %s", ("Appt 阳光瑜伽馆",))[0][0]
    print(f"   Studio ID: {studio_id}")
    print()
    
    # Step 2: Create instructors
    print("👨‍🏫 Creating instructors...")
    instructors = [
        ("张伟", "资深流瑜伽教练，拥有 8 年教学经验。RYT500 认证。", studio_id),
        ("李娜", "阴瑜伽专家，6 年教学经验。注重冥想和身心平衡。", studio_id),
        ("王强", "空中瑜伽创始人，10 年教学经验。独创的空中拉伸技法。", studio_id),
    ]
    
    instructor_ids = []
    for name, bio, sid in instructors:
        result = execute_sql("""
            INSERT INTO instructor (name, bio, studio_id, is_active, created_at)
            VALUES (%s, %s, %s, true, NOW())
            ON CONFLICT (name, studio_id) DO NOTHING
            RETURNING id
        """, (name, bio, sid))
        
        if result > 0:
            instr_id = execute_sql("SELECT id FROM instructor WHERE name = %s AND studio_id = %s", (name, sid))[0][0]
            instructor_ids.append(instr_id)
            print(f"   ✓ {name} (id={instr_id})")
    
    print()
    
    # Step 3: Create schedules for next 7 days
    print("📅 Creating weekly schedules...")
    time_slots = [
        ("08:00", "09:00", 60, 8),
        ("10:00", "11:00", 60, 8),
        ("14:00", "15:30", 90, 12),
        ("16:00", "17:00", 60, 8),
        ("19:00", "20:30", 90, 12),
    ]
    
    created_count = 0
    for instr_id in instructor_ids:
        for day_offset in range(7):
            schedule_date = date.today() + timedelta(days=day_offset)
            
            for start_time, end_time, duration, max_bookings in time_slots:
                execute_sql("""
                    INSERT INTO schedule (instructor_id, date, start_time, end_time, 
                                       duration_minutes, max_bookings, available_slots, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (instructor_id, date, start_time) DO NOTHING
                """, (instr_id, schedule_date, start_time, end_time, 
                      duration, max_bookings, max_bookings))
                created_count += 1
    
    total_schedules = execute_sql("SELECT COUNT(*) FROM schedule WHERE date >= CURRENT_DATE")[0][0]
    print(f"   ✓ Created {created_count} schedule entries")
    print()
    
    # Step 4: Summary
    print("📊 Database Statistics:")
    studios = execute_sql("SELECT COUNT(*) FROM studio")[0][0]
    instructors = execute_sql("SELECT COUNT(*) FROM instructor")[0][0]  
    schedules = execute_sql("SELECT COUNT(*) FROM schedule WHERE date >= CURRENT_DATE")[0][0]
    bookings = execute_sql("SELECT COUNT(*) FROM booking")[0][0]
    
    print(f"   Studios:     {studios}")
    print(f"   Instructors: {instructors}")
    print(f"   Schedules:   {schedules} (upcoming)")
    print(f"   Bookings:    {bookings}")
    print()
    print("=" * 60)
    print("✅ Seeding completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
