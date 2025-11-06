<template>
  <el-container class="app-layout">
    <!-- 顶部导航栏 -->
    <el-header class="app-header">
      <div class="header-content">
        <div class="logo" @click="$router.push('/')">
          <h2>AI旅行规划师</h2>
        </div>
        
        <!-- 导航菜单 -->
        <el-menu
          v-if="userStore.isLoggedIn"
          :default-active="activeIndex"
          class="app-menu"
          mode="horizontal"
          :ellipsis="false"
          @select="handleMenuSelect"
        >
          <el-menu-item index="/planning">
            <el-icon><MapLocation /></el-icon>
            <span>行程规划</span>
          </el-menu-item>
          <el-menu-item index="/expenses">
            <el-icon><Money /></el-icon>
            <span>费用管理</span>
          </el-menu-item>
        </el-menu>
        
        <!-- 用户区域 -->
        <div class="user-area">
          <template v-if="userStore.isLoggedIn">
            <el-dropdown trigger="click" @command="handleUserCommand">
              <span class="user-info">
                <el-avatar :size="32" :src="userStore.user?.avatar">
                  {{ userStore.user?.username?.charAt(0) }}
                </el-avatar>
                <span class="username">{{ userStore.user?.username }}</span>
                <el-icon><ArrowDown /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">
                    <el-icon><User /></el-icon>
                    个人中心
                  </el-dropdown-item>
                  <el-dropdown-item divided command="logout">
                    <el-icon><SwitchButton /></el-icon>
                    退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
          <template v-else>
            <el-button @click="$router.push('/login')">登录</el-button>
            <el-button type="primary" @click="$router.push('/register')">注册</el-button>
          </template>
        </div>
      </div>
    </el-header>

    <!-- 主要内容区域 -->
    <el-main class="app-main">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  MapLocation, 
  Money, 
  User, 
  ArrowDown, 
  SwitchButton 
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// 当前活跃的菜单项
const activeIndex = computed(() => {
  return route.path
})

// 处理菜单选择
const handleMenuSelect = (index: string) => {
  router.push(index)
}

// 处理用户下拉菜单命令
const handleUserCommand = (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'logout':
      userStore.logout()
      ElMessage.success('已成功退出登录')
      router.push('/')
      break
  }
}
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
}

.app-header {
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 0;
  line-height: 60px;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 20px;
}

.logo {
  cursor: pointer;
  transition: color 0.2s;
}

.logo:hover {
  color: #409EFF;
}

.logo h2 {
  color: #409EFF;
  margin: 0;
  font-size: 20px;
}

.app-menu {
  flex: 1;
  margin: 0 40px;
  border-bottom: none;
}

.app-menu .el-menu-item {
  border-bottom: 2px solid transparent;
}

.app-menu .el-menu-item.is-active {
  border-bottom-color: #409EFF;
  color: #409EFF;
}

.user-area {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 6px;
  transition: background-color 0.2s;
}

.user-info:hover {
  background-color: #f5f7fa;
}

.username {
  font-size: 14px;
  color: #606266;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.app-main {
  padding: 0;
  background: #f5f5f5;
  min-height: calc(100vh - 60px);
}

/* 页面切换动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    padding: 0 16px;
  }
  
  .app-menu {
    margin: 0 20px;
  }
  
  .logo h2 {
    font-size: 18px;
  }
  
  .username {
    display: none;
  }
}

@media (max-width: 480px) {
  .app-menu {
    display: none;
  }
  
  .user-area .el-button span {
    display: none;
  }
}
</style>