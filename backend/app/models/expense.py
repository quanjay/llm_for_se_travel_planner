from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Expense(Base):
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    travel_plan_id = Column(Integer, ForeignKey("travel_plans.id"), nullable=False)
    category = Column(String(50), nullable=False)  # transport, accommodation, food, attraction, shopping, other
    amount = Column(Numeric(10, 2), nullable=False)
    description = Column(String(500), nullable=True)
    expense_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系
    travel_plan = relationship("TravelPlan", back_populates="expenses")