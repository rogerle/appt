from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Time, Date, JSON, Index, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class Booking(Base):
    """预约记录模型"""
    
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id", ondelete="CASCADE"), nullable=False)
    customer_name = Column(String(50), nullable=False)
    customer_phone = Column(String(20), nullable=False)
    status = Column(String(20), default='confirmed')  # confirmed/cancelled/no_show
    notes = Column(Text, nullable=True)  # 备注（如：过敏史、特殊需求）
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    schedule = relationship("Schedule", back_populates="bookings")
    instructor = relationship("Instructor", secondary=lambda: Schedule.__table__, 
                              back_populates="bookings")
    
    # 索引 - 优化查询性能 (Performance Optimization)
    __table_args__ = (
        Index('idx_bookings_schedule', 'schedule_id'),           # Schedule lookup optimization
        Index('idx_bookings_customer', 'customer_phone'),         # Customer-based queries
        Index('idx_bookings_status', 'status'),                   # Status filtering
        Index('idx_bookings_date', 'created_at'),                 # Date-based sorting
        # Composite indexes for complex queries (Performance Critical)
        Index('idx_booking_composite_customer_status', 'customer_phone', 'status'),
        Index('idx_booking_composite_schedule_created', 'schedule_id', 'created_at'),
    )
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "schedule_id": self.schedule_id,
            "customer_name": self.customer_name,
            "customer_phone": self.customer_phone,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
