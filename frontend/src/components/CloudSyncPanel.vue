<template>
  <div class="cloud-sync-panel">
    <!-- 同步状态卡片 -->
    <el-card class="sync-status-card">
      <div class="card-header">
        <div class="header-left">
          <el-icon v-if="cloudSyncStore.enabled" class="status-icon enabled">
            <SuccessFilled />
          </el-icon>
          <el-icon v-else class="status-icon disabled">
            <CircleCloseFilled />
          </el-icon>
          <div>
            <h3>云端同步</h3>
            <p v-if="cloudSyncStore.enabled" class="status-text">
              ✅ 已启用 • {{ cloudSyncStore.syncStatus }}
            </p>
            <p v-else class="status-text">⚠️ 已禁用</p>
          </div>
        </div>
        <el-button 
          type="primary" 
          @click="handleSync"
          :loading="cloudSyncStore.syncing"
          :disabled="!cloudSyncStore.enabled"
        >
          <el-icon><Upload /></el-icon>
          立即同步
        </el-button>
      </div>

      <!-- 同步信息 -->
      <div v-if="cloudSyncStore.enabled" class="sync-info">
        <el-row :gutter="20">
          <el-col :xs="12" :sm="6">
            <div class="info-item">
              <div class="info-label">行程</div>
              <div class="info-value">{{ cloudSyncStore.syncStats.plans_count }}</div>
            </div>
          </el-col>
          <el-col :xs="12" :sm="6">
            <div class="info-item">
              <div class="info-label">费用</div>
              <div class="info-value">{{ cloudSyncStore.syncStats.expenses_count }}</div>
            </div>
          </el-col>
          <el-col :xs="12" :sm="12">
            <div class="info-item">
              <div class="info-label">上次同步</div>
              <div class="info-value">{{ lastSyncText }}</div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 操作按钮 -->
      <div v-if="cloudSyncStore.enabled" class="actions">
        <el-divider />
        <div class="button-group">
          <el-button 
            type="text" 
            @click="showRestoreDialog = true"
            :disabled="cloudSyncStore.syncStats.total_items === 0"
          >
            <el-icon><Download /></el-icon>
            从云端恢复
          </el-button>
          <el-button 
            type="text" 
            @click="showClearDialog = true"
            :disabled="cloudSyncStore.syncStats.total_items === 0"
          >
            <el-icon><Delete /></el-icon>
            清空云端数据
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 恢复确认对话框 -->
    <el-dialog 
      title="从云端恢复数据"
      v-model="showRestoreDialog"
      width="400px"
    >
      <p>此操作将从云端下载所有数据并与本地数据合并。</p>
      <p style="color: #f56c6c; margin-top: 10px;">
        ⚠️ 注意：本地数据将被云端版本覆盖。
      </p>
      <template #footer>
        <el-button @click="showRestoreDialog = false">取消</el-button>
        <el-button type="primary" @click="handleRestore" :loading="cloudSyncStore.syncing">
          确认恢复
        </el-button>
      </template>
    </el-dialog>

    <!-- 清空确认对话框 -->
    <el-dialog 
      title="清空云端数据"
      v-model="showClearDialog"
      width="400px"
    >
      <el-alert
        title="危险操作"
        type="error"
        :closable="false"
        show-icon
      >
        此操作将清空所有云端数据，无法撤销！
      </el-alert>
      <p style="margin-top: 16px;">
        请输入 <strong>确认删除</strong> 以确认此操作
      </p>
      <el-input 
        v-model="confirmText"
        placeholder="确认删除"
        @keyup.enter="handleClear"
      />
      <template #footer>
        <el-button @click="showClearDialog = false">取消</el-button>
        <el-button 
          type="danger" 
          @click="handleClear" 
          :disabled="confirmText !== '确认删除'"
          :loading="cloudSyncStore.syncing"
        >
          清空
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { 
  Upload, 
  Download, 
  Delete, 
  SuccessFilled, 
  CircleCloseFilled 
} from '@element-plus/icons-vue'
import { useCloudSyncStore } from '@/stores/cloud-sync'

const cloudSyncStore = useCloudSyncStore()
const showRestoreDialog = ref(false)
const showClearDialog = ref(false)
const confirmText = ref('')

const lastSyncText = computed(() => {
  if (!cloudSyncStore.lastSyncTime) {
    return '暂无'
  }
  const date = new Date(cloudSyncStore.lastSyncTime)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  if (diff < 60000) {
    return '刚刚'
  } else if (diff < 3600000) {
    return `${Math.floor(diff / 60000)} 分钟前`
  } else if (diff < 86400000) {
    return `${Math.floor(diff / 3600000)} 小时前`
  } else {
    return date.toLocaleDateString()
  }
})

onMounted(async () => {
  await cloudSyncStore.getSyncStatus()
})

const handleSync = async () => {
  await cloudSyncStore.syncAllData()
}

const handleRestore = async () => {
  const result = await cloudSyncStore.restoreFromCloud()
  if (result) {
    showRestoreDialog.value = false
  }
}

const handleClear = async () => {
  const success = await cloudSyncStore.clearCloudData(true)
  if (success) {
    showClearDialog.value = false
    confirmText.value = ''
  }
}
</script>

<style scoped>
.cloud-sync-panel {
  width: 100%;
}

.sync-status-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.status-icon {
  font-size: 24px;
}

.status-icon.enabled {
  color: #67c23a;
}

.status-icon.disabled {
  color: #f56c6c;
}

.header-left h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 16px;
}

.status-text {
  margin: 4px 0 0 0;
  color: #909399;
  font-size: 12px;
}

.sync-info {
  margin: 16px 0;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
}

.info-item {
  text-align: center;
}

.info-label {
  color: #909399;
  font-size: 12px;
  margin-bottom: 4px;
}

.info-value {
  color: #2c3e50;
  font-size: 20px;
  font-weight: bold;
}

.actions {
  margin-top: 16px;
}

.button-group {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .header-left {
    width: 100%;
  }

  .button-group {
    justify-content: flex-start;
  }
}
</style>
