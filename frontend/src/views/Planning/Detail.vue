<template>
  <div class="detail-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <el-button @click="$router.back()" circle>
        <el-icon><ArrowLeft /></el-icon>
      </el-button>
      <h1 v-if="travelPlan">{{ travelPlan.title }}</h1>
      <div class="header-actions">
        <el-button v-if="travelPlan" @click="editPlan">编辑行程</el-button>
        <el-button v-if="travelPlan" type="primary" @click="$router.push(`/expenses?plan=${travelPlan.id}`)">
          费用管理
        </el-button>
      </div>
    </div>

    <!-- 地图导航 -->
    <el-card v-if="travelPlan && travelPlan.itinerary && travelPlan.itinerary.length > 0" class="map-card">
      <div class="card-header clickable" @click="toggleMapExpanded">
        <div class="header-left">
          <el-icon class="collapse-icon" :class="{ 'is-expanded': isMapExpanded }">
            <ArrowDown />
          </el-icon>
          <h3>地图导航</h3>
          <el-tag type="info">{{ getAllLocationsCount() }} 个地点</el-tag>
        </div>
        <el-button 
          text 
          @click.stop="toggleMapExpanded"
          style="color: #409EFF;"
        >
          {{ isMapExpanded ? '收起' : '展开' }}
        </el-button>
      </div>
      <el-collapse-transition>
        <div v-show="isMapExpanded" class="map-container">
          <TravelMap 
            ref="travelMapRef"
            :itinerary="travelPlan.itinerary" 
            :destination="travelPlan.destination" 
          />
        </div>
      </el-collapse-transition>
    </el-card>

    <!-- 行程信息 -->
    <el-row v-if="travelPlan" :gutter="20" style="margin-top: 20px;">
      <!-- 基本信息 -->
      <el-col :xs="24" :md="8">
        <el-card class="info-card">
          <div class="card-header">
            <h3>行程信息</h3>
            <el-tag :type="getStatusTagType(travelPlan.status)">
              {{ getStatusText(travelPlan.status) }}
            </el-tag>
          </div>
          
          <div class="info-item">
            <label>目的地:</label>
            <span>{{ travelPlan.destination }}</span>
          </div>
          
          <div class="info-item">
            <label>出行时间:</label>
            <span>{{ formatDateRange(travelPlan.start_date, travelPlan.end_date) }}</span>
          </div>
          
          <div class="info-item">
            <label>出行天数:</label>
            <span>{{ getDayCount(travelPlan.start_date, travelPlan.end_date) }}天</span>
          </div>
          
          <div class="info-item">
            <label>出行人数:</label>
            <span>{{ travelPlan.people_count }}人</span>
          </div>
          
          <div class="info-item">
            <label>预算:</label>
            <span>¥{{ travelPlan.budget }}</span>
          </div>
          
          <div class="info-item">
            <label>已支出:</label>
            <span>¥{{ travelPlan.total_cost || 0 }}</span>
          </div>
          
          <div class="info-item" v-if="travelPlan.preferences && travelPlan.preferences.length > 0">
            <label>偏好:</label>
            <div class="preferences">
              <el-tag 
                v-for="preference in travelPlan.preferences" 
                :key="preference"
                size="small"
                style="margin-right: 8px; margin-bottom: 4px;"
              >
                {{ preference }}
              </el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <!-- 行程安排 -->
      <el-col :xs="24" :md="16">
        <el-card class="itinerary-card">
          <div class="card-header">
            <h3>行程安排</h3>
            <el-button v-if="!travelPlan.itinerary || travelPlan.itinerary.length === 0" type="primary" @click="generateItinerary">
              生成行程
            </el-button>
          </div>
          
          <!-- 有行程安排时显示 -->
          <div v-if="travelPlan.itinerary && travelPlan.itinerary.length > 0" class="itinerary-content">
            <el-timeline>
              <el-timeline-item
                v-for="day in travelPlan.itinerary"
                :key="day.day"
                :timestamp="`第${day.day}天 (${day.date})`"
                placement="top"
              >
                <el-card class="day-card">
                  <div class="day-summary">
                    <h4>第{{ day.day }}天行程</h4>
                    <span class="day-cost">当日预算: ¥{{ day.total_cost || 0 }}</span>
                  </div>
                  
                  <div class="activities">
                    <div 
                      v-for="(activity, index) in day.activities" 
                      :key="index"
                      class="activity-item"
                      :class="{ 'has-location': activity.location }"
                      @click="activity.location ? navigateToLocation(day, index) : null"
                    >
                      <div class="activity-icon">
                        <el-icon :color="getActivityColor(activity.type)">
                          <component :is="getActivityIcon(activity.type)" />
                        </el-icon>
                      </div>
                      
                      <div class="activity-content">
                        <div class="activity-header">
                          <h5>{{ activity.name }}</h5>
                          <div class="activity-header-right">
                            <span class="activity-time">{{ activity.start_time }} - {{ activity.end_time }}</span>
                            <el-tooltip v-if="activity.location" content="点击在地图上查看" placement="top">
                              <el-icon class="nav-icon"><MapLocation /></el-icon>
                            </el-tooltip>
                          </div>
                        </div>
                        
                        <p class="activity-description">{{ activity.description }}</p>
                        
                        <div class="activity-details">
                          <span class="activity-location">
                            <el-icon><MapLocation /></el-icon>
                            {{ activity.location }}
                          </span>
                          <span class="activity-cost">¥{{ activity.cost }}</span>
                          <span v-if="activity.rating" class="activity-rating">
                            <el-rate v-model="activity.rating" disabled show-score size="small" />
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </el-card>
              </el-timeline-item>
            </el-timeline>
          </div>
          
          <!-- 无行程安排时显示 -->
          <el-empty v-else description="暂无行程安排">
            <el-button type="primary" @click="generateItinerary">AI生成行程</el-button>
          </el-empty>
        </el-card>
      </el-col>
    </el-row>

    <!-- 加载状态 -->
    <div v-else-if="loading" class="loading">
      <el-skeleton :rows="6" animated />
    </div>

    <!-- 错误状态 -->
    <el-result v-else icon="warning" title="行程不存在" sub-title="请检查行程ID是否正确">
      <template #extra>
        <el-button type="primary" @click="$router.push('/planning')">返回行程列表</el-button>
      </template>
    </el-result>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  ArrowLeft,
  ArrowDown,
  MapLocation, 
  Van, 
  House, 
  Shop, 
  Camera,
  ShoppingBag,
  More 
} from '@element-plus/icons-vue'
import { travelPlanApi } from '@/api/travel-plan'
import type { TravelPlan } from '@/types'
import TravelMap from '@/components/TravelMap.vue'

