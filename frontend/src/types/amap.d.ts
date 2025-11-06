// 高德地图类型声明
declare namespace AMap {
  class Map {
    constructor(container: string | HTMLElement, options?: MapOptions)
    setCenter(center: [number, number]): void
    setZoom(zoom: number): void
    setMapStyle(style: string): void
    setFitView(overlays?: any[], immediately?: boolean, avoid?: [number, number, number, number]): void
    add(overlay: any): void
    remove(overlay: any): void
    addControl(control: any): void
    destroy(): void
  }

  interface MapOptions {
    zoom?: number
    center?: [number, number]
    mapStyle?: string
    viewMode?: '2D' | '3D'
    pitch?: number
    rotation?: number
    features?: string[]
  }

  class Marker {
    constructor(options?: MarkerOptions)
    setPosition(position: [number, number]): void
    getPosition(): { lng: number; lat: number }
    setContent(content: string | HTMLElement): void
    on(event: string, handler: Function): void
    off(event: string, handler: Function): void
  }

  interface MarkerOptions {
    position?: [number, number]
    content?: string | HTMLElement
    offset?: Pixel
    title?: string
    icon?: string | Icon
    draggable?: boolean
    cursor?: string
    zIndex?: number
  }

  class Polyline {
    constructor(options?: PolylineOptions)
    setPath(path: [number, number][]): void
    getPath(): [number, number][]
  }

  interface PolylineOptions {
    path?: [number, number][]
    strokeColor?: string
    strokeWeight?: number
    strokeOpacity?: number
    strokeStyle?: 'solid' | 'dashed'
    strokeDasharray?: number[]
    lineJoin?: 'miter' | 'round' | 'bevel'
    lineCap?: 'butt' | 'round' | 'square'
    zIndex?: number
  }

  class InfoWindow {
    constructor(options?: InfoWindowOptions)
    open(map: Map, position: [number, number]): void
    close(): void
    setContent(content: string | HTMLElement): void
  }

  interface InfoWindowOptions {
    content?: string | HTMLElement
    offset?: Pixel
    position?: [number, number]
    anchor?: string
    closeWhenClickMap?: boolean
  }

  class Geocoder {
    constructor(options?: GeocoderOptions)
    getLocation(
      address: string,
      callback: (status: string, result: GeocoderResult) => void
    ): void
    getAddress(
      location: [number, number],
      callback: (status: string, result: GeocoderResult) => void
    ): void
  }

  interface GeocoderOptions {
    city?: string
    radius?: number
    batch?: boolean
  }

  interface GeocoderResult {
    info: string
    geocodes?: Array<{
      formattedAddress: string
      location: { lng: number; lat: number }
      addressComponent: any
    }>
    regeocode?: {
      formattedAddress: string
      addressComponent: any
    }
  }

  class Pixel {
    constructor(x: number, y: number)
  }

  class Icon {
    constructor(options?: IconOptions)
  }

  interface IconOptions {
    size?: [number, number]
    imageSize?: [number, number]
    image?: string
    imageOffset?: [number, number]
  }

  class Scale {
    constructor()
  }

  class ToolBar {
    constructor(options?: ToolBarOptions)
  }

  interface ToolBarOptions {
    position?: string
  }

  class ControlBar {
    constructor(options?: ControlBarOptions)
  }

  interface ControlBarOptions {
    position?: string
  }

  // 插件
  namespace plugin {
    class PlaceSearch {
      constructor(options?: PlaceSearchOptions)
      search(keyword: string, callback: (status: string, result: any) => void): void
    }

    interface PlaceSearchOptions {
      city?: string
      citylimit?: boolean
      pageSize?: number
      pageIndex?: number
    }
  }
}

// 全局声明
interface Window {
  AMap: typeof AMap
  _AMapSecurityConfig: {
    securityJsCode: string
  }
}
