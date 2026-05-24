// 当前城市 — 完全由定位驱动（不提供手动切换）
//
// 产品定位：本地化出游，根据高德实时定位推荐附近。
// 用户不需要手动选城市，城市只是 UI 上"我在哪"的展示，以及
// 后端展示用。定位失败时首页不展示附近推荐，避免把城市中心伪装成当前位置。
import { defineStore } from 'pinia'

const KEY_CITY    = 'zhoumi_current_city'
const KEY_COORDS  = 'zhoumi_current_coords'
const DEFAULT_CITY = '成都'

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
  },
})
