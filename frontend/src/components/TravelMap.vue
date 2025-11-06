<template>
  <div class="travel-map-container">
    <!-- 加载提示 -->
    <div v-if="isMapLoading" class="map-loading">
      <el-icon class="is-loading" :size="40">
        <Loading />
      </el-icon>
      <p>正在加载地图...</p>
    </div>
    
    <div id="travel-map" class="map-view"></div>
    
    <!-- 地图控制面板 -->
    <div class="map-controls">
      <el-button-group>
        <el-button :type="viewMode === 'standard' ? 'primary' : ''" @click="changeMapStyle('standard')">
          标准地图
        </el-button>
        <el-button :type="viewMode === 'satellite' ? 'primary' : ''" @click="changeMapStyle('satellite')">
          卫星地图
        </el-button>
      </el-button-group>
      
      <el-button @click="fitView" style="margin-left: 8px;">
        <el-icon><FullScreen /></el-icon>
        适应视野
      </el-button>
    </div>
    
    <!-- 地点列表侧边栏 -->
    <div v-if="showLocationList" class="location-list">
      <div class="list-header">
        <h4>行程地点</h4>
        <el-button text @click="showLocationList = false">
          <el-icon><Close /></el-icon>
        </el-button>
      </div>
      
      <div class="list-content">
        <div 
          v-for="(location, index) in locations" 
          :key="index"
          class="location-item"
          @click="focusLocation(index)"
        >
          <div class="location-number">{{ index + 1 }}</div>
          <div class="location-info">
            <div class="location-name">{{ location.name }}</div>
            <div class="location-address">{{ location.address }}</div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 展开按钮 -->
    <el-button 
      v-if="!showLocationList && locations.length > 0"
      class="toggle-list-btn"
      circle
      @click="showLocationList = true"
    >
      <el-icon><List /></el-icon>
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { FullScreen, Close, List, Loading } from '@element-plus/icons-vue'
import { loadAMap } from '@/utils/loadAMap'

// 定义 Props
interface Location {
  name: string
  address: string
  type?: string
}

interface Props {
  itinerary?: any[]  // 行程数据
  destination?: string  // 目的地
}

const props = defineProps<Props>()

// 响应式数据
const map = ref<any>(null)
const markers = ref<any[]>([])
const polyline = ref<any>(null)
const viewMode = ref<'standard' | 'satellite'>('standard')
const showLocationList = ref(true)
const locations = ref<Location[]>([])
const isMapLoading = ref(true)

// 声明 AMap
declare const AMap: any

// 初始化地图
const initMap = async () => {
  try {
    console.log('=== 开始初始化地图 ===')
    console.log('Props 数据:', { 
      hasItinerary: !!props.itinerary, 
      itineraryLength: props.itinerary?.length,
      destination: props.destination 
    })
    
    // 先加载高德地图 JS API
    await loadAMap()
    
    if (typeof AMap === 'undefined') {
      console.error('AMap 未定义')
      ElMessage.error('高德地图加载失败，请检查网络连接')
      isMapLoading.value = false
      return
    }
    console.log('✓ 高德地图 API 已加载')
    
  } catch (error: any) {
    console.error('高德地图加载失败:', error)
    ElMessage.error(error.message || '高德地图加载失败')
    isMapLoading.value = false
    return
  }

  try {
    // 等待 DOM 元素准备好
    await nextTick()
    
    const mapContainer = document.getElementById('travel-map')
    if (!mapContainer) {
      console.error('地图容器不存在')
      ElMessage.error('地图容器初始化失败')
      isMapLoading.value = false
      return
    }
    console.log('✓ 地图容器已准备好')
    
    // 创建地图实例
    map.value = new AMap.Map('travel-map', {
      zoom: 12,
      center: [116.397428, 39.90923], // 默认中心点（北京）
      mapStyle: 'amap://styles/normal',
      viewMode: '2D', // AMap 2.0 建议使用 2D
      zooms: [3, 20]
    })

    // AMap 2.0 版本添加控件的方式
    // 添加比例尺控件
    AMap.plugin(['AMap.Scale', 'AMap.ToolBar'], () => {
      map.value.addControl(new AMap.Scale())
      map.value.addControl(new AMap.ToolBar({
        position: 'RT' // 右上角
      }))
      console.log('✓ 地图控件已添加')
    })

    console.log('✓ 地图实例创建成功')
    isMapLoading.value = false
    
    // 先定位到目的地城市
    if (props.destination) {
      console.log('定位到目的地城市:', props.destination)
      await searchAndLocate(props.destination)
    }
    
    // 如果有行程数据，解析并标注
    if (props.itinerary && props.itinerary.length > 0) {
      console.log('开始解析行程数据...')
      await parseItineraryAndMark()
    } else {
      console.warn('⚠ 没有行程数据')
    }
  } catch (error) {
    console.error('❌ 地图初始化失败:', error)
    ElMessage.error(`地图初始化失败: ${error instanceof Error ? error.message : '未知错误'}`)
    isMapLoading.value = false
  }
}

