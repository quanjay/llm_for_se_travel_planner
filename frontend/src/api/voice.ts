import api from './request'
import type { ApiResponse } from '@/types'

export interface VoiceRecognitionResult {
  text: string
  intent: {
    destination: string | null
    days: number | null
    budget: number | null
    people_count: number
    preferences: string[]
    raw_text: string
  }
}

export interface VoiceServiceStatus {
  available: boolean
  provider: string
  message: string
}

export interface ExpenseRecognitionResult {
  text: string
  expense: {
    amount: number | null
    category: string | null
    description: string | null
    expense_date: string
    raw_text: string
  }
}

export const voiceApi = {
  // 语音识别（行程规划）
  recognizeAudio: (audioBlob: Blob, language: string = 'zh_cn'): Promise<ApiResponse<VoiceRecognitionResult>> => {
    const formData = new FormData()
    formData.append('audio', audioBlob, 'recording.wav')
    formData.append('language', language)
    
    return api.post('/voice/recognize', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 30000 // 30秒超时
    })
  },

  // 费用记录语音识别
  recognizeExpense: (audioBlob: Blob, language: string = 'zh_cn'): Promise<ApiResponse<ExpenseRecognitionResult>> => {
    const formData = new FormData()
    formData.append('audio', audioBlob, 'recording.wav')
    formData.append('language', language)
    
    return api.post('/voice/recognize-expense', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 30000
    })
  },

  // 解析旅行意图
  parseIntent: (text: string): Promise<ApiResponse<any>> => {
    return api.post('/voice/parse-intent', null, {
      params: { text }
    })
  },

  // 解析费用意图
  parseExpense: (text: string): Promise<ApiResponse<any>> => {
    return api.post('/voice/parse-expense', null, {
      params: { text }
    })
  },

  // 检查语音服务状态
  checkStatus: (): Promise<ApiResponse<VoiceServiceStatus>> => {
    return api.get('/voice/status')
  }
}
