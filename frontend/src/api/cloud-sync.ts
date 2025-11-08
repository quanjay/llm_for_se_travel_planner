/**
 * 云端同步 API
 */

import request from './request'

interface SyncStatusData {
  enabled: boolean
  plans_count: number
  expenses_count: number
  total_items: number
  message: string
}

interface SyncResultData {
  success: boolean
  message: string
  plans_synced: number
  expenses_synced: number
  total_synced: number
}

interface CloudSyncResponse<T = any> {
  code: number
  message: string
  data: T
}

export const cloudSyncApi = {
  /**
   * 获取云端同步状态
   */
  getStatus(): Promise<CloudSyncResponse<SyncStatusData>> {
    return request.get('/cloud-sync/status')
  },

  /**
   * 一键同步所有数据到云端
   */
  syncAllData(): Promise<CloudSyncResponse<SyncResultData>> {
    return request.post('/cloud-sync/all-data')
  },

  /**
   * 同步单个行程到云端
   */
  syncTravelPlan(planId: number): Promise<CloudSyncResponse> {
    return request.post(`/cloud-sync/travel-plan/${planId}`)
  },

  /**
   * 同步单个费用到云端
   */
  syncExpense(expenseId: number): Promise<CloudSyncResponse> {
    return request.post(`/cloud-sync/expense/${expenseId}`)
  },

  /**
   * 从云端获取所有行程
   */
  getCloudTravelPlans(): Promise<CloudSyncResponse<any[]>> {
    return request.get('/cloud-sync/travel-plans')
  },

  /**
   * 从云端获取所有费用
   */
  getCloudExpenses(travelPlanId?: number): Promise<CloudSyncResponse<any[]>> {
    const url = travelPlanId
      ? `/cloud-sync/expenses?travel_plan_id=${travelPlanId}`
      : '/cloud-sync/expenses'
    return request.get(url)
  },

  /**
   * 从云端恢复数据
   */
  restoreFromCloud(): Promise<CloudSyncResponse<any>> {
    return request.post('/cloud-sync/restore')
  },

  /**
   * 清空云端数据（危险操作）
   */
  clearCloudData(confirm: boolean = false): Promise<CloudSyncResponse> {
    return request.post('/cloud-sync/clear-cloud', { confirm })
  }
}
