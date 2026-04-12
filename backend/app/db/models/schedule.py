from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Time, Date, JSONB, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class Schedule(Base):
    """排课计划模型 - 可预约时间段"""
    
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    instructor_id = Column(Integer, ForeignKey("instructors.id", ondelete="CASCADE"), nullable=False)
    studio_id = Column(Integer, ForeignKey("studios.id"), nullable=True)
    schedule_date = Column(Date, nullable=False)  # 日期
    start_time = Column(Time, nullable=False)     # 开始时间
    end_time = Column(Time, nullable=False)       # 结束时间
    max_bookings = Column(Integer, default=1)      # 最大预约人数（默认单人课）
    is_recurring = Column(Boolean, default=False)  # 是否重复排课
    recurrence_pattern = Column(JSONB, nullable=True)  # 重复规则（如：每周周一三五）
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联关系
    instructor = relationship("Instructor", back_populates="schedules")
    studio = relationship("Studio", backref="schedules")
    bookings = relationship("Booking", back_populates="schedule", cascade="all, delete-orphan")
    
    # 约束：结束时间必须晚于开始时间
    __table_args__ = (
        Index('idx_schedules_date', 'schedule_date'),           # Date-based queries
        Index('idx_schedules_instructor', 'instructor_id'),     # Instructor filtering
        Index('idx_schedules_active', 'is_recurring'),          # Active schedules only
        # Composite indexes for common query patterns (Performance Critical)
        Index('idx_schedule_composite_date_instructor', 'schedule_date', 'instructor_id'),
        Index('idx_schedule_composite_time', 'start_time', 'end_time'),
        {'sqlite_autoincrement': True},  # SQLite 兼容性
    )
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "instructor_id": self.instructor_id,
            "schedule_date": self.schedule_date.isoformat() if self.schedule_date else None,
            "start_time": self.start_time.strftime("%H:%M") if self.start_time else None,
            "end_time": self.end_time.strftime("%H:%M") if self.end_time else None,
            "max_bookings": self.max_bookings,
            "is_recurring": self.is_recurring,
        }
