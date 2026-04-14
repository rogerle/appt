"""
Database Connection Module

Provides SQLAlchemy engine, session factory, and connection pool configuration.
Includes slow query monitoring for performance optimization.
"""

import logging
import time
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# SQLAlchemy 2.0 style Base - call the function to get the base class
Base = declarative_base()

from app.core.config import settings

# Configure logger
logger = logging.getLogger(__name__)

# SQLAlchemy Base class for models (export as Base for compatibility)
Base = declarative_base()


class DatabaseManager:
    """Manages database connection and sessions."""

    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        
    def connect(self) -> None:
        """Create database engine and session factory."""
        
        # Create SQLAlchemy engine with connection pool configuration
        self.engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,           # Auto-detect invalid connections
            pool_size=settings.DATABASE_POOL_SIZE if hasattr(settings, 'DATABASE_POOL_SIZE') else 10,
            max_overflow=settings.DATABASE_MAX_OVERFLOW if hasattr(settings, 'DATABASE_MAX_OVERFLOW') else 20,
            pool_recycle=settings.DATABASE_POOL_RECIRCLE if hasattr(settings, 'DATABASE_POOL_RECIRCLE') else 3600,
            pool_timeout=settings.DATABASE_POOL_TIMEOUT if hasattr(settings, 'DATABASE_POOL_TIMEOUT') else 30,
        )
        
        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
        )
        
        # Register slow query monitoring
        self._setup_slow_query_monitor()
        
        logger.info(f"Database connected: {settings.DATABASE_URL}")

    def _setup_slow_query_monitor(self) -> None:
        """Set up event listeners for slow query detection."""
        
        @event.listens_for(self.engine, "before_cursor_execute")
        def before_cursor_execute(
            conn, cursor, statement, parameters, context, executemany
        ):
            conn.info.setdefault('query_start_time', []).append(time.time())

        @event.listens_for(self.engine, "after_cursor_execute")
        def after_cursor_execute(
            conn, cursor, statement, parameters, context, executemany
        ):
            total_time = time.time() - conn.info['query_start_time'].pop(-1)
            
            # Log queries slower than 100ms (configurable threshold)
            if total_time > 0.1:
                logger.warning(
                    f"Slow query detected ({total_time*1000:.2f}ms): {statement[:100]}..."
                )

    def get_session(self) -> Generator[Session, None, None]:
        """
        Get a database session.
        
        Yields:
            Session: SQLAlchemy database session
        
        Example:
            >>> with db_manager.get_session() as session:
            ...     users = session.query(User).all()
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def close(self) -> None:
        """Close database connection."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")


# Singleton instance
db_manager = DatabaseManager()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for getting database sessions.
    
    This function can be used in API route dependencies:
    
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            items = db.query(Item).all()
            return items
    
    Yields:
        Session: SQLAlchemy database session
    """
    session = db_manager.SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    """Initialize database connection."""
    if not db_manager.engine:
        db_manager.connect()


# Auto-initialize on import
init_db()
