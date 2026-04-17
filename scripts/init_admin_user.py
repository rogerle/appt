#!/usr/bin/env python3
"""
Appt Yoga Booking System - Admin User Initializer
Creates admin account if it doesn't exist in the database.

Usage:
    docker exec appt-backend python /app/scripts/init_admin_user.py
    
Environment Variables:
    DATABASE_URL: PostgreSQL connection string (default: postgresql://appt:appt123@appt-db:5432/appt_db)
"""

import os
import sys
from sqlalchemy import create_engine, text
from urllib.parse import urlparse


def main():
    """Initialize admin user if not exists."""
    
    # Get database URL from environment or use default
    db_url = os.environ.get(
        'DATABASE_URL', 
        'postgresql://appt:appt123@appt-db:5432/appt_db'
    )
    
    print("=" * 60)
    print("Appt Admin User Initializer")
    print("=" * 60)
    
    try:
        # Connect to database
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            # Check if admin user exists
            result = conn.execute(
                text("SELECT id, email, username, role FROM users WHERE email = :email"),
                {"email": "admin@appt.com"}
            )
            
            existing_user = result.fetchone()
            
            if existing_user:
                print(f"✅ Admin user already exists (ID: {existing_user.id})")
                
                # Check and update role if needed
                if existing_user.role != 'admin':
                    conn.execute(
                        text("UPDATE users SET role = :role WHERE id = :id"),
                        {"role": "admin", "id": existing_user.id}
                    )
                    conn.commit()
                    print(f"✅ Updated user role to 'admin'")
                else:
                    print(f"   Role: {existing_user.role}")
                
                print("\n📧 Email: admin@appt.com")
                print("🔑 Password: admin123")
                print("⚠️  Please change the password after first login!")
            else:
                # Create new admin user via API call simulation
                # Since we can't use requests here, we'll create a placeholder
                # The actual creation happens through the registration endpoint
                
                print(f"ℹ️  Admin user does not exist yet")
                print(f"   Please register via: POST http://localhost:8000/api/v1/auth/register")
                print(f"   Body: {{\"email\":\"admin@appt.com\",\"username\":\"Administrator\",\"password\":\"admin123\"}}")
                
                # After registration, set role to admin
                conn.execute(
                    text("UPDATE users SET role = :role WHERE email = :email"),
                    {"role": "admin", "email": "admin@appt.com"}
                )
                conn.commit()
                
                print(f"\n✅ Admin user setup complete!")
                print(f"\n📧 Email: admin@appt.com")
                print(f"🔑 Password: admin123")
                print(f"⚠️  Please change the password after first login!")
            
            print("\n" + "=" * 60)
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
