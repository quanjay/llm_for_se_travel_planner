from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models.expense import Expense
from app.models.travel_plan import TravelPlan
from app.schemas.expense import ExpenseCreate, ExpenseUpdate, BudgetAnalysisResponse, CategoryExpense
from decimal import Decimal

class ExpenseService:
    """费用管理服务"""
    
    @staticmethod
    def create_expense(db: Session, expense_data: ExpenseCreate, user_id: int) -> Expense:
        """创建费用记录"""
        # 验证行程是否属于当前用户
        travel_plan = db.query(TravelPlan).filter(
            and_(
                TravelPlan.id == expense_data.travel_plan_id,
                TravelPlan.user_id == user_id
            )
        ).first()
        
        if not travel_plan:
            raise ValueError("行程不存在或无权限访问")
        
        # 创建费用记录
        expense = Expense(**expense_data.model_dump())
        db.add(expense)
        db.commit()
        db.refresh(expense)
        
        # 更新行程总费用
        ExpenseService.update_travel_plan_total_cost(db, expense_data.travel_plan_id)
        
        return expense
    
    @staticmethod
    def get_expenses_by_travel_plan(
        db: Session, 
        travel_plan_id: int, 
        user_id: int,
        category: Optional[str] = None
    ) -> List[Expense]:
        """获取行程的费用记录"""
        # 验证行程权限
        travel_plan = db.query(TravelPlan).filter(
            and_(
                TravelPlan.id == travel_plan_id,
                TravelPlan.user_id == user_id
            )
        ).first()
        
        if not travel_plan:
            raise ValueError("行程不存在或无权限访问")
        
        query = db.query(Expense).filter(Expense.travel_plan_id == travel_plan_id)
        
        if category:
            query = query.filter(Expense.category == category)
        
        return query.order_by(Expense.expense_date.desc()).all()
    
    @staticmethod
    def update_expense(
        db: Session, 
        expense_id: int, 
        expense_data: ExpenseUpdate, 
        user_id: int
    ) -> Expense:
        """更新费用记录"""
        # 获取费用记录并验证权限
        expense = db.query(Expense).join(TravelPlan).filter(
            and_(
                Expense.id == expense_id,
                TravelPlan.user_id == user_id
            )
        ).first()
        
        if not expense:
            raise ValueError("费用记录不存在或无权限访问")
        
        # 更新字段
        update_data = expense_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(expense, field, value)
        
        db.commit()
        db.refresh(expense)
        
        # 更新行程总费用
        ExpenseService.update_travel_plan_total_cost(db, expense.travel_plan_id)
        
        return expense
    
    @staticmethod
    def delete_expense(db: Session, expense_id: int, user_id: int) -> bool:
        """删除费用记录"""
        expense = db.query(Expense).join(TravelPlan).filter(
            and_(
                Expense.id == expense_id,
                TravelPlan.user_id == user_id
            )
        ).first()
        
        if not expense:
            raise ValueError("费用记录不存在或无权限访问")
        
        travel_plan_id = expense.travel_plan_id
        db.delete(expense)
        db.commit()
        
        # 更新行程总费用
        ExpenseService.update_travel_plan_total_cost(db, travel_plan_id)
        
        return True
    
    @staticmethod
    def get_budget_analysis(db: Session, travel_plan_id: int, user_id: int) -> BudgetAnalysisResponse:
        """获取预算分析"""
        # 验证行程权限
        travel_plan = db.query(TravelPlan).filter(
            and_(
                TravelPlan.id == travel_plan_id,
                TravelPlan.user_id == user_id
            )
        ).first()
        
        if not travel_plan:
            raise ValueError("行程不存在或无权限访问")
        
        # 获取各类别的支出统计
        category_stats = db.query(
            Expense.category,
            func.sum(Expense.amount).label('total_spent')
        ).filter(
            Expense.travel_plan_id == travel_plan_id
        ).group_by(Expense.category).all()
        
        # 定义预算分类及默认分配比例
        default_budget_allocation = {
            'transport': 0.30,      # 交通 30%
            'accommodation': 0.35,  # 住宿 35%
            'food': 0.20,          # 餐饮 20%
            'attraction': 0.10,     # 景点 10%
            'shopping': 0.03,       # 购物 3%
            'other': 0.02          # 其他 2%
        }
        
        total_budget = float(travel_plan.budget)
        total_spent = sum(float(stat.total_spent) for stat in category_stats)
        
        # 构建分类预算分析
        category_breakdown = []
        for category, ratio in default_budget_allocation.items():
            budgeted = Decimal(str(total_budget * ratio))
            spent = Decimal('0')
            
            # 查找实际支出
            for stat in category_stats:
                if stat.category == category:
                    spent = stat.total_spent
                    break
            
            remaining = budgeted - spent
            percentage = float(spent / budgeted * 100) if budgeted > 0 else 0
            
            category_breakdown.append(CategoryExpense(
                category=category,
                budgeted=budgeted,
                spent=spent,
                remaining=remaining,
                percentage=percentage
            ))
        
        return BudgetAnalysisResponse(
            total_budget=Decimal(str(total_budget)),
            total_spent=Decimal(str(total_spent)),
            remaining=Decimal(str(total_budget - total_spent)),
            percentage_used=total_spent / total_budget * 100 if total_budget > 0 else 0,
            category_breakdown=category_breakdown
        )
    
    @staticmethod
    def update_travel_plan_total_cost(db: Session, travel_plan_id: int):
        """更新行程总费用"""
        total_cost = db.query(func.sum(Expense.amount)).filter(
            Expense.travel_plan_id == travel_plan_id
        ).scalar() or Decimal('0')
        
        travel_plan = db.query(TravelPlan).filter(TravelPlan.id == travel_plan_id).first()
        if travel_plan:
            travel_plan.total_cost = total_cost
            db.commit()
    
    @staticmethod
    def get_user_expenses_summary(db: Session, user_id: int) -> Dict[str, Any]:
        """获取用户的费用总览"""
        # 获取用户所有行程的费用统计
        result = db.query(
            func.count(Expense.id).label('total_records'),
            func.sum(Expense.amount).label('total_amount'),
            func.avg(Expense.amount).label('avg_amount')
        ).join(TravelPlan).filter(TravelPlan.user_id == user_id).first()
        
        # 按类别统计
        category_stats = db.query(
            Expense.category,
            func.count(Expense.id).label('count'),
            func.sum(Expense.amount).label('total')
        ).join(TravelPlan).filter(
            TravelPlan.user_id == user_id
        ).group_by(Expense.category).all()
        
        return {
            'total_records': result.total_records or 0,
            'total_amount': float(result.total_amount or 0),
            'average_amount': float(result.avg_amount or 0),
            'category_breakdown': [
                {
                    'category': stat.category,
                    'count': stat.count,
                    'total': float(stat.total)
                }
                for stat in category_stats
            ]
        }