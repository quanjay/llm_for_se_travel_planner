/**
 * 音频格式转换工具
 * 将 WebM/OGG 等格式转换为 WAV (PCM 16bit 16000Hz)
 */

/**
 * 将音频 Blob 转换为 WAV 格式
 * @param audioBlob 原始音频 Blob (WebM, OGG 等)
 * @returns WAV 格式的 Blob
 */
export async function convertToWav(audioBlob: Blob): Promise<Blob> {
  // 创建 AudioContext
  const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)({
    sampleRate: 16000 // 科大讯飞要求 16kHz 采样率
  })

  try {
    // 将 Blob 转换为 ArrayBuffer
    const arrayBuffer = await audioBlob.arrayBuffer()
    
    // 解码音频数据
    const audioBuffer = await audioContext.decodeAudioData(arrayBuffer)
    
    // 转换为 WAV 格式
    const wavBlob = audioBufferToWav(audioBuffer)
    
    return wavBlob
  } finally {
    // 关闭 AudioContext 释放资源
    await audioContext.close()
  }
}

/**
 * 将 AudioBuffer 转换为 WAV Blob
 */
function audioBufferToWav(audioBuffer: AudioBuffer): Blob {
  const numberOfChannels = 1 // 单声道
  const sampleRate = audioBuffer.sampleRate
  const bitDepth = 16
  
  // 获取音频数据（转为单声道）
  let audioData: Float32Array
  if (audioBuffer.numberOfChannels === 1) {
    audioData = audioBuffer.getChannelData(0)
  } else {
    // 多声道混音为单声道
    const left = audioBuffer.getChannelData(0)
    const right = audioBuffer.getChannelData(1)
    audioData = new Float32Array(left.length)
    for (let i = 0; i < left.length; i++) {
      audioData[i] = (left[i] + right[i]) / 2
    }
  }
  
  // 转换为 16bit PCM
  const pcmData = floatTo16BitPCM(audioData)
  
  // 创建 WAV 文件头
  const wavBuffer = createWavFile(pcmData, sampleRate, numberOfChannels, bitDepth)
  
  return new Blob([wavBuffer], { type: 'audio/wav' })
}

/**
 * 将 Float32Array 转换为 16bit PCM
 */
function floatTo16BitPCM(float32Array: Float32Array): Int16Array {
  const int16Array = new Int16Array(float32Array.length)
  for (let i = 0; i < float32Array.length; i++) {
    // 将 [-1, 1] 范围的浮点数转换为 [-32768, 32767] 范围的整数
    const s = Math.max(-1, Math.min(1, float32Array[i]))
    int16Array[i] = s < 0 ? s * 0x8000 : s * 0x7FFF
  }
  return int16Array
}

/**
 * 创建 WAV 文件
 */
function createWavFile(
  pcmData: Int16Array,
  sampleRate: number,
  numberOfChannels: number,
  bitDepth: number
): ArrayBuffer {
  const blockAlign = (numberOfChannels * bitDepth) / 8
  const byteRate = sampleRate * blockAlign
  const dataSize = pcmData.length * 2 // 16bit = 2 bytes
  
  const buffer = new ArrayBuffer(44 + dataSize)
  const view = new DataView(buffer)
  
  // RIFF 标识符
  writeString(view, 0, 'RIFF')
  // 文件大小
  view.setUint32(4, 36 + dataSize, true)
  // WAVE 标识符
  writeString(view, 8, 'WAVE')
  
  // fmt 子块
  writeString(view, 12, 'fmt ')
  view.setUint32(16, 16, true) // fmt 子块大小
  view.setUint16(20, 1, true) // 音频格式 (1 = PCM)
  view.setUint16(22, numberOfChannels, true) // 声道数
  view.setUint32(24, sampleRate, true) // 采样率
  view.setUint32(28, byteRate, true) // 字节率
  view.setUint16(32, blockAlign, true) // 块对齐
  view.setUint16(34, bitDepth, true) // 位深度
  
  // data 子块
  writeString(view, 36, 'data')
  view.setUint32(40, dataSize, true) // 数据大小
  
  // PCM 数据
  let offset = 44
  for (let i = 0; i < pcmData.length; i++) {
    view.setInt16(offset, pcmData[i], true)
    offset += 2
  }
  
  return buffer
}

/**
 * 在 DataView 中写入字符串
 */
function writeString(view: DataView, offset: number, string: string) {
  for (let i = 0; i < string.length; i++) {
    view.setUint8(offset + i, string.charCodeAt(i))
  }
}
