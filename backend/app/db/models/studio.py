from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class Studio(Base):
    """瑜伽馆信息模型"""
    
    __tablename__ = "studios"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联关系 - 一对多：一个瑜伽馆有多个教练
    instructors = relationship("Instructor", back_populates="studio")
    
    # 索引
    __table_args__ = (
        Index('idx_studios_created', 'created_at'),
    )
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "address": self.address,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
