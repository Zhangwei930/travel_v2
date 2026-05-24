import { defineStore } from 'pinia'

const KEY_CITY    = 'zhoumi_current_city'
const KEY_COORDS  = 'zhoumi_current_coords'
export const DEFAULT_CITY = '成都'
export const DEFAULT_COORDS = { lat: 30.5728, lng: 104.0668 }

function readCached() {
  try { return uni.getStorageSync(KEY_CITY) || DEFAULT_CITY } catch (_) { return DEFAULT_CITY }
}
function readCoords() {
  try { return uni.getStorageSync(KEY_COORDS) || null } catch (_) { return null }
}

export const useCityStore = defineStore('city', {
  state: () => ({
    current: readCached(),              // 城市名（来自定位反查，仅展示用）
    coords: readCoords(),               // { lat, lng }（API 调用的真实数据源）
    locating: false,                    // 是否正在定位
    locationDenied: false,              // 用户是否拒绝了定位授权
  }),
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
      try { uni.setStorageSync(KEY_COORDS, this.coords) } catch (_) {}
    },
    setDefaultLocation() {
      this.current = DEFAULT_CITY
      this.coords = { ...DEFAULT_COORDS }
      this.locationDenied = true
      try {
        uni.setStorageSync(KEY_CITY, this.current)
        uni.setStorageSync(KEY_COORDS, this.coords)
      } catch (_) {}
    },
  },
})
