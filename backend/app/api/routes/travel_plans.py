"""
旅行计划管理 API 路由
使用 Supabase 作为数据存储
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
from app.core.security import verify_token
from app.services.database_service import db
from app.schemas.travel_plan import (
    TravelPlanCreate, 
    TravelPlanUpdate, 
    TravelPlanResponse,
    TravelPlanListResponse,
    TravelPlanDetailResponse,
    TravelPlanGenerateRequest
)
from app.services.ai_travel_service import ai_travel_service
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

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
    current_user_id: int = Depends(get_current_user_id)
):
    """获取当前用户的行程列表"""
    
    # 检查数据库服务
    if not db.is_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="数据库服务不可用"
        )
    
    try:
        # 从数据库获取行程列表
        travel_plans = await db.get_user_travel_plans(current_user_id, status_filter)
        
        logger.info(f"获取用户 {current_user_id} 的行程列表成功，共 {len(travel_plans)} 条")
        
        return {
            "code": 200,
            "message": "获取成功",
            "data": travel_plans
        }
        
    except Exception as e:
        logger.error(f"获取行程列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取行程列表失败: {str(e)}"
        )


@router.get("/{plan_id}", response_model=TravelPlanDetailResponse)
async def get_travel_plan(
    plan_id: int,
    current_user_id: int = Depends(get_current_user_id)
):
    """获取行程详情"""
    
    # 检查数据库服务
    if not db.is_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="数据库服务不可用"
        )
    
    try:
        # 从数据库获取行程
        travel_plan = await db.get_travel_plan_by_id(plan_id, current_user_id)
        
        if not travel_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="行程不存在或无权限访问"
            )
        
        logger.info(f"获取行程 {plan_id} 详情成功")
        
        return {
            "code": 200,
            "message": "获取成功",
            "data": travel_plan
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取行程详情失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取行程详情失败: {str(e)}"
        )


@router.post("/", response_model=TravelPlanDetailResponse)
async def create_travel_plan(
    plan_data: TravelPlanCreate,
    current_user_id: int = Depends(get_current_user_id)
):
    """创建新行程"""
    
    # 检查数据库服务
    if not db.is_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="数据库服务不可用"
        )
    
    try:
        # 验证日期 - 允许单日游（开始和结束是同一天）
        if plan_data.start_date > plan_data.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="结束日期不能早于开始日期"
            )
        
        # 准备数据
        plan_dict = {
            "title": plan_data.title,
            "destination": plan_data.destination,
            "start_date": plan_data.start_date.isoformat() if isinstance(plan_data.start_date, date) else plan_data.start_date,
            "end_date": plan_data.end_date.isoformat() if isinstance(plan_data.end_date, date) else plan_data.end_date,
            "budget": float(plan_data.budget) if plan_data.budget else None,
            "people_count": plan_data.people_count,
            "preferences": plan_data.preferences or [],
            "status": "draft"
        }
        
        # 创建行程
        travel_plan = await db.create_travel_plan(current_user_id, plan_dict)
        
        logger.info(f"创建行程成功: {travel_plan['id']}")
        
        return {
            "code": 200,
            "message": "创建成功",
            "data": travel_plan
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建行程失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建行程失败: {str(e)}"
        )


@router.post("/generate", response_model=TravelPlanDetailResponse)
async def generate_travel_plan(
    request: TravelPlanGenerateRequest,
    current_user_id: int = Depends(get_current_user_id)
):
    """AI生成行程规划"""
    
    # 添加调试日志
    logger.info(f"收到AI生成请求，用户ID: {current_user_id}")
    logger.info(f"请求数据: destination={request.destination}, start_date={request.start_date}, end_date={request.end_date}, budget={request.budget}, people_count={request.people_count}")
    
    # 检查数据库服务
    if not db.is_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="数据库服务不可用"
        )
    
    try:
        # 验证日期 - 允许单日游（开始和结束是同一天）
        if request.start_date > request.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="结束日期不能早于开始日期"
            )
        
        # 调用AI服务生成行程
        logger.info(f"开始生成AI行程: {request.destination}")
        
        ai_result = await ai_travel_service.generate_travel_plan(
            destination=request.destination,
            start_date=request.start_date,
            end_date=request.end_date,
            budget=float(request.budget),
            people_count=request.people_count,
            preferences=request.preferences,
            special_requirements=request.special_requirements
        )
        
        # 准备数据
        plan_dict = {
            "title": f"{request.destination}之旅",
            "destination": request.destination,
            "start_date": request.start_date.isoformat() if isinstance(request.start_date, date) else request.start_date,
            "end_date": request.end_date.isoformat() if isinstance(request.end_date, date) else request.end_date,
            "budget": float(request.budget),
            "people_count": request.people_count,
            "preferences": request.preferences,
            "itinerary": ai_result.get("itinerary", []),
            "status": "draft"
        }
        
        # 创建行程
        travel_plan = await db.create_travel_plan(current_user_id, plan_dict)
        
        logger.info(f"AI行程生成成功: {travel_plan['id']}")
        
        return {
            "code": 200,
            "message": "AI行程生成成功",
            "data": travel_plan
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成行程失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成行程失败: {str(e)}"
        )


@router.put("/{plan_id}", response_model=TravelPlanDetailResponse)
async def update_travel_plan(
    plan_id: int,
    plan_data: TravelPlanUpdate,
    current_user_id: int = Depends(get_current_user_id)
):
    """更新行程"""
    
    # 检查数据库服务
    if not db.is_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="数据库服务不可用"
        )
    
    try:
        # 检查行程是否存在
        existing_plan = await db.get_travel_plan_by_id(plan_id, current_user_id)
        
        if not existing_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="行程不存在或无权限访问"
            )
        
        # 准备更新数据
        update_dict = plan_data.model_dump(exclude_unset=True)
        
        # 转换日期格式
        if 'start_date' in update_dict and update_dict['start_date']:
            update_dict['start_date'] = update_dict['start_date'].isoformat() if isinstance(update_dict['start_date'], date) else update_dict['start_date']
        
        if 'end_date' in update_dict and update_dict['end_date']:
            update_dict['end_date'] = update_dict['end_date'].isoformat() if isinstance(update_dict['end_date'], date) else update_dict['end_date']
        
        if 'budget' in update_dict and update_dict['budget'] is not None:
            update_dict['budget'] = float(update_dict['budget'])
        
        if 'total_cost' in update_dict and update_dict['total_cost'] is not None:
            update_dict['total_cost'] = float(update_dict['total_cost'])
        
        # 更新行程
        updated_plan = await db.update_travel_plan(plan_id, current_user_id, update_dict)
        
        logger.info(f"更新行程成功: {plan_id}")
        
        return {
            "code": 200,
            "message": "更新成功",
            "data": updated_plan
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新行程失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新行程失败: {str(e)}"
        )


@router.delete("/{plan_id}")
async def delete_travel_plan(
    plan_id: int,
    current_user_id: int = Depends(get_current_user_id)
):
    """删除行程"""
    
    # 检查数据库服务
    if not db.is_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="数据库服务不可用"
        )
    
    try:
        # 检查行程是否存在
        existing_plan = await db.get_travel_plan_by_id(plan_id, current_user_id)
        
        if not existing_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="行程不存在或无权限访问"
            )
        
        # 删除行程
        await db.delete_travel_plan(plan_id, current_user_id)
        
        logger.info(f"删除行程成功: {plan_id}")
        
        return {
            "code": 200,
            "message": "删除成功",
            "data": None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除行程失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除行程失败: {str(e)}"
        )
