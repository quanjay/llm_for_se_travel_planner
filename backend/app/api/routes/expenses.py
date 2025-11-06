from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.security import verify_token
from app.schemas.expense import (
    ExpenseCreate,
    ExpenseUpdate,
    ExpenseResponse,
    ExpenseListResponse,
    ExpenseDetailResponse,
    BudgetAnalysisDetailResponse
)
from app.services.expense_service import ExpenseService

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
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """创建费用记录"""
    try:
        expense = ExpenseService.create_expense(db, expense_data, current_user_id)
        return {
            "code": 200,
            "message": "费用记录创建成功",
            "data": expense
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建费用记录失败: {str(e)}"
        )

@router.get("/travel-plan/{travel_plan_id}", response_model=ExpenseListResponse)
async def get_expenses_by_travel_plan(
    travel_plan_id: int,
    category: Optional[str] = Query(None, description="费用类别筛选"),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """获取指定行程的费用记录"""
    try:
        expenses = ExpenseService.get_expenses_by_travel_plan(
            db, travel_plan_id, current_user_id, category
        )
        return {
            "code": 200,
            "message": "获取成功",
            "data": expenses
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{expense_id}", response_model=ExpenseDetailResponse)
async def update_expense(
    expense_id: int,
    expense_data: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """更新费用记录"""
    try:
        expense = ExpenseService.update_expense(db, expense_id, expense_data, current_user_id)
        return {
            "code": 200,
            "message": "费用记录更新成功",
            "data": expense
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新费用记录失败: {str(e)}"
        )

@router.delete("/{expense_id}")
async def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """删除费用记录"""
    try:
        ExpenseService.delete_expense(db, expense_id, current_user_id)
        return {
            "code": 200,
            "message": "费用记录删除成功",
            "data": None
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除费用记录失败: {str(e)}"
        )

@router.get("/budget-analysis/{travel_plan_id}", response_model=BudgetAnalysisDetailResponse)
async def get_budget_analysis(
    travel_plan_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """获取预算分析"""
    try:
        analysis = ExpenseService.get_budget_analysis(db, travel_plan_id, current_user_id)
        return {
            "code": 200,
            "message": "获取成功",
            "data": analysis
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取预算分析失败: {str(e)}"
        )

@router.get("/summary/user")
async def get_user_expenses_summary(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """获取用户费用总览"""
    try:
        summary = ExpenseService.get_user_expenses_summary(db, current_user_id)
        return {
            "code": 200,
            "message": "获取成功",
            "data": summary
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取费用总览失败: {str(e)}"
        )