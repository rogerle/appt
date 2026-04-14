#!/usr/bin/env python3
"""Initialize database tables using SQLAlchemy."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from app.core.config import settings

# Create engine
engine = create_engine(settings.DATABASE_URL)

# Import all models to register them with Base
try:
    from app.db.models.studio import Studio
    from app.db.models.instructor import Instructor  
    from app.db.models.schedule import Schedule
    from app.db.models.booking import Booking
    
    # Create all tables
    print("📊 Creating database tables...")
    
    with engine.connect() as conn:
        # Check if tables exist
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('studio', 'instructor', 'schedule', 'booking')
        """))
        
        existing_tables = [row[0] for row in result.fetchall()]
        
        if not existing_tables:
            print("   Tables don't exist yet, creating...")
            # Create all tables using Base.metadata
            from app.db.database import Base
            Base.metadata.create_all(engine)
            print("✓ All tables created successfully!")
        else:
            print(f"   Existing tables: {', '.join(existing_tables)}")
            
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