// 解析行程数据并标注地点
const parseItineraryAndMark = async () => {
  if (!props.itinerary || props.itinerary.length === 0) {
    console.warn('没有行程数据')
    return
  }

  console.log('原始行程数据:', props.itinerary)
  const allLocations: Location[] = []
  
  // 遍历每一天的行程
  props.itinerary.forEach((day, dayIndex) => {
    console.log(`处理第 ${dayIndex + 1} 天的行程:`, day)
    
    if (day.activities && Array.isArray(day.activities)) {
      day.activities.forEach((activity: any, actIndex: number) => {
        console.log(`  - 活动 ${actIndex + 1}:`, activity)
        
        if (activity.location && activity.name) {
          allLocations.push({
            name: activity.name,
            address: activity.location,
            type: activity.type
          })
          console.log(`    ✓ 添加地点: ${activity.name} (${activity.location})`)
        } else {
          console.warn(`    ⚠ 跳过无效活动:`, activity)
        }
      })
    } else {
      console.warn(`  第 ${dayIndex + 1} 天没有有效的 activities 数组`)
    }
  })

  console.log(`共解析出 ${allLocations.length} 个地点:`, allLocations)
  locations.value = allLocations
  
  if (allLocations.length === 0) {
    console.warn('行程中没有有效的地点信息')
    ElMessage.warning('行程中没有有效的地点信息')
    return
  }

  // 使用高德地图地理编码服务获取坐标
  await geocodeAndMark(allLocations)
}

