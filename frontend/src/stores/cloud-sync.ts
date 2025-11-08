/**
 * 云端同步状态管理 Store
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { cloudSyncApi } from '@/api/cloud-sync'
import { ElMessage } from 'element-plus'

export const useCloudSyncStore = defineStore('cloud-sync', () => {
  // 状态
  const enabled = ref(false)
  const syncing = ref(false)
  const lastSyncTime = ref<string | null>(null)
  const syncStats = ref({
    plans_count: 0,
    expenses_count: 0,
    total_items: 0
  })

  // 计算属性
  const syncStatus = computed(() => {
    return `${syncStats.value.plans_count} 个行程，${syncStats.value.expenses_count} 个费用`
  })

  const hasSynced = computed(() => {
    return !!lastSyncTime.value
  })

  // 方法
  
  /**
   * 获取同步状态
   */
  async function getSyncStatus() {
    try {
      const response = await cloudSyncApi.getStatus()
      if (response.data) {
        const data = response.data
        enabled.value = data.enabled
        syncStats.value = {
          plans_count: data.plans_count || 0,
          expenses_count: data.expenses_count || 0,
          total_items: data.total_items || 0
        }
        return data
      }
    } catch (error: any) {
      console.error('获取同步状态失败:', error)
      enabled.value = false
      return null
    }
  }

  /**
   * 一键同步所有数据
   */
  async function syncAllData() {
    if (!enabled.value) {
      ElMessage.warning('云端同步未启用')
      return false
    }

    syncing.value = true
    try {
      const response = await cloudSyncApi.syncAllData()
      if (response.data?.success || response.code === 200) {
        lastSyncTime.value = new Date().toISOString()
        await getSyncStatus()
        ElMessage.success(`✅ 同步成功！${response.data?.total_synced || 0} 条数据已上传`)
        return true
      } else {
        ElMessage.error('同步失败: ' + response.message)
        return false
      }
    } catch (error: any) {
      console.error('同步所有数据失败:', error)
      ElMessage.error('同步失败: ' + (error.message || error.detail || '未知错误'))
      return false
    } finally {
      syncing.value = false
    }
  }

  /**
   * 同步单个行程
   */
  async function syncTravelPlan(planId: number) {
    if (!enabled.value) {
      return false
    }

    try {
      const response = await cloudSyncApi.syncTravelPlan(planId)
      if (response.data?.synced || response.code === 200) {
        lastSyncTime.value = new Date().toISOString()
        return true
      }
      return false
    } catch (error: any) {
      console.error('同步行程失败:', error)
      return false
    }
  }

  /**
   * 同步单个费用
   */
  async function syncExpense(expenseId: number) {
    if (!enabled.value) {
      return false
    }

    try {
      const response = await cloudSyncApi.syncExpense(expenseId)
      if (response.data?.synced || response.code === 200) {
        lastSyncTime.value = new Date().toISOString()
        return true
      }
      return false
    } catch (error: any) {
      console.error('同步费用失败:', error)
      return false
    }
  }

  /**
   * 从云端获取所有行程
   */
  async function getCloudTravelPlans() {
    if (!enabled.value) {
      return []
    }

    try {
      const response = await cloudSyncApi.getCloudTravelPlans()
      return response.data || []
    } catch (error: any) {
      console.error('获取云端行程失败:', error)
      return []
    }
  }

  /**
   * 从云端获取所有费用
   */
  async function getCloudExpenses(travelPlanId?: number) {
    if (!enabled.value) {
      return []
    }

    try {
      const response = await cloudSyncApi.getCloudExpenses(travelPlanId)
      return response.data || []
    } catch (error: any) {
      console.error('获取云端费用失败:', error)
      return []
    }
  }

  /**
   * 从云端恢复数据
   */
  async function restoreFromCloud() {
    if (!enabled.value) {
      ElMessage.warning('云端同步未启用')
      return null
    }

    syncing.value = true
    try {
      const response = await cloudSyncApi.restoreFromCloud()
      if (response.code === 200) {
        ElMessage.success('✅ 数据恢复成功')
        await getSyncStatus()
        return response.data
      } else {
        ElMessage.error('数据恢复失败')
        return null
      }
    } catch (error: any) {
      console.error('恢复数据失败:', error)
      ElMessage.error('恢复失败: ' + (error.message || error.detail))
      return null
    } finally {
      syncing.value = false
    }
  }

  /**
   * 清空云端数据
   */
  async function clearCloudData(confirm: boolean = false) {
    if (!enabled.value) {
      ElMessage.warning('云端同步未启用')
      return false
    }

    if (!confirm) {
      ElMessage.warning('请确认此危险操作')
      return false
    }

    try {
      const response = await cloudSyncApi.clearCloudData(true)
      if (response.code === 200) {
        ElMessage.success('✅ 云端数据已清空')
        await getSyncStatus()
        return true
      } else {
        ElMessage.error('清空失败')
        return false
      }
    } catch (error: any) {
      console.error('清空云端数据失败:', error)
      ElMessage.error('清空失败: ' + (error.message || error.detail))
      return false
    }
  }

  return {
    // 状态
    enabled,
    syncing,
    lastSyncTime,
    syncStats,
    // 计算属性
    syncStatus,
    hasSynced,
    // 方法
    getSyncStatus,
    syncAllData,
    syncTravelPlan,
    syncExpense,
    getCloudTravelPlans,
    getCloudExpenses,
    restoreFromCloud,
    clearCloudData
  }
})
