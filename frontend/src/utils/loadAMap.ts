/**
 * 高德地图动态加载工具
 * 从环境变量读取配置，动态加载高德地图 JS API
 */

let isLoading = false
let isLoaded = false

/**
 * 动态加载高德地图 JS API
 * @returns Promise<boolean> 加载成功返回 true
 */
export const loadAMap = (): Promise<boolean> => {
  return new Promise((resolve, reject) => {
    // 如果已经加载完成，直接返回
    if (isLoaded && window.AMap) {
      resolve(true)
      return
    }

    // 如果正在加载中，等待加载完成
    if (isLoading) {
      const checkInterval = setInterval(() => {
        if (isLoaded && window.AMap) {
          clearInterval(checkInterval)
          resolve(true)
        }
      }, 100)
      return
    }

    // 获取环境变量中的配置
    const amapKey = import.meta.env.VITE_AMAP_KEY
    const amapSecurityCode = import.meta.env.VITE_AMAP_SECURITY_CODE

    // 检查配置是否存在
    if (!amapKey || !amapSecurityCode) {
      const errorMsg = '高德地图配置未找到，请在 .env 文件中配置 VITE_AMAP_KEY 和 VITE_AMAP_SECURITY_CODE'
      console.error(errorMsg)
      reject(new Error(errorMsg))
      return
    }

    console.log('开始加载高德地图 JS API...')
    isLoading = true

    try {
      // 设置安全密钥
      window._AMapSecurityConfig = {
        securityJsCode: amapSecurityCode
      }

      // 动态创建 script 标签加载高德地图
      const script = document.createElement('script')
      script.type = 'text/javascript'
      script.src = `https://webapi.amap.com/maps?v=2.0&key=${amapKey}`
      
      script.onload = () => {
        isLoading = false
        isLoaded = true
        console.log('高德地图 JS API 加载成功')
        resolve(true)
      }

      script.onerror = (error) => {
        isLoading = false
        const errorMsg = '高德地图 JS API 加载失败，请检查网络连接和 API Key 配置'
        console.error(errorMsg, error)
        reject(new Error(errorMsg))
      }

      document.head.appendChild(script)
    } catch (error) {
      isLoading = false
      console.error('加载高德地图时发生错误:', error)
      reject(error)
    }
  })
}

/**
 * 检查高德地图是否已加载
 * @returns boolean
 */
export const isAMapLoaded = (): boolean => {
  return isLoaded && !!window.AMap
}

/**
 * 获取环境变量配置信息（用于调试）
 * @returns object
 */
export const getAMapConfig = () => {
  return {
    key: import.meta.env.VITE_AMAP_KEY ? '已配置' : '未配置',
    securityCode: import.meta.env.VITE_AMAP_SECURITY_CODE ? '已配置' : '未配置',
    isLoaded: isLoaded,
    isLoading: isLoading
  }
}
