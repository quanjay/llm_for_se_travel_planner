<template>
  <div class="expense-voice-recorder">
    <el-button
      :type="isRecording ? 'danger' : 'primary'"
      :loading="isProcessing"
      @click="toggleRecording"
      :disabled="!isSupported || isProcessing"
      :circle="!showText"
      :size="size"
      :class="{ 'record-button': !showText }"
    >
      <el-icon v-if="!isRecording && !isProcessing">
        <Microphone />
      </el-icon>
      <el-icon v-else-if="isRecording">
        <VideoPause />
      </el-icon>
      <template v-if="showText">
        {{ isRecording ? '停止录音' : '语音记录' }}
      </template>
    </el-button>

    <div v-if="showInfo" class="recorder-info">
      <template v-if="!isSupported">
        <el-text type="danger" size="small">浏览器不支持录音</el-text>
      </template>
      <template v-else-if="isRecording">
        <el-text type="primary" size="small">
          <el-icon class="recording-icon"><VideoCamera /></el-icon>
          录音中 {{ recordingTime }}s
        </el-text>
      </template>
      <template v-else-if="isProcessing">
        <el-text type="info" size="small">识别中...</el-text>
      </template>
      <template v-else>
        <el-text type="info" size="small">{{ placeholder }}</el-text>
      </template>
    </div>

    <!-- 录音波形 -->
    <div v-if="isRecording && showWaveform" class="waveform">
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

interface Props {
  size?: 'large' | 'default' | 'small'
  showText?: boolean
  showInfo?: boolean
  showWaveform?: boolean
  placeholder?: string
}

withDefaults(defineProps<Props>(), {
  size: 'default',
  showText: false,
  showInfo: true,
  showWaveform: true,
  placeholder: '说出费用，如："刚在餐厅花了200元"'
})

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

onMounted(async () => {
  isSupported.value = !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia)
  
  if (!isSupported.value) {
    console.warn('浏览器不支持语音录制')
  }
})

onUnmounted(() => {
  stopRecording()
})

const toggleRecording = async () => {
  if (isRecording.value) {
    await stopRecording()
  } else {
    await startRecording()
  }
}

const startRecording = async () => {
  try {
    stream = await navigator.mediaDevices.getUserMedia({ 
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        sampleRate: 16000
      } 
    })
    
    const options = { mimeType: 'audio/webm' }
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
    
    recordingInterval = window.setInterval(() => {
      recordingTime.value++
      if (recordingTime.value >= 30) {
        stopRecording()
        ElMessage.warning('录音时间已达上限，自动停止')
      }
    }, 1000)
    
  } catch (error: any) {
    console.error('启动录音失败:', error)
    if (error.name === 'NotAllowedError') {
      ElMessage.error('请允许使用麦克风权限')
    } else {
      ElMessage.error('启动录音失败')
    }
    emit('error', error.message)
  }
}

const stopRecording = async () => {
  if (mediaRecorder && isRecording.value) {
    mediaRecorder.stop()
    isRecording.value = false
    
    if (recordingInterval) {
      clearInterval(recordingInterval)
      recordingInterval = null
    }
    
    if (stream) {
      stream.getTracks().forEach(track => track.stop())
      stream = null
    }
  }
}

const processAudio = async (audioBlob: Blob) => {
  if (audioBlob.size === 0) {
    ElMessage.warning('未录制到音频，请重试')
    return
  }
  
  isProcessing.value = true
  
  try {
    // 转换为 WAV 格式（科大讯飞要求）
    console.log(`原始音频: ${audioBlob.type}, 大小: ${audioBlob.size} bytes`)
    const wavBlob = await convertToWav(audioBlob)
    console.log(`转换后音频: ${wavBlob.type}, 大小: ${wavBlob.size} bytes`)
    
    const response = await voiceApi.recognizeExpense(wavBlob)
    
    if (response.code === 200 && response.data.text) {
      const expense = response.data.expense
      
      if (expense.amount) {
        ElMessage.success(`识别成功: ${expense.description || '费用'} ${expense.amount}元`)
        emit('recognized', response.data)
      } else {
        ElMessage.warning('未识别到金额，请重新录音')
      }
    } else {
      ElMessage.warning('未识别到有效内容，请重新录音')
    }
    
  } catch (error: any) {
    console.error('费用语音识别失败:', error)
    ElMessage.error('识别失败: ' + (error.message || error.detail || '未知错误'))
    emit('error', error.message || '识别失败')
  } finally {
    isProcessing.value = false
  }
}
</script>

<style scoped>
.expense-voice-recorder {
  display: inline-flex;
  align-items: center;
  gap: 12px;
}

.record-button {
  transition: all 0.3s;
}

.record-button:hover:not(:disabled) {
  transform: scale(1.05);
}

.record-button.is-danger {
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(245, 108, 108, 0.7);
  }
  50% {
    box-shadow: 0 0 0 6px rgba(245, 108, 108, 0);
  }
}

.recorder-info {
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
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
  display: inline-flex;
  align-items: center;
  gap: 3px;
  height: 24px;
}

.wave-bar {
  width: 2px;
  height: 8px;
  background: linear-gradient(to top, #409EFF, #79bbff);
  border-radius: 1px;
  animation: wave 1s ease-in-out infinite;
}

.wave-bar:nth-child(1) { animation-delay: 0s; }
.wave-bar:nth-child(2) { animation-delay: 0.1s; }
.wave-bar:nth-child(3) { animation-delay: 0.2s; }
.wave-bar:nth-child(4) { animation-delay: 0.3s; }
.wave-bar:nth-child(5) { animation-delay: 0.4s; }

@keyframes wave {
  0%, 100% { height: 8px; }
  50% { height: 20px; }
}
</style>