// 地理编码并标注
const geocodeAndMark = async (locationList: Location[]) => {
  if (!map.value) {
    console.error('地图实例不存在')
    return
  }

  console.log('开始地理编码，共 ' + locationList.length + ' 个地点')
  console.log('目的地城市:', props.destination || '全国')
  
  // 清除旧标记
  clearMarkers()
  
  // AMap 2.0 需要先加载地点搜索插件
  await new Promise<void>((resolve) => {
    AMap.plugin(['AMap.PlaceSearch'], () => {
      resolve()
    })
  })

  const coordinates: [number, number][] = []
  let successCount = 0
  let failCount = 0
  
  // 创建地点搜索实例（直接使用地点搜索，更可靠）
  const placeSearch = new AMap.PlaceSearch({
    city: props.destination || '全国',
    pageSize: 1,
    citylimit: false  // 不限制城市范围，扩大搜索
  })
  
  for (let i = 0; i < locationList.length; i++) {
    const location = locationList[i]
    console.log(`\n[${i + 1}/${locationList.length}] 正在搜索: ${location.name}`)
    console.log(`  地址: ${location.address}`)
    
    try {
      // 优先使用地点名称搜索（更准确）
      const searchQuery = location.name || location.address
      console.log(`  搜索关键词: ${searchQuery}`)
      
      const placeResult: any = await Promise.race([
        new Promise((resolve, reject) => {
          placeSearch.search(searchQuery, (status: string, result: any) => {
            console.log(`  搜索状态: ${status}`)
            
            if (status === 'complete' && result.poiList && result.poiList.pois.length > 0) {
              console.log(`  找到 ${result.poiList.pois.length} 个结果`)
              resolve(result.poiList.pois[0])
            } else {
              reject(new Error(`地点搜索失败: ${status}`))
            }
          })
        }),
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error('搜索超时(5秒)')), 5000)
        )
      ])
      
      const position = [placeResult.location.lng, placeResult.location.lat] as [number, number]
      console.log(`  ✓ 成功获取坐标: [${position[0]}, ${position[1]}]`)
      console.log(`  详细地址: ${placeResult.address || ''}`)
      coordinates.push(position)
      successCount++

      // 创建自定义标记（带数字）
      const marker = createNumberedMarker(position, i + 1, location)
      markers.value.push(marker)
      map.value.add(marker)
      console.log(`  ✓ 标记已添加`)

    } catch (error) {
      failCount++
      console.error(`  ❌ 地点 "${location.name}" 搜索失败:`, error)
      
      // 备用方案：使用地址搜索
      if (location.address && location.address !== location.name) {
        try {
          console.log(`  尝试备用方案: 使用地址搜索...`)
          
          const addressResult: any = await Promise.race([
            new Promise((resolve, reject) => {
              placeSearch.search(location.address, (status: string, result: any) => {
                console.log(`    地址搜索状态: ${status}`)
                if (status === 'complete' && result.poiList && result.poiList.pois.length > 0) {
                  resolve(result.poiList.pois[0])
                } else {
                  reject(new Error('地址搜索失败'))
                }
              })
            }),
            new Promise((_, reject) => 
              setTimeout(() => reject(new Error('地址搜索超时(5秒)')), 5000)
            )
          ])
          
          const position = [addressResult.location.lng, addressResult.location.lat] as [number, number]
          console.log(`    ✓ 地址搜索成功，坐标: [${position[0]}, ${position[1]}]`)
          coordinates.push(position)
          successCount++
          
          const marker = createNumberedMarker(position, i + 1, location)
          markers.value.push(marker)
          map.value.add(marker)
          console.log(`    ✓ 标记已添加`)
          
        } catch (searchError) {
          console.error(`    ❌ 备用方案也失败了:`, searchError)
        }
      }
    }
    
    // 添加延迟，避免请求过快
    if (i < locationList.length - 1) {
      await new Promise(resolve => setTimeout(resolve, 300))
    }
  }

  console.log(`\n=== 地理编码完成 ===`)
  console.log(`成功: ${successCount} 个`)
  console.log(`失败: ${failCount} 个`)
  console.log(`总坐标数: ${coordinates.length}`)
  console.log(`坐标列表:`, coordinates)

  // 如果有多个地点，绘制路线
  if (coordinates.length > 1) {
    console.log('绘制连接线...')
    drawPolyline(coordinates)
  }

  // 调整地图视野以显示所有标记
  if (coordinates.length > 0) {
    console.log('调整地图视野，包含所有标记点...')
    
    // 使用 nextTick 确保所有标记都已添加到地图
    await nextTick()
    
    // 设置合适的缩放级别和中心点
    try {
      map.value.setFitView(markers.value, false, [50, 50, 50, 50])
      console.log('✓ 视野调整完成')
    } catch (e) {
      console.warn('setFitView 失败，尝试手动设置中心点', e)
      // 备用方案：计算中心点
      const avgLng = coordinates.reduce((sum, coord) => sum + coord[0], 0) / coordinates.length
      const avgLat = coordinates.reduce((sum, coord) => sum + coord[1], 0) / coordinates.length
      map.value.setCenter([avgLng, avgLat])
      map.value.setZoom(10)
    }
    
    // 成功标注提示
    if (failCount > 0) {
      ElMessage.warning(`已标注 ${successCount} 个地点，${failCount} 个地点未找到`)
    } else {
      ElMessage.success(`已标注 ${successCount} 个地点`)
    }
  } else {
    console.error('没有成功获取任何坐标')
    
    // 检查是否是国外目的地
    const isForeign = props.destination && !isChineseCity(props.destination)
    if (isForeign) {
      ElMessage.warning('高德地图对国外地点支持有限，建议使用国内目的地')
    } else {
      ElMessage.error('所有地点的搜索都失败了，请检查地址信息')
    }
  }
}

