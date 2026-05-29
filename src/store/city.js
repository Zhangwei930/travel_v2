import { defineStore } from 'pinia'

const KEY_CITY     = 'zhoumi_current_city'
const KEY_COORDS   = 'zhoumi_current_coords'
const KEY_LOCATION_SOURCE = 'zhoumi_location_source'
const KEY_LANDMARK = 'zhoumi_landmark'
export const DEFAULT_CITY = '成都'
export const DEFAULT_COORDS = { lat: 30.5728, lng: 104.0668 }

function readCached() {
  try { return uni.getStorageSync(KEY_CITY) || '' } catch (_) { return '' }
}
function readCoords() {
  try { return uni.getStorageSync(KEY_COORDS) || null } catch (_) { return null }
}
function isDefaultCoords(coords) {
  if (!coords) return false
  return Math.abs(Number(coords.lat) - DEFAULT_COORDS.lat) < 0.000001
    && Math.abs(Number(coords.lng) - DEFAULT_COORDS.lng) < 0.000001
}
function readLandmark() {
  try { return uni.getStorageSync(KEY_LANDMARK) || '' } catch (_) { return '' }
}
function readSource() {
  try {
    const source = uni.getStorageSync(KEY_LOCATION_SOURCE)
    if (source) return source
  } catch (_) {}
  const coords = readCoords()
  return isDefaultCoords(coords) ? 'default' : (coords ? 'located' : '')
}

export const useCityStore = defineStore('city', {
  state: () => ({
    current: readCached(),              // 城市名（来自定位反查，仅展示用）
    coords: readCoords(),               // { lat, lng }（API 调用的真实数据源）
    source: readSource(),               // located / default / ''
    locating: false,                    // 是否正在定位
    locationDenied: false,              // 用户是否拒绝了定位授权
    landmark: readLandmark(),            // 最近 POI 名（来自高德逆地理，仅展示用）
  }),
  getters: {
    hasRealLocation: (state) => state.source === 'located' && state.coords?.lat != null && state.coords?.lng != null,
  },
  actions: {
    setFromLocation(name) {
      if (!name || name === this.current) return
      this.current = name
      try { uni.setStorageSync(KEY_CITY, name) } catch (_) {}
      uni.$emit('cityChanged', name)
    },
    setCoords(lat, lng) {
      if (lat == null || lng == null) return
      this.coords = { lat, lng }
      this.source = 'located'
      // 坐标更新时清空 landmark，防止旧地标跟随旧城市继续显示
      this.landmark = ''
      try {
        uni.setStorageSync(KEY_COORDS, this.coords)
        uni.setStorageSync(KEY_LOCATION_SOURCE, this.source)
        uni.removeStorageSync(KEY_LANDMARK)
      } catch (_) {}
      // current 保留旧城市名，等 API 返回新城市后由 setFromLocation 更新
    },
    setDefaultLocation() {
      this.current = DEFAULT_CITY
      this.coords = { ...DEFAULT_COORDS }
      this.source = 'default'
      this.locationDenied = true
      try {
        uni.setStorageSync(KEY_CITY, this.current)
        uni.setStorageSync(KEY_COORDS, this.coords)
        uni.setStorageSync(KEY_LOCATION_SOURCE, this.source)
      } catch (_) {}
    },
  },
})
