from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.security import verify_token
from app.models.user import User
from app.models.travel_plan import TravelPlan
from app.schemas.travel_plan import (
    TravelPlanCreate, 
    TravelPlanUpdate, 
    TravelPlanResponse,
    TravelPlanListResponse,
    TravelPlanDetailResponse,
    TravelPlanGenerateRequest
)
from app.services.ai_travel_service import ai_travel_service
from datetime import datetime
import json

router = APIRouter()
security = HTTPBearer()

async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """获取当前用户ID"""
    token = credentials.credentials
    user_id = verify_token(token)
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的访问令牌"
        )
    
    return int(user_id)

@router.get("/", response_model=TravelPlanListResponse)
async def get_travel_plans(
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """获取当前用户的行程列表"""
    query = db.query(TravelPlan).filter(TravelPlan.user_id == current_user_id)
    
    if status_filter:
        query = query.filter(TravelPlan.status == status_filter)
    
    travel_plans = query.order_by(TravelPlan.created_at.desc()).all()
    
    return {
        "code": 200,
        "message": "获取成功",
        "data": travel_plans
    }

@router.get("/{plan_id}", response_model=TravelPlanDetailResponse)
async def get_travel_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """获取行程详情"""
    travel_plan = db.query(TravelPlan).filter(
        TravelPlan.id == plan_id,
        TravelPlan.user_id == current_user_id
    ).first()
    
    if not travel_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="行程不存在或无权限访问"
        )
    
    return {
        "code": 200,
        "message": "获取成功",
        "data": travel_plan
    }

@router.post("/", response_model=TravelPlanDetailResponse)
async def create_travel_plan(
    plan_data: TravelPlanCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """创建新行程"""
    # 验证日期
    if plan_data.start_date >= plan_data.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="结束日期必须晚于开始日期"
        )
    
    # 创建行程记录
    travel_plan = TravelPlan(
        user_id=current_user_id,
        title=plan_data.title,
        destination=plan_data.destination,
        start_date=plan_data.start_date,
        end_date=plan_data.end_date,
        budget=plan_data.budget,
        people_count=plan_data.people_count,
        preferences=plan_data.preferences or [],
        status='draft'
    )
    
    db.add(travel_plan)
    db.commit()
    db.refresh(travel_plan)
    
    return {
        "code": 200,
        "message": "创建成功",
        "data": travel_plan
    }

@router.post("/generate", response_model=TravelPlanDetailResponse)
async def generate_travel_plan(
    request: TravelPlanGenerateRequest,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """AI生成行程规划"""
    # 验证日期
    if request.start_date >= request.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="结束日期必须晚于开始日期"
        )
    
    try:
        # 调用AI服务生成行程
        ai_result = await ai_travel_service.generate_travel_plan(
            destination=request.destination,
            start_date=request.start_date,
            end_date=request.end_date,
            budget=float(request.budget),
            people_count=request.people_count,
            preferences=request.preferences,
            special_requirements=request.special_requirements
        )
        
        # 创建行程记录
        travel_plan = TravelPlan(
            user_id=current_user_id,
            title=f"{request.destination}之旅",
            destination=request.destination,
            start_date=request.start_date,
            end_date=request.end_date,
            budget=request.budget,
            people_count=request.people_count,
            preferences=request.preferences,
            itinerary=ai_result.get("itinerary", []),
            status='draft'
        )
        
        db.add(travel_plan)
        db.commit()
        db.refresh(travel_plan)
        
        return {
            "code": 200,
            "message": "AI行程生成成功",
            "data": travel_plan
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成行程失败: {str(e)}"
        )

@router.put("/{plan_id}", response_model=TravelPlanDetailResponse)
async def update_travel_plan(
    plan_id: int,
    plan_data: TravelPlanUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """更新行程"""
    travel_plan = db.query(TravelPlan).filter(
        TravelPlan.id == plan_id,
        TravelPlan.user_id == current_user_id
    ).first()
    
    if not travel_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="行程不存在或无权限访问"
        )
    
    # 更新字段
    update_data = plan_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(travel_plan, field, value)
    
    # 验证日期
    if travel_plan.start_date >= travel_plan.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="结束日期必须晚于开始日期"
        )
    
    db.commit()
    db.refresh(travel_plan)
    
    return {
        "code": 200,
        "message": "更新成功",
        "data": travel_plan
    }

@router.delete("/{plan_id}")
async def delete_travel_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """删除行程"""
    travel_plan = db.query(TravelPlan).filter(
        TravelPlan.id == plan_id,
        TravelPlan.user_id == current_user_id
    ).first()
    
    if not travel_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="行程不存在或无权限访问"
        )
    
    db.delete(travel_plan)
    db.commit()
    
    return {"code": 200, "message": "删除成功", "data": None}