from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class Instructor(Base):
    """教练模型"""
    
    __tablename__ = "instructors"
    
    id = Column(Integer, primary_key=True, index=True)
    studio_id = Column(Integer, ForeignKey("studios.id", ondelete="CASCADE"), nullable=True)
    name = Column(String(50), nullable=False)
    avatar_url = Column(Text, nullable=True)
    description = Column(Text, nullable=True)  # 教练简介
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联关系
    studio = relationship("Studio", back_populates="instructors")
    schedules = relationship("Schedule", back_populates="instructor", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="instructor", cascade="all, delete-orphan")
    
    # 索引 - 优化查询性能 (Performance Optimization)
    __table_args__ = (
        Index('idx_instructors_studio', 'studio_id'),           # Studio filtering
        Index('idx_instructors_active', 'is_active'),          # Active instructor listing
        Index('idx_instructors_name', 'name'),                 # Name search optimization
        Index('idx_instructor_composite', 'studio_id', 'is_active'),  # Composite index for filtered queries
    )
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "name": self.name,
            "avatar_url": self.avatar_url,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
