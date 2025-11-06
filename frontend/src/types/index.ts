// 用户相关类型
export interface User {
  id: number
  email: string
  username: string
  avatar?: string
  phone?: string
  created_at: string
  updated_at: string
}

export interface UserRegister {
  email: string
  username: string
  password: string
  phone?: string
}

export interface UserLogin {
  email: string
  password: string
}

// 行程相关类型
export interface TravelPlan {
  id: number
  user_id: number
  title: string
  destination: string
  start_date: string
  end_date: string
  budget: number
  people_count: number
  preferences: string[]
  itinerary: DayItinerary[]
  total_cost: number
  status: 'draft' | 'published' | 'completed'
  created_at: string
  updated_at: string
}

export interface DayItinerary {
  day: number
  date: string
  activities: Activity[]
  total_cost: number
}

export interface Activity {
  id: string
  type: 'attraction' | 'restaurant' | 'hotel' | 'transport'
  name: string
  description: string
  location: string
  start_time: string
  end_time: string
  cost: number
  rating?: number
  image_url?: string
}

// 费用相关类型
export interface Expense {
  id: number
  travel_plan_id: number
  category: 'transport' | 'accommodation' | 'food' | 'attraction' | 'shopping' | 'other'
  amount: number
  description: string
  expense_date: string
  created_at: string
}

export interface BudgetAnalysis {
  total_budget: number
  total_spent: number
  remaining: number
  percentage_used: number
  category_breakdown: CategoryExpense[]
}

export interface CategoryExpense {
  category: string
  budgeted: number
  spent: number
  remaining: number
}

// 旅行规划请求类型
export interface TravelPlanRequest {
  destination: string
  start_date: string
  end_date: string
  budget: number
  people_count: number
  preferences: string[]
  special_requirements?: string
}

// API响应类型
export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}