<template>
  <div class="expenses-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>费用管理</h1>
      <div class="header-actions">
        <el-select 
          v-model="selectedTravelPlan" 
          placeholder="选择行程"
          @change="onTravelPlanChange"
          style="width: 200px; margin-right: 12px;"
        >
          <el-option
            v-for="plan in travelPlans"
            :key="plan.id"
            :label="plan.title"
            :value="plan.id"
          />
        </el-select>
        <el-button 
          type="primary" 
          @click="showAddExpenseDialog = true"
          :disabled="!selectedTravelPlan"
        >
          <el-icon><Plus /></el-icon>
          添加费用
        </el-button>
      </div>
    </div>

    <!-- 预算分析卡片 -->
    <div class="budget-overview" v-if="budgetAnalysis">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-value">¥{{ budgetAnalysis.total_budget }}</div>
              <div class="stat-label">总预算</div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-value">¥{{ budgetAnalysis.total_spent }}</div>
              <div class="stat-label">已支出</div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-value">¥{{ budgetAnalysis.remaining }}</div>
              <div class="stat-label">剩余预算</div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-value">{{ budgetAnalysis.percentage_used.toFixed(1) }}%</div>
              <div class="stat-label">预算使用率</div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 预算进度条 -->
      <el-card class="progress-card" style="margin-top: 20px;">
        <div class="progress-header">
          <h3>预算使用情况</h3>
        </div>
        <el-progress
          :percentage="budgetAnalysis.percentage_used"
          :color="getProgressColor(budgetAnalysis.percentage_used)"
          :stroke-width="12"
          :show-text="false"
        />
        <div class="progress-text">
          已使用 {{ budgetAnalysis.percentage_used.toFixed(1) }}% 
          (¥{{ budgetAnalysis.total_spent }} / ¥{{ budgetAnalysis.total_budget }})
        </div>
      </el-card>
    </div>

    <!-- 费用列表 -->
    <el-card class="expenses-list-card" v-if="selectedTravelPlan">
      <div class="card-header">
        <h3>费用记录</h3>
        <div class="filters">
          <el-select 
            v-model="categoryFilter" 
            placeholder="筛选类别"
            clearable
            @change="fetchExpenses"
            style="width: 150px;"
          >
            <el-option label="交通" value="transport" />
            <el-option label="住宿" value="accommodation" />
            <el-option label="餐饮" value="food" />
            <el-option label="景点" value="attraction" />
            <el-option label="购物" value="shopping" />
            <el-option label="其他" value="other" />
          </el-select>
        </div>
      </div>

      <el-table :data="expenses" style="width: 100%">
        <el-table-column prop="date" label="日期" width="120">
          <template #default="{ row }">
            {{ formatDate(row.expense_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="category" label="类别" width="100">
          <template #default="{ row }">
            <el-tag :type="getCategoryTagType(row.category)">
              {{ getCategoryText(row.category) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" />
        <el-table-column prop="amount" label="金额" width="120" align="right">
          <template #default="{ row }">
            <span class="amount">¥{{ row.amount }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button type="text" @click="editExpense(row)">编辑</el-button>
            <el-button type="text" class="danger" @click="deleteExpense(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 空状态 -->
      <el-empty v-if="expenses.length === 0" description="暂无费用记录">
        <el-button type="primary" @click="showAddExpenseDialog = true">添加第一条费用记录</el-button>
      </el-empty>
    </el-card>

    <!-- 未选择行程提示 -->
    <el-empty v-else description="请先选择一个行程来管理费用">
      <el-button type="primary" @click="$router.push('/planning')">去创建行程</el-button>
    </el-empty>

    <!-- 添加/编辑费用对话框 -->
    <el-dialog
      :title="editingExpense ? '编辑费用' : '添加费用'"
      v-model="showAddExpenseDialog"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="expenseFormRef"
        :model="expenseForm"
        :rules="expenseFormRules"
        label-width="80px"
      >
        <el-form-item label="类别" prop="category">
          <el-select v-model="expenseForm.category" placeholder="请选择费用类别">
            <el-option label="交通" value="transport" />
            <el-option label="住宿" value="accommodation" />
            <el-option label="餐饮" value="food" />
            <el-option label="景点" value="attraction" />
            <el-option label="购物" value="shopping" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>

        <el-form-item label="金额" prop="amount">
          <el-input-number
            v-model="expenseForm.amount"
            :min="0"
            :precision="2"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input
            v-model="expenseForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入费用描述"
          />
        </el-form-item>

        <el-form-item label="日期" prop="expense_date">
          <el-date-picker
            v-model="expenseForm.expense_date"
            type="datetime"
            placeholder="选择费用发生时间"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAddExpenseDialog = false">取消</el-button>
          <el-button type="primary" @click="saveExpense" :loading="saving">
            {{ editingExpense ? '更新' : '添加' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { travelPlanApi } from '@/api/travel-plan'
import { expenseApi } from '@/api/expense'
import type { TravelPlan, Expense, BudgetAnalysis } from '@/types'

// 响应式数据
const travelPlans = ref<TravelPlan[]>([])
const selectedTravelPlan = ref<number | null>(null)
const expenses = ref<Expense[]>([])
const budgetAnalysis = ref<BudgetAnalysis | null>(null)
const showAddExpenseDialog = ref(false)
const editingExpense = ref<Expense | null>(null)
const categoryFilter = ref('')
const saving = ref(false)
const expenseFormRef = ref<FormInstance>()

// 表单数据
const expenseForm = reactive({
  category: '' as Expense['category'] | '',
  amount: 0,
  description: '',
  expense_date: ''
})

// 表单验证规则
const expenseFormRules: FormRules = {
  category: [
    { required: true, message: '请选择费用类别', trigger: 'change' }
  ],
  amount: [
    { required: true, message: '请输入金额', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入费用描述', trigger: 'blur' }
  ],
  expense_date: [
    { required: true, message: '请选择费用发生时间', trigger: 'change' }
  ]
}

// 获取行程列表
const fetchTravelPlans = async () => {
  try {
    const response = await travelPlanApi.getTravelPlans()
    travelPlans.value = response.data
    
    // 自动选择第一个行程
    if (travelPlans.value.length > 0 && !selectedTravelPlan.value) {
      selectedTravelPlan.value = travelPlans.value[0].id
      onTravelPlanChange()
    }
  } catch (error: any) {
    ElMessage.error(error.message || '获取行程列表失败')
  }
}

// 行程切换
const onTravelPlanChange = () => {
  if (selectedTravelPlan.value) {
    fetchExpenses()
    fetchBudgetAnalysis()
  }
}

// 获取费用列表
const fetchExpenses = async () => {
  if (!selectedTravelPlan.value) return

  try {
    const response = await expenseApi.getExpensesByTravelPlan(
      selectedTravelPlan.value,
      categoryFilter.value || undefined
    )
    expenses.value = response.data
  } catch (error: any) {
    ElMessage.error(error.message || '获取费用记录失败')
  }
}

// 获取预算分析
const fetchBudgetAnalysis = async () => {
  if (!selectedTravelPlan.value) return

  try {
    const response = await expenseApi.getBudgetAnalysis(selectedTravelPlan.value)
    budgetAnalysis.value = response.data
  } catch (error: any) {
    ElMessage.error(error.message || '获取预算分析失败')
  }
}

// 保存费用
const saveExpense = async () => {
  if (!expenseFormRef.value || !selectedTravelPlan.value) return

  try {
    await expenseFormRef.value.validate()
    saving.value = true

    const expenseData = {
      category: expenseForm.category as Expense['category'],
      amount: expenseForm.amount,
      description: expenseForm.description,
      expense_date: expenseForm.expense_date,
      travel_plan_id: selectedTravelPlan.value
    }

    if (editingExpense.value) {
      await expenseApi.updateExpense(editingExpense.value.id, expenseData)
      ElMessage.success('费用更新成功')
    } else {
      await expenseApi.createExpense(expenseData)
      ElMessage.success('费用添加成功')
    }

    showAddExpenseDialog.value = false
    resetForm()
    fetchExpenses()
    fetchBudgetAnalysis()

  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  } finally {
    saving.value = false
  }
}

// 编辑费用
const editExpense = (expense: Expense) => {
  editingExpense.value = expense
  expenseForm.category = expense.category
  expenseForm.amount = Number(expense.amount)
  expenseForm.description = expense.description
  expenseForm.expense_date = expense.expense_date
  showAddExpenseDialog.value = true
}

// 删除费用
const deleteExpense = async (expenseId: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这条费用记录吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await expenseApi.deleteExpense(expenseId)
    ElMessage.success('费用删除成功')
    fetchExpenses()
    fetchBudgetAnalysis()

  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// 重置表单
const resetForm = () => {
  editingExpense.value = null
  expenseForm.category = ''
  expenseForm.amount = 0
  expenseForm.description = ''
  expenseForm.expense_date = ''
}

// 获取类别标签类型
const getCategoryTagType = (category: string) => {
  const typeMap: Record<string, string> = {
    transport: 'primary',
    accommodation: 'success',
    food: 'warning',
    attraction: 'info',
    shopping: 'danger',
    other: ''
  }
  return typeMap[category] || ''
}

// 获取类别文本
const getCategoryText = (category: string) => {
  const textMap: Record<string, string> = {
    transport: '交通',
    accommodation: '住宿',
    food: '餐饮',
    attraction: '景点',
    shopping: '购物',
    other: '其他'
  }
  return textMap[category] || category
}

// 格式化日期
const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString()
}

// 获取进度条颜色
const getProgressColor = (percentage: number) => {
  if (percentage < 50) return '#67c23a'
  if (percentage < 80) return '#e6a23c'
  return '#f56c6c'
}

// 页面加载
onMounted(() => {
  fetchTravelPlans()
})
</script>

<style scoped>
.expenses-container {
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

.header-actions {
  display: flex;
  align-items: center;
}

.budget-overview {
  margin-bottom: 24px;
}

.stat-card {
  text-align: center;
  margin-bottom: 16px;
}

.stat-content {
  padding: 10px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 4px;
}

.stat-label {
  color: #909399;
  font-size: 14px;
}

.progress-card {
  padding: 20px;
}

.progress-header {
  margin-bottom: 16px;
}

.progress-header h3 {
  margin: 0;
  color: #2c3e50;
}

.progress-text {
  text-align: center;
  margin-top: 8px;
  color: #606266;
  font-size: 14px;
}

.expenses-list-card {
  margin-top: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.card-header h3 {
  margin: 0;
  color: #2c3e50;
}

.amount {
  font-weight: bold;
  color: #2c3e50;
}

.danger:hover {
  color: #f56c6c !important;
}

.dialog-footer {
  display: flex;
  gap: 12px;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .header-actions {
    flex-direction: column;
    gap: 12px;
  }
  
  .card-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
}
</style>