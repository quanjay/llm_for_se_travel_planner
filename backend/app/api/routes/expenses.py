"""
费用记录管理 API 路由
使用 Supabase 作为数据存储
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
from decimal import Decimal
from app.core.security import verify_token
from app.services.database_service import db
from app.schemas.expense import (
    ExpenseCreate,
    ExpenseUpdate,
    ExpenseResponse,
    ExpenseListResponse,
    ExpenseDetailResponse,
    BudgetAnalysisDetailResponse
)
from datetime import date
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


@router.post("/", response_model=ExpenseDetailResponse)
async def create_expense(
    expense_data: ExpenseCreate,
    current_user_id: int = Depends(get_current_user_id)
):
    """创建费用记录"""
    
    # 检查数据库服务
    if not db.is_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="数据库服务不可用"
        )
    
    try:
        # 如果有 travel_plan_id，验证行程是否存在且属于当前用户
        if expense_data.travel_plan_id:
            travel_plan = await db.get_travel_plan_by_id(expense_data.travel_plan_id, current_user_id)
            if not travel_plan:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="行程不存在或无权限访问"
                )
        
        # 准备数据
        expense_dict = {
            "travel_plan_id": expense_data.travel_plan_id,
            "category": expense_data.category,
            "amount": float(expense_data.amount),
            "description": expense_data.description,
            "expense_date": expense_data.expense_date.isoformat() if isinstance(expense_data.expense_date, date) else expense_data.expense_date
        }
        
        # 创建费用记录
        expense = await db.create_expense(current_user_id, expense_dict)
        
        logger.info(f"创建费用记录成功: {expense['id']}")
        
        return {
            "code": 200,
            "message": "费用记录创建成功",
            "data": expense
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建费用记录失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建费用记录失败: {str(e)}"
        )


@router.get("/travel-plan/{travel_plan_id}", response_model=ExpenseListResponse)
async def get_expenses_by_travel_plan(
    travel_plan_id: int,
    category: Optional[str] = Query(None, description="费用类别筛选"),
    current_user_id: int = Depends(get_current_user_id)
):
    """获取指定行程的费用记录"""
    
    # 检查数据库服务
    if not db.is_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="数据库服务不可用"
        )
    
    try:
        # 验证行程是否存在且属于当前用户
        travel_plan = await db.get_travel_plan_by_id(travel_plan_id, current_user_id)
        if not travel_plan:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="行程不存在或无权限访问"
            )
        
        # 获取行程的所有费用
        expenses = await db.get_plan_expenses(travel_plan_id, current_user_id)
        
        # 如果有类别筛选
        if category:
            expenses = [exp for exp in expenses if exp.get('category') == category]
        
        logger.info(f"获取行程 {travel_plan_id} 的费用记录成功，共 {len(expenses)} 条")
        
        return {
            "code": 200,
            "message": "获取成功",
            "data": expenses
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取费用记录失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取费用记录失败: {str(e)}"
        )


@router.put("/{expense_id}", response_model=ExpenseDetailResponse)
async def update_expense(
    expense_id: int,
    expense_data: ExpenseUpdate,
    current_user_id: int = Depends(get_current_user_id)
):
    """更新费用记录"""
    
    # 检查数据库服务
    if not db.is_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="数据库服务不可用"
        )
    
    try:
        # 检查费用是否存在
        existing_expense = await db.get_expense_by_id(expense_id, current_user_id)
        
        if not existing_expense:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="费用记录不存在或无权限访问"
            )
        
        # 准备更新数据
        update_dict = expense_data.model_dump(exclude_unset=True)
        
        # 转换日期格式
        if 'expense_date' in update_dict and update_dict['expense_date']:
            update_dict['expense_date'] = update_dict['expense_date'].isoformat() if isinstance(update_dict['expense_date'], date) else update_dict['expense_date']
        
        if 'amount' in update_dict and update_dict['amount'] is not None:
            update_dict['amount'] = float(update_dict['amount'])
        
        # 如果要更新 travel_plan_id，验证行程是否存在
        if 'travel_plan_id' in update_dict and update_dict['travel_plan_id']:
            travel_plan = await db.get_travel_plan_by_id(update_dict['travel_plan_id'], current_user_id)
            if not travel_plan:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="行程不存在或无权限访问"
                )
        
        # 更新费用记录
        updated_expense = await db.update_expense(expense_id, current_user_id, update_dict)
        
        logger.info(f"更新费用记录成功: {expense_id}")
        
        return {
            "code": 200,
            "message": "费用记录更新成功",
            "data": updated_expense
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新费用记录失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新费用记录失败: {str(e)}"
        )


@router.delete("/{expense_id}")
async def delete_expense(
    expense_id: int,
    current_user_id: int = Depends(get_current_user_id)
):
    """删除费用记录"""
    
    # 检查数据库服务
    if not db.is_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="数据库服务不可用"
        )
    
    try:
        # 检查费用是否存在
        existing_expense = await db.get_expense_by_id(expense_id, current_user_id)
        
        if not existing_expense:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="费用记录不存在或无权限访问"
            )
        
        # 删除费用记录
        await db.delete_expense(expense_id, current_user_id)
        
        logger.info(f"删除费用记录成功: {expense_id}")
        
        return {
            "code": 200,
            "message": "费用记录删除成功",
            "data": None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除费用记录失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除费用记录失败: {str(e)}"
        )


@router.get("/budget-analysis/{travel_plan_id}", response_model=BudgetAnalysisDetailResponse)
async def get_budget_analysis(
    travel_plan_id: int,
    current_user_id: int = Depends(get_current_user_id)
):
    """获取预算分析"""
    
    # 检查数据库服务
    if not db.is_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="数据库服务不可用"
        )
    
    try:
        # 验证行程是否存在且属于当前用户
        travel_plan = await db.get_travel_plan_by_id(travel_plan_id, current_user_id)
        if not travel_plan:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="行程不存在或无权限访问"
            )
        
        # 获取费用统计
        expense_stats = await db.get_expense_statistics(current_user_id, travel_plan_id)
        
        # 计算预算分析（统一使用 Decimal 类型）
        budget = Decimal(str(travel_plan.get('budget', 0))) if travel_plan.get('budget') else Decimal('0')
        total_spent = Decimal(str(expense_stats['total']))
        remaining = budget - total_spent
        usage_percentage = float((total_spent / budget * 100) if budget > 0 else 0)
        
        # 构建分类明细列表（符合 schema 要求）
        category_breakdown = []
        for category, stats in expense_stats['by_category'].items():
            spent_amount = Decimal(str(stats['total']))
            category_breakdown.append({
                "category": category,
                "budgeted": Decimal('0'),  # 可以根据需要设置每个类别的预算
                "spent": spent_amount,
                "remaining": Decimal('0'),  # 如果有分类预算的话
                "percentage": float((spent_amount / total_spent * 100) if total_spent > 0 else 0)
            })
        
        # 符合 BudgetAnalysisResponse schema 的数据结构
        analysis = {
            "total_budget": budget,
            "total_spent": total_spent,
            "remaining": remaining,
            "percentage_used": usage_percentage,
            "category_breakdown": category_breakdown
        }
        
        logger.info(f"获取行程 {travel_plan_id} 的预算分析成功")
        
        return {
            "code": 200,
            "message": "获取成功",
            "data": analysis
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取预算分析失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取预算分析失败: {str(e)}"
        )


@router.get("/summary/user")
async def get_user_expenses_summary(
    current_user_id: int = Depends(get_current_user_id)
):
    """获取用户费用总览"""
    
    # 检查数据库服务
    if not db.is_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="数据库服务不可用"
        )
    
    try:
        # 获取用户统计
        stats = await db.get_user_statistics(current_user_id)
        
        # 获取所有费用进行详细统计
        expense_stats = await db.get_expense_statistics(current_user_id)
        
        summary = {
            "total_expenses": stats['total_expenses'],
            "expenses_count": stats['expenses_count'],
            "travel_plans_count": stats['plans_count'],
            "average_expense": expense_stats['average'],
            "category_breakdown": expense_stats['by_category']
        }
        
        logger.info(f"获取用户 {current_user_id} 的费用总览成功")
        
        return {
            "code": 200,
            "message": "获取成功",
            "data": summary
        }
        
    except Exception as e:
        logger.error(f"获取费用总览失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取费用总览失败: {str(e)}"
        )
