from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

class TravelPlanBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="行程标题")
    destination: str = Field(..., min_length=1, max_length=255, description="目的地")
    start_date: datetime = Field(..., description="开始日期")
    end_date: datetime = Field(..., description="结束日期")
    budget: Decimal = Field(..., ge=0, description="预算金额")
    people_count: int = Field(..., ge=1, description="出行人数")
    preferences: Optional[List[str]] = Field(default=[], description="偏好标签")

class TravelPlanCreate(TravelPlanBase):
    special_requirements: Optional[str] = Field(None, max_length=1000, description="特殊需求")

class TravelPlanUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    destination: Optional[str] = Field(None, min_length=1, max_length=255)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget: Optional[Decimal] = Field(None, ge=0)
    people_count: Optional[int] = Field(None, ge=1)
    preferences: Optional[List[str]] = None
    status: Optional[str] = Field(None, pattern="^(draft|published|completed)$")

class ActivityBase(BaseModel):
    type: str = Field(..., pattern="^(attraction|restaurant|hotel|transport|shopping|entertainment)$")
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    location: str = Field(..., min_length=1, max_length=255)
    start_time: str = Field(..., description="开始时间，格式：HH:MM")
    end_time: str = Field(..., description="结束时间，格式：HH:MM")
    cost: Decimal = Field(..., ge=0, description="费用")
    rating: Optional[float] = Field(None, ge=0, le=5)
    image_url: Optional[str] = None

class DayItineraryBase(BaseModel):
    day: int = Field(..., ge=1, description="第几天")
    date: str = Field(..., description="日期，格式：YYYY-MM-DD")
    activities: List[ActivityBase] = Field(default=[], description="活动列表")
    total_cost: Decimal = Field(default=0, ge=0, description="当日总费用")

class TravelPlanResponse(TravelPlanBase):
    id: int
    user_id: int
    itinerary: Optional[List[DayItineraryBase]] = None
    total_cost: Decimal = Field(default=0)
    status: str = "draft"
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class TravelPlanGenerateRequest(BaseModel):
    destination: str = Field(..., min_length=1, description="目的地")
    start_date: datetime = Field(..., description="开始日期")
    end_date: datetime = Field(..., description="结束日期")
    budget: Decimal = Field(..., ge=0, description="预算金额")
    people_count: int = Field(..., ge=1, description="出行人数")
    preferences: List[str] = Field(default=[], description="偏好标签：美食、购物、文化、自然风光、亲子、商务等")
    special_requirements: Optional[str] = Field(None, description="特殊需求")

class TravelPlanListResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: List[TravelPlanResponse]

class TravelPlanDetailResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: TravelPlanResponse