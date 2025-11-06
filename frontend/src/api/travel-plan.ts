import api from './request'
import type { 
  TravelPlan, 
  TravelPlanRequest, 
  ApiResponse
} from '@/types'

export const travelPlanApi = {
  // 获取行程列表
  getTravelPlans: (status?: string): Promise<ApiResponse<TravelPlan[]>> => {
    const params = status ? { status_filter: status } : {}
    return api.get('/travel-plans', { params })
  },

  // 获取行程详情
  getTravelPlan: (id: number): Promise<ApiResponse<TravelPlan>> => {
    return api.get(`/travel-plans/${id}`)
  },

  // 创建行程
  createTravelPlan: (data: Partial<TravelPlan>): Promise<ApiResponse<TravelPlan>> => {
    return api.post('/travel-plans', data)
  },

  // AI生成行程 - 需要更长的等待时间
  generateTravelPlan: (data: TravelPlanRequest): Promise<ApiResponse<TravelPlan>> => {
    return api.post('/travel-plans/generate', data, {
      timeout: 180000, // 3分钟超时，确保能完成 AI 调用和重试
      headers: {
        'Content-Type': 'application/json'
      }
    })
  },

  // 更新行程
  updateTravelPlan: (id: number, data: Partial<TravelPlan>): Promise<ApiResponse<TravelPlan>> => {
    return api.put(`/travel-plans/${id}`, data)
  },

  // 删除行程
  deleteTravelPlan: (id: number): Promise<ApiResponse<null>> => {
    return api.delete(`/travel-plans/${id}`)
  }
}