const route = useRoute()
const router = useRouter()

// 响应式数据
const travelPlan = ref<TravelPlan | null>(null)
const loading = ref(true)
const isMapExpanded = ref(false)  // 地图默认收起
const travelMapRef = ref<InstanceType<typeof TravelMap> | null>(null)  // 地图组件引用

// 获取行程详情
const fetchTravelPlan = async () => {
  try {
    const planId = Number(route.params.id)
    if (!planId) {
      throw new Error('无效的行程ID')
    }
    
    const response = await travelPlanApi.getTravelPlan(planId)
    travelPlan.value = response.data
    
  } catch (error: any) {
    ElMessage.error(error.message || '获取行程详情失败')
  } finally {
    loading.value = false
  }
}

// 生成行程
const generateItinerary = async () => {
  if (!travelPlan.value) return
  
  try {
    ElMessage.info('正在生成行程，请稍候...')
    
    const response = await travelPlanApi.generateTravelPlan({
      destination: travelPlan.value.destination,
      start_date: travelPlan.value.start_date,
      end_date: travelPlan.value.end_date,
      budget: Number(travelPlan.value.budget),
      people_count: travelPlan.value.people_count,
      preferences: travelPlan.value.preferences || []
    })
    
    travelPlan.value = response.data
    ElMessage.success('行程生成成功！')
    
  } catch (error: any) {
    ElMessage.error(error.message || '生成行程失败')
  }
}

// 编辑行程
const editPlan = () => {
  router.push('/planning?edit=' + travelPlan.value?.id)
}

// 获取状态标签类型
const getStatusTagType = (status: string) => {
  const typeMap: Record<string, string> = {
    draft: 'info',
    published: 'success',
    completed: 'warning'
  }
  return typeMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    draft: '草稿',
    published: '已发布',
    completed: '已完成'
  }
  return textMap[status] || '未知'
}

// 格式化日期范围
const formatDateRange = (startDate: string, endDate: string) => {
  const start = new Date(startDate).toLocaleDateString()
  const end = new Date(endDate).toLocaleDateString()
  return `${start} - ${end}`
}

// 计算天数
const getDayCount = (startDate: string, endDate: string) => {
  const start = new Date(startDate)
  const end = new Date(endDate)
  return Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24)) + 1
}

// 获取活动图标
const getActivityIcon = (type: string) => {
  const iconMap: Record<string, any> = {
    transport: Van,
    hotel: House,
    restaurant: Shop,
    attraction: Camera,
    shopping: ShoppingBag,
    other: More
  }
  return iconMap[type] || More
}

