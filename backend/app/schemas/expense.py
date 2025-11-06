from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class ExpenseBase(BaseModel):
    category: str = Field(..., pattern="^(transport|accommodation|food|attraction|shopping|other)$", description="费用类别")
    amount: Decimal = Field(..., ge=0, description="金额")
    description: Optional[str] = Field(None, max_length=500, description="描述")
    expense_date: datetime = Field(..., description="费用发生日期")

class ExpenseCreate(ExpenseBase):
    travel_plan_id: int = Field(..., description="关联的行程ID")

class ExpenseUpdate(BaseModel):
    category: Optional[str] = Field(None, pattern="^(transport|accommodation|food|attraction|shopping|other)$")
    amount: Optional[Decimal] = Field(None, ge=0)
    description: Optional[str] = Field(None, max_length=500)
    expense_date: Optional[datetime] = None

class ExpenseResponse(ExpenseBase):
    id: int
    travel_plan_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CategoryExpense(BaseModel):
    category: str
    budgeted: Decimal
    spent: Decimal
    remaining: Decimal
    percentage: float

class BudgetAnalysisResponse(BaseModel):
    total_budget: Decimal
    total_spent: Decimal
    remaining: Decimal
    percentage_used: float
    category_breakdown: List[CategoryExpense]

class ExpenseListResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: List[ExpenseResponse]

class ExpenseDetailResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: ExpenseResponse

class BudgetAnalysisDetailResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: BudgetAnalysisResponse