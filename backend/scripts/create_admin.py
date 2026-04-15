#!/usr/bin/env python3
"""Create Admin User Script - Direct database insertion to bypass bcrypt issues"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.db.database import db_manager
from app.core.config import settings
from app.db.models.user import User


def create_admin_direct():
    """Create admin user using bcrypt-compatible password."""
    
    db_manager.connect()
    session = db_manager.SessionLocal()
    
    try:
        # Check if admin already exists
        existing = session.query(User).filter(
            (User.email == "admin@appt.local") | 
            (User.username == "admin")
        ).first()
        
        if existing:
            print(f"✓ Admin user already exists:")
            print(f"  Email: {existing.email}")
            print(f"  Username: {existing.username}")
            print(f"  Role: {existing.role}")
            return
        
        # Use simple password that works with bcrypt (max 72 bytes after salt)
        admin_password = getattr(settings, 'ADMIN_PASSWORD', 'admin123')
        
        # Import hash function
        from app.core.security import hash_password
        
        print(f"Creating admin user...")
        print(f"  Password: {admin_password}")
        print(f"  Hashing with bcrypt...")
        
        try:
            hashed = hash_password(admin_password)
            print(f"  ✓ Password hashed successfully (length: {len(hashed)})")
            
            # Create admin user
            admin_user = User(
                email="admin@appt.local",
                username="admin",
                hashed_password=hashed,
                role="admin",
                is_active=True
            )
            
            session.add(admin_user)
            session.commit()
            session.refresh(admin_user)
            
            print(f"\n✅ Admin user created successfully!")
            print("=" * 50)
            print("🔐 Login Credentials:")
            print(f"   Email: admin@appt.local")
            print(f"   Password: {admin_password}")
            print(f"   Role: {admin_user.role}")
            print(f"   User ID: {admin_user.id}")
            print("=" * 50)
            print("\n📝 Next steps:")
            print("   1. Test login API:")
            print("      curl -X POST http://localhost:8000/api/v1/auth/login \\")
            print("        -H 'Content-Type: application/json' \\")
            print(f"        -d '{{\"email\": \"admin@appt.local\", \"password\": \"{admin_password}\"}}'")
            print("\n   2. Copy the access_token from response")
            print("   3. Test protected endpoints:")
            print("      curl http://localhost:8000/api/v1/auth/me \\" )
            print(f"        -H 'Authorization: Bearer YOUR_TOKEN'")
            
        except ValueError as e:
            print(f"\n❌ bcrypt error: {e}")
            print("\n⚠️ Workaround: Creating user with plain text password (NOT SECURE!)")
            print("   This is only for testing - change PASSWORD_HASHING=false in production")
            
            # Fallback: use plain text (very insecure, but works for testing)
            admin_user = User(
                email="admin@appt.local",
                username="admin", 
                hashed_password=admin_password,  # Plain text!
                role="admin",
                is_active=True
            )
            
            session.add(admin_user)
            session.commit()
            print(f"⚠️ Admin created with plain password (temporary solution)")


    except Exception as e:
        session.rollback()
        print(f"\n❌ Error creating admin user: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
        
    finally:
        session.close()


if __name__ == "__main__":
    print("=" * 60)
    print("🔐 Admin User Creation Script")
    print("=" * 60)
    print()
    
    create_admin_direct()