// 获取活动颜色
const getActivityColor = (type: string) => {
  const colorMap: Record<string, string> = {
    transport: '#409EFF',
    hotel: '#67C23A',
    restaurant: '#E6A23C',
    attraction: '#F56C6C',
    shopping: '#909399',
    other: '#606266'
  }
  return colorMap[type] || '#606266'
}

// 切换地图展开/收起
const toggleMapExpanded = () => {
  isMapExpanded.value = !isMapExpanded.value
}

// 导航到地图上的位置
const navigateToLocation = async (day: any, activityIndex: number) => {
  if (!travelPlan.value?.itinerary) return
  
  // 计算全局位置索引（跨天）
  let globalIndex = 0
  for (let i = 0; i < travelPlan.value.itinerary.length; i++) {
    const currentDay = travelPlan.value.itinerary[i]
    if (currentDay.day === day.day) {
      globalIndex += activityIndex
      break
    }
    globalIndex += currentDay.activities?.length || 0
  }
  
  // 展开地图
  if (!isMapExpanded.value) {
    isMapExpanded.value = true
    // 等待地图渲染
    await new Promise(resolve => setTimeout(resolve, 300))
  }
  
  // 滚动到地图位置
  const mapCard = document.querySelector('.map-card')
  if (mapCard) {
    mapCard.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
  
  // 调用地图组件的聚焦方法
  if (travelMapRef.value && typeof travelMapRef.value.focusLocation === 'function') {
    await new Promise(resolve => setTimeout(resolve, 400))
    travelMapRef.value.focusLocation(globalIndex)
  }
}

// 获取所有地点数量
const getAllLocationsCount = () => {
  if (!travelPlan.value || !travelPlan.value.itinerary) return 0
  
  let count = 0
  travelPlan.value.itinerary.forEach(day => {
    if (day.activities && Array.isArray(day.activities)) {
      count += day.activities.length
    }
  })
  
  return count
}

// 页面加载
onMounted(() => {
  fetchTravelPlan()
})
</script>

<style scoped>
.detail-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.page-header h1 {
  flex: 1;
  margin: 0;
  color: #2c3e50;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.map-card {
  margin-bottom: 20px;
}

.map-card .card-header {
  margin-bottom: 0;
  cursor: pointer;
  user-select: none;
  transition: background-color 0.3s;
  padding: 8px;
  margin: -8px;
  border-radius: 4px;
}

.map-card .card-header:hover {
  background-color: #f5f7fa;
}

.map-card .card-header.clickable {
  cursor: pointer;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.collapse-icon {
  transition: transform 0.3s;
  color: #409EFF;
}

.collapse-icon.is-expanded {
  transform: rotate(180deg);
}

.map-container {
  margin-top: 20px;
  height: 450px;
  border-radius: 4px;
  overflow: hidden;
}

.info-card,
.itinerary-card {
  height: fit-content;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.card-header h3 {
  margin: 0;
  color: #2c3e50;
}

.info-item {
  display: flex;
  margin-bottom: 12px;
  align-items: flex-start;
}

.info-item label {
  width: 80px;
  color: #909399;
  font-size: 14px;
  flex-shrink: 0;
}

.info-item span {
  color: #2c3e50;
  font-size: 14px;
}

.preferences {
  flex: 1;
}

.itinerary-content {
  margin-top: 20px;
}

.day-card {
  margin-bottom: 16px;
}

.day-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.day-summary h4 {
  margin: 0;
  color: #2c3e50;
}

.day-cost {
  color: #67C23A;
  font-weight: bold;
}

.activities {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  background: #f9f9f9;
  border-radius: 8px;
  transition: all 0.3s;
}

.activity-item.has-location {
  cursor: pointer;
}

.activity-item.has-location:hover {
  background: #e6f7ff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
  transform: translateX(4px);
}

.activity-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 50%;
  flex-shrink: 0;
}

.activity-content {
  flex: 1;
}

.activity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.activity-header h5 {
  margin: 0;
  color: #2c3e50;
  flex: 1;
}

.activity-header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.activity-time {
  color: #909399;
  font-size: 12px;
}

.nav-icon {
  color: #409EFF;
  font-size: 16px;
  transition: transform 0.3s;
}

.activity-item.has-location:hover .nav-icon {
  transform: scale(1.2);
}

.activity-description {
  color: #606266;
  font-size: 14px;
  margin-bottom: 8px;
  line-height: 1.4;
}

.activity-details {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 12px;
}

.activity-location {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #909399;
}

.activity-cost {
  color: #E6A23C;
  font-weight: bold;
}

.loading {
  padding: 40px;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .header-actions {
    justify-content: center;
  }
  
  .activity-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
  
  .activity-details {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>