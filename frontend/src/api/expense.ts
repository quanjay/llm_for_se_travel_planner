import api from './request'
import type { 
  Expense, 
  BudgetAnalysis, 
  ApiResponse 
} from '@/types'

export const expenseApi = {
  // 创建费用记录
  createExpense: (data: Omit<Expense, 'id' | 'created_at'>): Promise<ApiResponse<Expense>> => {
    return api.post('/expenses', data)
  },

  // 获取指定行程的费用记录
  getExpensesByTravelPlan: (
    travelPlanId: number, 
    category?: string
  ): Promise<ApiResponse<Expense[]>> => {
    const params = category ? { category } : {}
    return api.get(`/expenses/travel-plan/${travelPlanId}`, { params })
  },

  // 更新费用记录
  updateExpense: (
    id: number, 
    data: Partial<Omit<Expense, 'id' | 'created_at'>>
  ): Promise<ApiResponse<Expense>> => {
    return api.put(`/expenses/${id}`, data)
  },

  // 删除费用记录
  deleteExpense: (id: number): Promise<ApiResponse<null>> => {
    return api.delete(`/expenses/${id}`)
  },

  // 获取预算分析
  getBudgetAnalysis: (travelPlanId: number): Promise<ApiResponse<BudgetAnalysis>> => {
    return api.get(`/expenses/budget-analysis/${travelPlanId}`)
  },

  // 获取用户费用总览
  getUserExpensesSummary: (): Promise<ApiResponse<any>> => {
    return api.get('/expenses/summary/user')
  }
}