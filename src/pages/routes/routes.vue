<template>
  <view class="cy-page">
    <cy-nav-bar title="精选路线" subtitle="多种时长路线组合" />

    <!-- 时长 tabs -->
    <view class="cy-dur-tabs">
      <view
        v-for="t in tabs"
        :key="t.id"
        class="cy-dur-tab"
        :class="{ 'cy-dur-tab--active': active === t.id }"
        @tap="active = t.id"
      >
        <text class="cy-dur-label">{{ t.label }}</text>
        <view v-if="active === t.id" class="cy-dur-line" />
      </view>
    </view>

    <scroll-view scroll-y class="cy-scroll" :show-scrollbar="false">
      <view v-if="loading" class="cy-hint-muted"><text>加载中…</text></view>
      <view v-else-if="locationError" class="cy-state-card">
        <text class="cy-state-title">需要开启定位</text>
        <text class="cy-state-sub">允许位置权限后才会推荐附近路线</text>
        <view class="cy-state-btn" @tap="reload">重新定位</view>
      </view>
      <view v-else-if="!visibleRoutes.length" class="cy-hint-muted"><text>该时长暂无精选路线</text></view>

      <view class="cy-route-list">
        <view
          v-for="route in visibleRoutes"
          :key="route.id"
          class="cy-route-row"
          @tap="openRoute(route)"
        >
          <view class="cy-route-thumb">
            <image
              :src="routeThumb(route)"
              class="cy-route-img"
              mode="aspectFill"
              lazy-load
              @error="onRouteImageError(route)"
            />
          </view>
          <view class="cy-route-body">
            <text class="cy-route-title">{{ route.title }}</text>
            <text class="cy-route-sub">{{ route.summary || '' }}</text>
            <view class="cy-route-meta">
              <view class="cy-meta-left">
                <view class="cy-meta-chip">
                  <CyIcon name="clock-green" :size="26" />
                  <text>{{ route.duration || '半日' }}</text>
                </view>
                <view class="cy-meta-chip">
                  <CyIcon name="pin-outline-green" :size="26" />
                  <text>{{ route.stops?.length || 0 }}个地点</text>
                </view>
              </view>
              <text class="cy-route-dist">约{{ totalDist(route) }}</text>
            </view>
          </view>
        </view>
      </view>

      <view style="height: 32rpx;" />
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { api } from '../../api/index.js'
import { routeImage } from '../../api/assets.js'
import { getHomeFeedCache, setHomeFeedCache } from '../../api/storage.js'
import { useCityStore } from '../../store/city.js'
import CyNavBar from '../../components/cy/cy-nav-bar.vue'
import CyIcon from '../../components/cy/cy-icon.vue'

const cityStore = useCityStore()
const loading = ref(false)
const locationError = ref(false)
const allRoutes = ref([])
const brokenRoute = ref({})

const tabs = [
  { id: '2h',   label: '2小时' },
  { id: 'half', label: '半日' },
  { id: 'day',  label: '一日' },
]
const active = ref('2h')

const visibleRoutes = computed(() => {
  const match = active.value === '2h'   ? /2\s*小时|2h|两小时/i
              : active.value === 'half' ? /半日|半天|3\s*小时|4\s*小时/i
              :                           /一日|全天|一天|day/i
  return allRoutes.value.filter(r => match.test(r.duration || ''))
})

function parseDistKm(text) {
  const m = String(text || '').match(/([0-9.]+)\s*(km|m|公里|米)?/i)
  if (!m) return 0
  const n = parseFloat(m[1])
  return /^m|米$/i.test(m[2] || '') ? n / 1000 : n
}

function totalDist(route) {
  const stops = route?.stops || []
  if (!stops.length) return '—'
  const km = stops.reduce((s, stop) => s + parseDistKm(stop.distance || ''), 0)
  return km.toFixed(1) + 'km'
}

function routeThumb(route) { return routeImage(route, brokenRoute.value[route?.id]) }
function onRouteImageError(r) {
  if (r?.id) brokenRoute.value = { ...brokenRoute.value, [r.id]: true }
}

onLoad(() => { loadFeed(false) })