// 检查是否是中国城市（简单判断）
const isChineseCity = (city: string): boolean => {
  const chineseRegions = [
    '北京', '上海', '天津', '重庆', '广州', '深圳', '成都', '西安', '杭州', '武汉',
    '郑州', '南京', '沈阳', '青岛', '济南', '哈尔滨', '长春', '大连', '厦门', '福州',
    '昆明', '贵阳', '兰州', '西宁', '银川', '呼和浩特', '乌鲁木齐', '拉萨', '南宁',
    '海口', '三亚', '石家庄', '太原', '南昌', '合肥', '长沙', '海南', '云南', '四川',
    '贵州', '西藏', '新疆', '内蒙', '广西', '宁夏', '青海', '甘肃', '陕西', '河北',
    '山西', '辽宁', '吉林', '黑龙江', '江苏', '浙江', '安徽', '福建', '江西', '山东',
    '河南', '湖北', '湖南', '广东', '台湾', '香港', '澳门'
  ]
  return chineseRegions.some(region => city.includes(region))
}

// 创建带数字的标记
const createNumberedMarker = (position: [number, number], number: number, location: Location) => {
  // 创建自定义标记内容
  const content = `
    <div class="custom-marker">
      <div class="marker-number">${number}</div>
    </div>
  `

  const marker = new AMap.Marker({
    position: position,
    content: content,
    offset: new AMap.Pixel(-20, -40),
    title: location.name
  })

  // 添加点击事件
  marker.on('click', () => {
    showInfoWindow(marker, location, number)
  })

  return marker
}

// 显示信息窗口
const showInfoWindow = (marker: any, location: Location, number: number) => {
  const infoWindow = new AMap.InfoWindow({
    content: `
      <div class="info-window">
        <h4>${number}. ${location.name}</h4>
        <p>${location.address}</p>
        ${location.type ? `<p class="info-type">类型: ${getTypeText(location.type)}</p>` : ''}
      </div>
    `,
    offset: new AMap.Pixel(0, -40)
  })

  infoWindow.open(map.value, marker.getPosition())
}

// 绘制路线
const drawPolyline = (coordinates: [number, number][]) => {
  // 清除旧路线
  if (polyline.value) {
    map.value.remove(polyline.value)
  }

  polyline.value = new AMap.Polyline({
    path: coordinates,
    strokeColor: '#409EFF',
    strokeWeight: 4,
    strokeOpacity: 0.8,
    strokeStyle: 'solid',
    strokeDasharray: [10, 5],
    lineJoin: 'round',
    lineCap: 'round',
    zIndex: 50
  })

  map.value.add(polyline.value)
}

// 清除所有标记
const clearMarkers = () => {
  if (markers.value.length > 0) {
    map.value.remove(markers.value)
    markers.value = []
  }
  if (polyline.value) {
    map.value.remove(polyline.value)
    polyline.value = null
  }
}

// 搜索并定位到目的地
const searchAndLocate = (destination: string): Promise<void> => {
  return new Promise((resolve) => {
    if (!map.value || !destination) {
      resolve()
      return
    }

    console.log(`正在定位目的地: ${destination}`)
    
    // AMap 2.0 需要先加载 PlaceSearch 插件
    AMap.plugin('AMap.PlaceSearch', () => {
      const placeSearch = new AMap.PlaceSearch({
        citylimit: false
      })
      
      // 使用地点搜索定位目的地（支持国外城市）
      const searchPromise = Promise.race([
        new Promise((innerResolve, innerReject) => {
          placeSearch.search(destination, (status: string, result: any) => {
            console.log(`目的地搜索状态: ${status}`, result)
            
            if (status === 'complete' && result.poiList && result.poiList.pois.length > 0) {
              const poi = result.poiList.pois[0]
              const location = poi.location
              console.log(`✓ 目的地坐标: [${location.lng}, ${location.lat}]`)
              map.value.setCenter([location.lng, location.lat])
              map.value.setZoom(11)
              innerResolve(true)
            } else {
              innerReject(new Error(`目的地搜索失败: ${status}`))
            }
          })
        }),
        new Promise((_, innerReject) => 
          setTimeout(() => innerReject(new Error('目的地搜索超时')), 5000)
        )
      ])
      
      searchPromise
        .then(() => resolve())
        .catch((error) => {
          console.warn('⚠ 高德地图无法定位目的地:', destination, error.message)
          console.log('使用默认坐标（将在标注地点后自动调整）')
          // 不设置中心点，让后续的 setFitView 自动调整
          resolve()
        })
    })
  })
}

