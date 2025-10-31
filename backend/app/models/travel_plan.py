from sqlalchemy import Column, Integer, String, DateTime, Text, Numeric, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class TravelPlan(Base):
    __tablename__ = "travel_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    destination = Column(String(255), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    budget = Column(Numeric(10, 2), nullable=False)
    people_count = Column(Integer, nullable=False, default=1)
    preferences = Column(JSON, nullable=True)  # 存储偏好列表
    itinerary = Column(JSON, nullable=True)    # 存储完整行程JSON
    total_cost = Column(Numeric(10, 2), nullable=True, default=0.00)
    status = Column(String(20), nullable=False, default='draft')  # draft, published, completed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系
    user = relationship("User")
    expenses = relationship("Expense", back_populates="travel_plan")