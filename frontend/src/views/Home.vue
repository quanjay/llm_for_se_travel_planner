<template>
  <div class="home">
    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 欢迎区域 -->
      <div class="hero-section">
        <h1 class="hero-title">智能旅行规划，让出行更简单</h1>
        <p class="hero-subtitle">通过AI技术为您规划个性化的旅行路线，管理预算，记录美好时光</p>
        
        <!-- 快速开始按钮 -->
        <div class="hero-actions">
          <el-button 
            type="primary" 
            size="large" 
            @click="startPlanning"
            :loading="loading"
          >
            <el-icon><Plus /></el-icon>
            开始规划行程
          </el-button>
        </div>
      </div>

      <!-- 功能特性 -->
      <div class="features-section">
        <h2 class="section-title">核心功能</h2>
        <el-row :gutter="24">
          <el-col :xs="24" :sm="12" :md="8">
            <el-card class="feature-card" shadow="hover">
              <div class="feature-icon">
                <el-icon size="40" color="#409EFF"><Location /></el-icon>
              </div>
              <h3>智能行程规划</h3>
              <p>AI根据您的偏好自动生成个性化行程，包含景点、餐厅、住宿等详细安排</p>
            </el-card>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8">
            <el-card class="feature-card" shadow="hover">
              <div class="feature-icon">
                <el-icon size="40" color="#67C23A"><Money /></el-icon>
              </div>
              <h3>预算管理</h3>
              <p>智能预算分析和费用跟踪，帮您合理规划旅行开支，控制成本</p>
            </el-card>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8">
            <el-card class="feature-card" shadow="hover">
              <div class="feature-icon">
                <el-icon size="40" color="#E6A23C"><Upload /></el-icon>
              </div>
              <h3>云端同步</h3>
              <p>所有数据云端保存，支持多设备同步访问，随时随地查看您的行程</p>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 热门目的地 -->
      <div class="popular-destinations">
        <h2 class="section-title">热门目的地</h2>
        <el-row :gutter="16">
          <el-col v-for="destination in popularDestinations" :key="destination.name" :xs="12" :sm="8" :md="6">
            <el-card class="destination-card" shadow="hover" @click="quickPlan(destination.name)">
              <img 
                :src="destination.image" 
                :alt="destination.name" 
                class="destination-image"
                @error="handleImageError"
              >
              <div class="destination-info">
                <h4>{{ destination.name }}</h4>
                <p>{{ destination.description }}</p>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  Plus, 
  Location, 
  Money, 
  Upload
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)

// 热门目的地数据
const popularDestinations = ref([
  {
    name: '东京',
    description: '现代与传统的完美融合',
    image: 'https://picsum.photos/300/200?random=1'
  },
  {
    name: '巴黎',
    description: '浪漫之都，艺术天堂',
    image: 'https://picsum.photos/300/200?random=2'
  },
  {
    name: '纽约',
    description: '不夜城，梦想之地',
    image: 'https://picsum.photos/300/200?random=3'
  },
  {
    name: '伦敦',
    description: '历史悠久的国际大都市',
    image: 'https://picsum.photos/300/200?random=4'
  }
])

// 开始规划行程
const startPlanning = () => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录后再开始规划行程')
    router.push('/login')
    return
  }
  router.push('/planning')
}

// 快速规划特定目的地
const quickPlan = (destination: string) => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录后再开始规划行程')
    router.push('/login')
    return
  }
  // 跳转到规划页面，并传递目的地参数
  router.push({
    path: '/planning',
    query: { destination }
  })
}

// 图片加载错误处理
const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  // 使用一个占位图片或者设置默认背景
  img.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDMwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIzMDAiIGhlaWdodD0iMjAwIiBmaWxsPSIjRjVGN0ZBIi8+CjxwYXRoIGQ9Ik0xMzAgMTAwSDEyMFY5MEgxMzBWMTAwWk0xNTAgMTAwSDE0MFY5MEgxNTBWMTAwWk0xNzAgMTAwSDE2MFY5MEgxNzBWMTAwWiIgZmlsbD0iIzlDQTNBRiIvPgo8L3N2Zz4K'
}


</script>

<style scoped>
.home {
  min-height: 100vh;
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.hero-section {
  text-align: center;
  padding: 80px 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  margin: 0 -20px 60px -20px;
}

.hero-title {
  font-size: 48px;
  font-weight: 600;
  margin-bottom: 16px;
  line-height: 1.2;
}

.hero-subtitle {
  font-size: 20px;
  margin-bottom: 40px;
  opacity: 0.9;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.hero-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.section-title {
  text-align: center;
  margin-bottom: 40px;
  font-size: 32px;
  color: #2c3e50;
}

.features-section {
  margin-bottom: 80px;
}

.feature-card {
  text-align: center;
  padding: 20px;
  height: 100%;
  transition: transform 0.2s;
  margin-bottom: 24px;
}

.feature-card:hover {
  transform: translateY(-4px);
}

.feature-icon {
  margin-bottom: 20px;
}

.feature-card h3 {
  margin-bottom: 16px;
  color: #2c3e50;
}

.feature-card p {
  color: #606266;
  line-height: 1.6;
}

.popular-destinations {
  margin-bottom: 80px;
}

.destination-card {
  cursor: pointer;
  transition: transform 0.2s;
  margin-bottom: 16px;
  overflow: hidden;
}

.destination-card:hover {
  transform: translateY(-2px);
}

.destination-image {
  width: 100%;
  height: 120px;
  object-fit: cover;
}

.destination-info {
  padding: 16px;
}

.destination-info h4 {
  margin-bottom: 8px;
  color: #2c3e50;
}

.destination-info p {
  color: #909399;
  font-size: 12px;
  margin: 0;
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 32px;
  }
  
  .hero-subtitle {
    font-size: 16px;
  }
  
  .section-title {
    font-size: 24px;
  }
}
</style>