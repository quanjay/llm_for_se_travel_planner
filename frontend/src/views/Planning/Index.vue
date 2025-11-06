<template>
  <div class="planning-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>行程规划</h1>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        新建行程
      </el-button>
    </div>

    <!-- 行程列表 -->
    <div class="travel-plans-list">
      <el-row :gutter="20">
        <el-col 
          v-for="plan in travelPlans" 
          :key="plan.id" 
          :xs="24" 
          :sm="12" 
          :md="8" 
          :lg="6"
        >
          <el-card class="travel-plan-card" shadow="hover">
            <div class="plan-header">
              <h3>{{ plan.title }}</h3>
              <el-tag :type="getStatusTagType(plan.status)">
                {{ getStatusText(plan.status) }}
              </el-tag>
            </div>
            
            <div class="plan-details">
              <p class="destination">
                <el-icon><MapLocation /></el-icon>
                {{ plan.destination }}
              </p>
              <p class="date-range">
                <el-icon><Calendar /></el-icon>
                {{ formatDateRange(plan.start_date, plan.end_date) }}
              </p>
              <p class="budget">
                <el-icon><Money /></el-icon>
                预算: ¥{{ plan.budget }}
              </p>
              <p class="people">
                <el-icon><User /></el-icon>
                {{ plan.people_count }}人
              </p>
            </div>

            <div class="plan-actions">
              <el-button type="text" @click="viewPlan(plan.id)">查看详情</el-button>
              <el-button type="text" @click="editPlan(plan)">编辑</el-button>
              <el-button type="text" class="danger" @click="deletePlan(plan.id)">删除</el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 空状态 -->
      <el-empty v-if="travelPlans.length === 0" description="暂无行程计划">
        <el-button type="primary" @click="showCreateDialog = true">创建第一个行程</el-button>
      </el-empty>
    </div>

    <!-- 创建/编辑行程对话框 -->
    <el-dialog 
      :title="editingPlan ? '编辑行程' : '创建新行程'"
      v-model="showCreateDialog"
      width="600px"
      :close-on-click-modal="false"
    >
      <!-- 语音输入选项卡 -->
      <el-tabs v-model="inputMode" class="input-tabs">
        <el-tab-pane label="文字输入" name="text">
          <!-- 表单输入 -->
        </el-tab-pane>
        <el-tab-pane label="语音输入" name="voice">
          <div class="voice-input-container">
            <el-alert
              title="语音输入提示"
              type="info"
              :closable="false"
              show-icon
            >
              请描述您的旅行计划，例如："我想去北京玩5天，预算5000元，2个人，喜欢美食和文化"
            </el-alert>
            <VoiceRecorder @recognized="handleVoiceRecognized" @error="handleVoiceError" />
            <div v-if="voiceRecognizedText" class="recognized-text">
              <el-text type="success">
                <el-icon><Check /></el-icon>
                识别结果: {{ voiceRecognizedText }}
              </el-text>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>

      <el-form
        ref="planFormRef"
        :model="planForm"
        :rules="planFormRules"
        label-width="80px"
      >
        <el-form-item label="行程名称" prop="title">
          <el-input v-model="planForm.title" placeholder="请输入行程名称" />
        </el-form-item>

        <el-form-item label="目的地" prop="destination">
          <el-input v-model="planForm.destination" placeholder="请输入目的地" />
        </el-form-item>

        <el-form-item label="出行日期" prop="dateRange">
          <el-date-picker
            v-model="planForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="预算" prop="budget">
          <el-input-number
            v-model="planForm.budget"
            :min="0"
            :precision="0"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="出行人数" prop="people_count">
          <el-input-number
            v-model="planForm.people_count"
            :min="1"
            :max="20"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="偏好标签">
          <el-checkbox-group v-model="planForm.preferences">
            <el-checkbox label="美食">美食</el-checkbox>
            <el-checkbox label="购物">购物</el-checkbox>
            <el-checkbox label="文化">文化</el-checkbox>
            <el-checkbox label="自然风光">自然风光</el-checkbox>
            <el-checkbox label="亲子">亲子</el-checkbox>
            <el-checkbox label="商务">商务</el-checkbox>
            <el-checkbox label="休闲">休闲</el-checkbox>
            <el-checkbox label="冒险">冒险</el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-form-item label="特殊需求">
          <el-input
            v-model="planForm.special_requirements"
            type="textarea"
            :rows="3"
            placeholder="请描述特殊需求，如无障碍设施、素食要求等"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCreateDialog = false">取消</el-button>
          <el-button @click="createPlan" :loading="creating">手动创建</el-button>
          <el-button type="primary" @click="generateAIPlan" :loading="generating">
            {{ generating ? 'AI正在生成中...' : 'AI生成行程' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { 
  Plus, 
  MapLocation, 
  Calendar, 
  Money, 
  User,
  Check
} from '@element-plus/icons-vue'
import { travelPlanApi } from '@/api/travel-plan'
import type { TravelPlan } from '@/types'
import VoiceRecorder from '@/components/VoiceRecorder.vue'

const router = useRouter()
const route = useRoute()

// 响应式数据
const travelPlans = ref<TravelPlan[]>([])
const showCreateDialog = ref(false)
const editingPlan = ref<TravelPlan | null>(null)
const creating = ref(false)
const generating = ref(false)
const planFormRef = ref<FormInstance>()
const inputMode = ref<'text' | 'voice'>('text')
const voiceRecognizedText = ref('')

// 表单数据
const planForm = reactive({
  title: '',
  destination: '',
  dateRange: [] as string[],
  budget: 5000,
  people_count: 1,
  preferences: [] as string[],
  special_requirements: ''
})

// 表单验证规则
const planFormRules: FormRules = {
  title: [
    { required: true, message: '请输入行程名称', trigger: 'blur' }
  ],
  destination: [
    { required: true, message: '请输入目的地', trigger: 'blur' }
  ],
  dateRange: [
    { required: true, message: '请选择出行日期', trigger: 'change' }
  ],
  budget: [
    { required: true, message: '请输入预算', trigger: 'blur' }
  ],
  people_count: [
    { required: true, message: '请输入出行人数', trigger: 'blur' }
  ]
}

// 获取行程列表
const fetchTravelPlans = async () => {
  try {
    const response = await travelPlanApi.getTravelPlans()
    travelPlans.value = response.data
  } catch (error: any) {
    ElMessage.error(error.message || '获取行程列表失败')
  }
}

// 创建行程
const createPlan = async () => {
  if (!planFormRef.value) return

  try {
    await planFormRef.value.validate()
    creating.value = true

    const toIsoDate = (d: string) => {
      if (!d) return d
      return d.includes('T') ? d : `${d}T00:00:00Z`
    }

    const planData = {
      title: planForm.title,
      destination: planForm.destination,
      start_date: toIsoDate(planForm.dateRange[0]),
      end_date: toIsoDate(planForm.dateRange[1]),
      budget: planForm.budget,
      people_count: planForm.people_count,
      preferences: planForm.preferences
    }

    if (editingPlan.value) {
      await travelPlanApi.updateTravelPlan(editingPlan.value.id, planData)
      ElMessage.success('行程更新成功')
    } else {
      await travelPlanApi.createTravelPlan(planData)
      ElMessage.success('行程创建成功')
    }

    showCreateDialog.value = false
    resetForm()
    fetchTravelPlans()

  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  } finally {
    creating.value = false
  }
}

// AI生成行程
const generateAIPlan = async () => {
  if (!planFormRef.value) return

  try {
    await planFormRef.value.validate()
    generating.value = true

    // 显示详细的进度提示
    const loadingMessage = ElMessage({
      message: '正在调用AI生成行程，请耐心等待（可能需要1-3分钟）...',
      type: 'info',
      duration: 0, // 不自动关闭
      showClose: true
    })

    const toIsoDate = (d: string) => {
      if (!d) return d
      return d.includes('T') ? d : `${d}T00:00:00Z`
    }

    const requestData = {
      destination: planForm.destination,
      start_date: toIsoDate(planForm.dateRange[0]),
      end_date: toIsoDate(planForm.dateRange[1]),
      budget: planForm.budget,
      people_count: planForm.people_count,
      preferences: planForm.preferences,
      special_requirements: planForm.special_requirements
    }

    const response = await travelPlanApi.generateTravelPlan(requestData)
    
    // 关闭加载消息
    loadingMessage.close()
    
    // 检查是否使用了 AI 生成
    if (response.data && 'ai_generated' in response.data && !response.data.ai_generated) {
      ElMessage.warning('AI服务暂时不可用，已为您生成默认行程模板，建议手动调整')
    } else {
      ElMessage.success('AI行程生成成功！')
    }
    
    showCreateDialog.value = false
    resetForm()
    fetchTravelPlans()

  } catch (error: any) {
    // 关闭可能还存在的加载消息
    ElMessage.closeAll()
    
    if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      ElMessage.error('请求超时，AI服务可能繁忙，请稍后重试')
    } else if (error.message?.includes('网络')) {
      ElMessage.error('网络连接失败，请检查网络后重试')
    } else {
      ElMessage.error(error.message || 'AI生成失败，请重试')
    }
  } finally {
    generating.value = false
  }
}

// 查看行程详情
const viewPlan = (planId: number) => {
  router.push(`/planning/${planId}`)
}

// 编辑行程
const editPlan = (plan: TravelPlan) => {
  editingPlan.value = plan
  planForm.title = plan.title
  planForm.destination = plan.destination
  planForm.dateRange = [plan.start_date, plan.end_date]
  planForm.budget = Number(plan.budget)
  planForm.people_count = plan.people_count
  planForm.preferences = plan.preferences || []
  showCreateDialog.value = true
}

// 删除行程
const deletePlan = async (planId: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个行程吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await travelPlanApi.deleteTravelPlan(planId)
    ElMessage.success('行程删除成功')
    fetchTravelPlans()

  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// 处理语音识别结果
const handleVoiceRecognized = (result: any) => {
  voiceRecognizedText.value = result.text
  const intent = result.intent
  
  // 自动填充表单
  if (intent.destination) {
    planForm.destination = intent.destination
  }
  
  if (intent.budget) {
    planForm.budget = intent.budget
  }
  
  if (intent.people_count) {
    planForm.people_count = intent.people_count
  }
  
  if (intent.preferences && intent.preferences.length > 0) {
    planForm.preferences = intent.preferences
  }
  
  // 如果识别到天数，计算日期范围
  if (intent.days) {
    const today = new Date()
    const endDate = new Date(today)
    endDate.setDate(today.getDate() + intent.days - 1)
    
    planForm.dateRange = [
      today.toISOString().split('T')[0],
      endDate.toISOString().split('T')[0]
    ]
  }
  
  // 自动生成标题
  if (intent.destination) {
    const days = intent.days ? `${intent.days}天` : ''
    planForm.title = `${intent.destination}${days}之旅`
  }
  
  // 切换到文字输入标签页，让用户确认
  inputMode.value = 'text'
  
  ElMessage.success('已自动填充表单，请确认信息')
}

// 处理语音识别错误
const handleVoiceError = (error: string) => {
  console.error('语音识别错误:', error)
}

// 重置表单
const resetForm = () => {
  editingPlan.value = null
  planForm.title = ''
  planForm.destination = ''
  planForm.dateRange = []
  planForm.budget = 5000
  planForm.people_count = 1
  planForm.preferences = []
  planForm.special_requirements = ''
  voiceRecognizedText.value = ''
  inputMode.value = 'text'
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

// 页面加载时获取数据
onMounted(() => {
  fetchTravelPlans()
  
  // 如果URL中有destination参数，自动填充目的地
  if (route.query.destination) {
    planForm.destination = route.query.destination as string
    showCreateDialog.value = true
  }
})
</script>

<style scoped>
.planning-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0;
  color: #2c3e50;
}

.travel-plans-list {
  min-height: 400px;
}

.travel-plan-card {
  margin-bottom: 20px;
  transition: transform 0.2s;
}

.travel-plan-card:hover {
  transform: translateY(-2px);
}

.plan-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.plan-header h3 {
  margin: 0;
  color: #2c3e50;
}

.plan-details p {
  margin: 8px 0;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #606266;
  font-size: 14px;
}

.plan-actions {
  margin-top: 16px;
  display: flex;
  gap: 8px;
}

.danger:hover {
  color: #f56c6c !important;
}

.dialog-footer {
  display: flex;
  gap: 12px;
}

.input-tabs {
  margin-bottom: 20px;
}

.voice-input-container {
  padding: 20px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.recognized-text {
  padding: 12px;
  background: #f0f9ff;
  border-radius: 4px;
  width: 100%;
  text-align: center;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .plan-actions {
    flex-direction: column;
  }
}
</style>