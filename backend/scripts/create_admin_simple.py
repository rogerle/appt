#!/usr/bin/env python3
"""Create Admin User - Simple SQL Insert (bypass bcrypt issues)"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.db.database import db_manager


def create_admin_sql():
    """Use raw SQL to insert admin user with plain password."""
    
    db_manager.connect()
    session = db_manager.SessionLocal()
    
    try:
        # Check if admin exists
        from sqlalchemy import text
        result = session.execute(text(
            "SELECT id FROM users WHERE username = 'admin'"
        ))
        existing = result.scalar()
        
        if existing:
            print(f"✓ Admin user already exists (id={existing})")
            return
        
        # Insert with plain password (bcrypt not working in this environment)
        from sqlalchemy import text
        session.execute(text(
            """INSERT INTO users (email, username, hashed_password, role, is_active, created_at, updated_at) 
                VALUES ('admin@appt.com', 'admin', 'admin123', 'admin', true, NOW(), NOW())"""
        ))
        
        session.commit()
        
        print("✅ Admin user created successfully!")
        print("=" * 50)
        print("🔐 Login Credentials:")
        print("   Email: admin@appt.com")
        print("   Password: admin123")  
        print("   Role: admin")
        print("=" * 50)


    except Exception as e:
        session.rollback()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        session.close()


if __name__ == "__main__":
    create_admin_sql()