// 改变地图样式
const changeMapStyle = (style: 'standard' | 'satellite') => {
  if (!map.value) return
  
  viewMode.value = style
  
  if (style === 'standard') {
    map.value.setMapStyle('amap://styles/normal')
  } else {
    map.value.setMapStyle('amap://styles/satellite')
  }
}

// 适应视野
const fitView = () => {
  if (map.value && markers.value.length > 0) {
    map.value.setFitView()
  }
}

// 聚焦到某个地点
const focusLocation = (index: number) => {
  if (markers.value[index]) {
    const marker = markers.value[index]
    map.value.setCenter(marker.getPosition())
    map.value.setZoom(16)
    
    // 触发标记点击事件
    const location = locations.value[index]
    showInfoWindow(marker, location, index + 1)
  }
}

// 获取类型文本
const getTypeText = (type: string) => {
  const typeMap: Record<string, string> = {
    attraction: '景点',
    restaurant: '餐厅',
    hotel: '酒店',
    transport: '交通',
    shopping: '购物',
    entertainment: '娱乐',
    other: '其他'
  }
  return typeMap[type] || type
}

// 监听行程数据变化
watch(() => props.itinerary, () => {
  if (map.value && props.itinerary) {
    parseItineraryAndMark()
  }
}, { deep: true })

// 组件挂载
onMounted(() => {
  nextTick(() => {
    initMap()
  })
})

// 暴露方法给父组件
defineExpose({
  focusLocation,
  fitView
})
</script>

<style scoped>
.travel-map-container {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 400px;
  border-radius: 8px;
  overflow: hidden;
}

.map-loading {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  z-index: 2000;
}

.map-loading p {
  margin-top: 16px;
  color: #606266;
  font-size: 14px;
}

.map-view {
  width: 100%;
  height: 100%;
}

.map-controls {
  position: absolute;
  top: 16px;
  right: 16px;
  z-index: 1000;
  background: white;
  padding: 8px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.location-list {
  position: absolute;
  left: 16px;
  top: 16px;
  bottom: 16px;
  width: 280px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  display: flex;
  flex-direction: column;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #eee;
}

.list-header h4 {
  margin: 0;
  color: #2c3e50;
  font-size: 16px;
}

.list-content {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.location-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  margin-bottom: 8px;
  background: #f9f9f9;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.location-item:hover {
  background: #e6f7ff;
  transform: translateX(4px);
}

.location-number {
  width: 32px;
  height: 32px;
  background: #409EFF;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  flex-shrink: 0;
}

.location-info {
  flex: 1;
  overflow: hidden;
}

.location-name {
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.location-address {
  font-size: 12px;
  color: #909399;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.toggle-list-btn {
  position: absolute;
  left: 16px;
  top: 16px;
  z-index: 1000;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 移动端适配 */
@media (max-width: 768px) {
  .travel-map-container {
    height: 400px;
  }
  
  .location-list {
    width: 240px;
  }
  
  .map-controls {
    top: 8px;
    right: 8px;
    padding: 4px;
  }
}
</style>

<style>
/* 全局样式：自定义标记 */
.custom-marker {
  width: 40px;
  height: 40px;
  position: relative;
}

.marker-number {
  width: 40px;
  height: 40px;
  background: #409EFF;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  border: 3px solid white;
  cursor: pointer;
  transition: all 0.3s;
}

.marker-number:hover {
  transform: scale(1.1);
  background: #66b1ff;
}

/* 自定义信息窗口 */
.info-window {
  padding: 8px;
  min-width: 200px;
}

.info-window h4 {
  margin: 0 0 8px 0;
  color: #2c3e50;
  font-size: 14px;
}

.info-window p {
  margin: 4px 0;
  color: #606266;
  font-size: 12px;
}

.info-type {
  color: #909399;
  font-style: italic;
}
</style>
