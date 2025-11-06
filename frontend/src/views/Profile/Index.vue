<template>
  <div class="profile-container">
    <el-row :gutter="20">
      <!-- 用户信息卡片 -->
      <el-col :xs="24" :md="8">
        <el-card class="user-info-card">
          <div class="user-header">
            <el-avatar :size="80" :src="userStore.user?.avatar">
              {{ userStore.user?.username?.charAt(0) }}
            </el-avatar>
            <h2>{{ userStore.user?.username }}</h2>
            <p class="user-email">{{ userStore.user?.email }}</p>
          </div>
          
          <div class="user-stats">
            <div class="stat-item">
              <div class="stat-number">{{ userStats.totalPlans }}</div>
              <div class="stat-label">总行程</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">{{ userStats.completedPlans }}</div>
              <div class="stat-label">已完成</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">¥{{ userStats.totalSpent }}</div>
              <div class="stat-label">总支出</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <!-- 个人信息编辑 -->
      <el-col :xs="24" :md="16">
        <el-card class="profile-form-card">
          <div class="card-header">
            <h3>个人信息</h3>
            <el-button 
              v-if="!editing" 
              type="primary" 
              @click="startEdit"
            >
              编辑信息
            </el-button>
          </div>
          
          <el-form
            ref="profileFormRef"
            :model="profileForm"
            :rules="profileFormRules"
            label-width="100px"
            :disabled="!editing"
          >
            <el-form-item label="用户名" prop="username">
              <el-input v-model="profileForm.username" />
            </el-form-item>
            
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="profileForm.email" disabled />
            </el-form-item>
            
            <el-form-item label="手机号" prop="phone">
              <el-input v-model="profileForm.phone" />
            </el-form-item>
            
            <el-form-item v-if="editing">
              <el-button @click="cancelEdit">取消</el-button>
              <el-button type="primary" @click="saveProfile" :loading="saving">
                保存
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
        
        <!-- 修改密码 -->
        <el-card class="password-card" style="margin-top: 20px;">
          <div class="card-header">
            <h3>修改密码</h3>
          </div>
          
          <el-form
            ref="passwordFormRef"
            :model="passwordForm"
            :rules="passwordFormRules"
            label-width="100px"
          >
            <el-form-item label="当前密码" prop="currentPassword">
              <el-input
                v-model="passwordForm.currentPassword"
                type="password"
                show-password
              />
            </el-form-item>
            
            <el-form-item label="新密码" prop="newPassword">
              <el-input
                v-model="passwordForm.newPassword"
                type="password"
                show-password
              />
            </el-form-item>
            
            <el-form-item label="确认密码" prop="confirmPassword">
              <el-input
                v-model="passwordForm.confirmPassword"
                type="password"
                show-password
              />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="changePassword" :loading="changingPassword">
                修改密码
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { authApi } from '@/api/auth'
import { travelPlanApi } from '@/api/travel-plan'
import { expenseApi } from '@/api/expense'

const userStore = useUserStore()

// 响应式数据
const editing = ref(false)
const saving = ref(false)
const changingPassword = ref(false)
const profileFormRef = ref<FormInstance>()
const passwordFormRef = ref<FormInstance>()

// 用户统计信息
const userStats = reactive({
  totalPlans: 0,
  completedPlans: 0,
  totalSpent: 0
})

// 个人信息表单
const profileForm = reactive({
  username: '',
  email: '',
  phone: ''
})

// 密码修改表单
const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 表单验证规则
const profileFormRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 20, message: '用户名长度在2-20个字符', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ]
}

const validateConfirmPassword = (_rule: any, value: string, callback: any) => {
  if (value !== passwordForm.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const passwordFormRules: FormRules = {
  currentPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

// 获取用户统计信息
const fetchUserStats = async () => {
  try {
    // 获取行程统计
    const plansResponse = await travelPlanApi.getTravelPlans()
    const plans = plansResponse.data
    userStats.totalPlans = plans.length
    userStats.completedPlans = plans.filter(plan => plan.status === 'completed').length
    
    // 获取费用统计
    const expenseResponse = await expenseApi.getUserExpensesSummary()
    userStats.totalSpent = expenseResponse.data.total_amount || 0
    
  } catch (error: any) {
    console.error('获取用户统计失败:', error)
  }
}

// 开始编辑
const startEdit = () => {
  editing.value = true
  // 填充当前用户信息
  if (userStore.user) {
    profileForm.username = userStore.user.username
    profileForm.email = userStore.user.email
    profileForm.phone = userStore.user.phone || ''
  }
}

// 取消编辑
const cancelEdit = () => {
  editing.value = false
  // 重置表单
  profileForm.username = ''
  profileForm.email = ''
  profileForm.phone = ''
}

// 保存个人信息
const saveProfile = async () => {
  if (!profileFormRef.value) return
  
  try {
    await profileFormRef.value.validate()
    saving.value = true
    
    // 这里应该调用更新用户信息的API
    // 暂时模拟成功
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 更新用户store中的信息
    if (userStore.user) {
      userStore.user.username = profileForm.username
      userStore.user.phone = profileForm.phone
    }
    
    ElMessage.success('个人信息更新成功')
    editing.value = false
    
  } catch (error: any) {
    ElMessage.error(error.message || '更新失败')
  } finally {
    saving.value = false
  }
}

// 修改密码
const changePassword = async () => {
  if (!passwordFormRef.value) return
  
  try {
    await passwordFormRef.value.validate()
    changingPassword.value = true
    
    await authApi.changePassword({
      old_password: passwordForm.currentPassword,
      new_password: passwordForm.newPassword
    })
    
    ElMessage.success('密码修改成功')
    
    // 重置表单
    passwordForm.currentPassword = ''
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
    
  } catch (error: any) {
    ElMessage.error(error.message || '密码修改失败')
  } finally {
    changingPassword.value = false
  }
}

// 页面加载
onMounted(() => {
  fetchUserStats()
})
</script>

<style scoped>
.profile-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.user-info-card {
  text-align: center;
}

.user-header {
  padding: 20px 0;
}

.user-header h2 {
  margin: 16px 0 8px 0;
  color: #2c3e50;
}

.user-email {
  color: #909399;
  margin: 0;
}

.user-stats {
  display: flex;
  justify-content: space-around;
  padding: 20px 0;
  border-top: 1px solid #ebeef5;
  margin-top: 20px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.profile-form-card,
.password-card {
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

@media (max-width: 768px) {
  .user-stats {
    flex-direction: column;
    gap: 16px;
  }
  
  .card-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
}
</style>