async function loadFeed(forceLocation) {
  loading.value = true
  locationError.value = false
  try {
    const cached = !forceLocation ? getHomeFeedCache() : null
    if (cached) {
      allRoutes.value = cached.routes || []
      loading.value = false
      return
    }
    let coords = cityStore.coords
    if (!coords?.lat || forceLocation) {
      const r = await new Promise((res, rej) => {
        uni.getLocation({ type: 'gcj02', success: res, fail: rej })
      })
      cityStore.setCoords(r.latitude, r.longitude)
      coords = cityStore.coords
    }
    const city = cityStore.source === 'default' ? cityStore.current : ''
    const feed = await api.getHomeFeed({ lat: coords.lat, lng: coords.lng, city, intent: 'hot_routes' })
    if (feed?.location?.city) cityStore.setFromLocation(feed.location.city)
    setHomeFeedCache(feed)
    allRoutes.value = feed.routes || []
  } catch (_) {
    locationError.value = true
    allRoutes.value = []
  } finally {
    loading.value = false
  }
}

function reload() { loadFeed(true) }

function openRoute(route) {
  if (!route) return
  try { uni.setStorageSync('currentRoute', route) } catch (_) {}
  uni.navigateTo({ url: '/pages/routes/detail' })
}
</script>

<style lang="scss">
@import '../../uni.scss';

.cy-page {
  min-height: 100vh;
  background: $cy-bg;
  font-family: "PingFang SC", "HarmonyOS Sans SC", "Noto Sans SC", -apple-system, system-ui, sans-serif;
}

// ── 时长 tabs ──────────────────────────────────────────────
.cy-dur-tabs {
  display: flex;
  background: #fff;
  border-bottom: 1rpx solid $cy-border;
  padding: 0 32rpx;
}

.cy-dur-tab {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20rpx 0 0;
  position: relative;
  cursor: pointer;
}

.cy-dur-label {
  font-size: 30rpx;
  color: $cy-muted;
  font-weight: 500;
  padding-bottom: 18rpx;
}

.cy-dur-tab--active .cy-dur-label {
  color: $cy-green-d;
  font-size: 34rpx;
  font-weight: 800;
}

.cy-dur-line {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 48rpx;
  height: 4rpx;
  border-radius: 2rpx;
  background: $cy-green-d;
}

// ── 路线列表 ────────────────────────────────────────────────
.cy-hint-muted {
  text-align: center;
  color: $cy-muted;
  font-size: 26rpx;
  padding: 60rpx 0;
}

.cy-state-card {
  margin: 40rpx 24rpx;
  background: $cy-card;
  border-radius: 20rpx;
  padding: 40rpx;
  text-align: center;
  box-shadow: $cy-shadow;
}

.cy-state-title { display: block; font-size: 30rpx; font-weight: 800; color: $cy-text; margin-bottom: 8rpx; }
.cy-state-sub   { display: block; font-size: 24rpx; color: $cy-text-sub; margin-bottom: 24rpx; }
.cy-state-btn {
  display: inline-flex; align-items: center; height: 72rpx; padding: 0 40rpx;
  border-radius: 36rpx; background: $cy-green; color: #fff; font-size: 26rpx; font-weight: 700;
}

.cy-route-list {
  display: flex;
  flex-direction: column;
  padding: 20rpx 28rpx;
}

.cy-route-row {
  background: #fff;
  border-radius: 32rpx;
  border: 1rpx solid $cy-border;
  padding: 28rpx;
  margin-bottom: 28rpx;
  display: flex;
  gap: 20rpx;
  box-shadow: $cy-shadow;
  cursor: pointer;
}

.cy-route-thumb {
  width: 220rpx;
  height: 220rpx;
  border-radius: 24rpx;
  overflow: hidden;
  background: $cy-green-ls;
  flex-shrink: 0;
}

.cy-route-img { width: 100%; height: 100%; }

.cy-route-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.cy-route-title {
  display: block;
  font-size: 32rpx;
  font-weight: 800;
  color: $cy-text;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cy-route-sub {
  display: block;
  font-size: 24rpx;
  color: $cy-text-sub;
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  flex: 1;
  margin: 8rpx 0;
}

.cy-route-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.cy-meta-left {
  display: flex;
  gap: 12rpx;
}

.cy-meta-chip {
  display: flex;
  align-items: center;
  gap: 8rpx;
  font-size: 26rpx;
  color: $cy-text-sub;
}

.cy-route-dist {
  font-size: 26rpx;
  color: $cy-green;
  font-weight: 600;
}
</style>
