<template>
  <div class="voice-recorder">
    <el-button
      :type="isRecording ? 'danger' : 'primary'"
      :loading="isProcessing"
      @click="toggleRecording"
      :disabled="!isSupported || isProcessing"
      circle
      size="large"
      class="record-button"
    >
      <el-icon v-if="!isRecording && !isProcessing" :size="24">
        <Microphone />
      </el-icon>
      <el-icon v-else-if="isRecording" :size="24">
        <VideoPause />
      </el-icon>
    </el-button>

    <div class="recorder-info">
      <template v-if="!isSupported">
        <el-text type="danger" size="small">您的浏览器不支持语音录制</el-text>
      </template>
      <template v-else-if="isRecording">
        <el-text type="primary" size="small">
          <el-icon class="recording-icon"><VideoCamera /></el-icon>
          录音中... {{ recordingTime }}s
        </el-text>
      </template>
      <template v-else-if="isProcessing">
        <el-text type="info" size="small">识别中...</el-text>
      </template>
      <template v-else>
        <el-text type="info" size="small">点击开始语音输入</el-text>
      </template>
    </div>

    <!-- 录音波形动画 -->
    <div v-if="isRecording" class="waveform">
      <span v-for="i in 5" :key="i" class="wave-bar"></span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Microphone, VideoPause, VideoCamera } from '@element-plus/icons-vue'
import { voiceApi } from '@/api/voice'
import { convertToWav } from '@/utils/audioConverter'

const emit = defineEmits<{
  (e: 'recognized', result: any): void
  (e: 'error', error: string): void
}>()

const isSupported = ref(false)
const isRecording = ref(false)
const isProcessing = ref(false)
const recordingTime = ref(0)

let mediaRecorder: MediaRecorder | null = null
let audioChunks: Blob[] = []
let recordingInterval: number | null = null
let stream: MediaStream | null = null

// 检查浏览器支持
onMounted(async () => {
  isSupported.value = !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia)
  
  if (!isSupported.value) {
    ElMessage.warning('您的浏览器不支持语音录制功能')
  }
  
  // 检查语音服务状态
  try {
    const response = await voiceApi.checkStatus()
    if (!response.data.available) {
      ElMessage.warning('语音识别服务未配置，请联系管理员')
    }
  } catch (error) {
    console.error('检查语音服务状态失败:', error)
  }
})

onUnmounted(() => {
  stopRecording()
})

// 开始/停止录音
const toggleRecording = async () => {
  if (isRecording.value) {
    await stopRecording()
  } else {
    await startRecording()
  }
}

// 开始录音
const startRecording = async () => {
  try {
    // 请求麦克风权限
    stream = await navigator.mediaDevices.getUserMedia({ 
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        sampleRate: 16000
      } 
    })
    
    // 创建 MediaRecorder
    const options = { mimeType: 'audio/webm' }
    
    // 检查浏览器支持的 MIME 类型
    if (!MediaRecorder.isTypeSupported(options.mimeType)) {
      options.mimeType = 'audio/ogg'
      if (!MediaRecorder.isTypeSupported(options.mimeType)) {
        options.mimeType = ''
      }
    }
    
    mediaRecorder = new MediaRecorder(stream, options.mimeType ? options : undefined)
    audioChunks = []
    
    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.push(event.data)
      }
    }
    
    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(audioChunks, { type: mediaRecorder?.mimeType || 'audio/webm' })
      await processAudio(audioBlob)
    }
    
    mediaRecorder.start()
    isRecording.value = true
    recordingTime.value = 0
    
    // 开始计时
    recordingInterval = window.setInterval(() => {
      recordingTime.value++
      
      // 最长录音60秒
      if (recordingTime.value >= 60) {
        stopRecording()
        ElMessage.warning('录音时间已达上限，自动停止')
      }
    }, 1000)
    
    ElMessage.success('开始录音')
    
  } catch (error: any) {
    console.error('启动录音失败:', error)
    if (error.name === 'NotAllowedError') {
      ElMessage.error('请允许使用麦克风权限')
    } else {
      ElMessage.error('启动录音失败: ' + error.message)
    }
    emit('error', error.message)
  }
}

// 停止录音
const stopRecording = async () => {
  if (mediaRecorder && isRecording.value) {
    mediaRecorder.stop()
    isRecording.value = false
    
    if (recordingInterval) {
      clearInterval(recordingInterval)
      recordingInterval = null
    }
    
    // 关闭媒体流
    if (stream) {
      stream.getTracks().forEach(track => track.stop())
      stream = null
    }
  }
}

// 处理音频
const processAudio = async (audioBlob: Blob) => {
  if (audioBlob.size === 0) {
    ElMessage.warning('未录制到音频，请重试')
    return
  }
  
  isProcessing.value = true
  
  try {
    // 转换为 WAV 格式（科大讯飞要求）
    console.log(`原始音频: ${audioBlob.type}, 大小: ${audioBlob.size} bytes`)
    const processedBlob = await convertToWav(audioBlob)
    console.log(`转换后音频: ${processedBlob.type}, 大小: ${processedBlob.size} bytes`)
    
    // 调用识别接口
    const response = await voiceApi.recognizeAudio(processedBlob)
    
    if (response.code === 200 && response.data.text) {
      ElMessage.success('识别成功: ' + response.data.text)
      emit('recognized', response.data)
    } else {
      ElMessage.warning('未识别到有效内容，请重新录音')
    }
    
  } catch (error: any) {
    console.error('语音识别失败:', error)
    ElMessage.error('语音识别失败: ' + (error.message || error.detail || '未知错误'))
    emit('error', error.message || '识别失败')
  } finally {
    isProcessing.value = false
  }
}
</script>

<style scoped>
.voice-recorder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 20px;
}

.record-button {
  width: 64px;
  height: 64px;
  font-size: 24px;
  transition: all 0.3s;
}

.record-button:hover:not(:disabled) {
  transform: scale(1.1);
}

.record-button.is-danger {
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(245, 108, 108, 0.7);
  }
  50% {
    box-shadow: 0 0 0 10px rgba(245, 108, 108, 0);
  }
}

.recorder-info {
  min-height: 24px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.recording-icon {
  color: #f56c6c;
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 50%, 100% {
    opacity: 1;
  }
  25%, 75% {
    opacity: 0.3;
  }
}

.waveform {
  display: flex;
  align-items: center;
  gap: 4px;
  height: 30px;
}

.wave-bar {
  width: 3px;
  height: 10px;
  background: linear-gradient(to top, #409EFF, #79bbff);
  border-radius: 2px;
  animation: wave 1s ease-in-out infinite;
}

.wave-bar:nth-child(1) {
  animation-delay: 0s;
}

.wave-bar:nth-child(2) {
  animation-delay: 0.1s;
}

.wave-bar:nth-child(3) {
  animation-delay: 0.2s;
}

.wave-bar:nth-child(4) {
  animation-delay: 0.3s;
}

.wave-bar:nth-child(5) {
  animation-delay: 0.4s;
}

@keyframes wave {
  0%, 100% {
    height: 10px;
  }
  50% {
    height: 25px;
  }
}
</style>
