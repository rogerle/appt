from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings
import logging
import time

settings = get_settings()

# 创建数据库引擎 - 优化性能配置
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,           # 自动检测连接有效性
    pool_size=10,                 # 连接池大小
    max_overflow=20,              # 最大溢出连接数
    pool_recycle=3600,            # 每 1 小时回收连接，避免超时
    pool_timeout=30,              # 获取连接超时时间
    echo=False                    # 生产环境关闭 SQL 日志
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类 (所有模型继承此基类)
Base = declarative_base()

# SQL Query Performance Monitoring
logger = logging.getLogger(__name__)

@event.listens_for(engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, params, context, executemany):
    """
    Record start time for each SQL query.
    Used to detect slow queries (>100ms) for performance optimization.
    """
    conn.info.setdefault('query_start_time', []).append(time.time())

@event.listens_for(engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, params, context, executemany):
    """
    Log execution time for each SQL query.
    Queries taking >100ms are logged as warnings to identify bottlenecks.
    """
    total_time = time.time() - conn.info['query_start_time'].pop(-1)
    if total_time > 0.1:  # Log queries slower than 100ms
        logger.warning(f"Slow query detected ({total_time*1000:.2f}ms): {statement[:100]}...")


def get_db():
    """获取数据库会话的依赖项"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
