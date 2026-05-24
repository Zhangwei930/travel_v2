<template>
  <view class="page">
    <u-nav-bar title="精选路线" />
    <text class="page-subtitle">多种时长路线组合</text>

    <!-- 时长 tab -->
    <view class="duration-tabs">
      <view
        v-for="t in tabs"
        :key="t.id"
        class="dur-tab"
        :class="{ active: active === t.id }"
        @tap="setTab(t.id)"
      >
        <text class="dur-tab-text">{{ t.label }}</text>
        <view v-if="active === t.id" class="dur-tab-underline" />
      </view>
    </view>

    <scroll-view scroll-y class="scroll-body" :show-scrollbar="false">
      <view v-if="loading" class="hint">加载中…</view>
      <view v-else-if="locationError" class="state-card">
        <text class="state-title">需要开启定位</text>
        <text class="state-sub">允许位置权限后才会推荐附近路线</text>
        <view class="state-btn" @tap="reload">重新定位</view>
      </view>
      <view v-else-if="!visibleRoutes.length" class="hint">该时长暂无精选路线</view>

      <view class="route-list">
        <view
          v-for="route in visibleRoutes"
          :key="route.id"
          class="route-card"
          @tap="openRoute(route)"
        >
          <view class="route-thumb">
            <image
              :src="routeThumb(route)"
              class="route-thumb-img"
              mode="aspectFill"
              lazy-load
              @error="onRouteImageError(route)"
            />
          </view>
          <view class="route-body">
            <text class="route-title">{{ route.title }}</text>
            <text class="route-summary">{{ route.summary || ' ' }}</text>
            <view class="route-meta">
              <view class="meta-left">
                <text class="meta-item">🕐 约{{ route.duration || '半日' }}</text>
                <text class="meta-item">🚶 {{ route.stops?.length || 0 }}个地点</text>
              </view>
              <text class="meta-dist">约{{ totalDist(route) }}</text>
            </view>
          </view>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { computed, ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { api } from '../../api/mock.js'
import { routeImage } from '../../api/assets.js'
import { getHomeFeedCache, setHomeFeedCache } from '../../api/storage.js'
import { useCityStore } from '../../store/city.js'
import UNavBar from '../../components/UNavBar.vue'

const cityStore = useCityStore()
const loading = ref(false)
const locationError = ref(false)
const allRoutes = ref([])
const brokenRouteImages = ref({})

const tabs = [
  { id: '2h',    label: '2小时' },
  { id: 'half',  label: '半日' },
  { id: 'day',   label: '一日' },
]
const active = ref('2h')

const visibleRoutes = computed(() => {
  const match = active.value === '2h'   ? /2\s*小时|2h|两小时/i
              : active.value === 'half' ? /半日|半天|3\s*小时|4\s*小时/i
              :                            /一日|全天|一天|day/i
  return allRoutes.value.filter(r => match.test(r.duration || ''))
})

function setTab(id) { active.value = id }

function parseDistanceKm(text) {
  if (!text) return 0
  const m = String(text).match(/([0-9.]+)\s*(km|m|公里|米)?/i)
  if (!m) return 0
  const n = parseFloat(m[1])
  return /^m|米$/i.test(m[2] || '') ? n / 1000 : n
}

function totalDist(route) {
  const stops = route?.stops || []
  if (!stops.length) return '—'
  const km = stops.reduce((sum, s) => sum + parseDistanceKm(s.distance || ''), 0)
  return km.toFixed(1) + 'km'
}

function routeThumb(route) {
  return routeImage(route, brokenRouteImages.value[route?.id])
}

function onRouteImageError(route) {
  if (!route?.id) return
  brokenRouteImages.value = { ...brokenRouteImages.value, [route.id]: true }
}

onLoad(async () => {
  await loadFeed(false)
})

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
    if (!coords || forceLocation) {
      coords = await new Promise((resolve, reject) => {
        uni.getLocation({ type: 'gcj02', success: (r) => resolve({ lat: r.latitude, lng: r.longitude }), fail: reject })
      })
      cityStore.setCoords(coords.lat, coords.lng)
    }
    const feed = await api.getHomeFeed({
      lat: coords.lat,
      lng: coords.lng,
      city: cityStore.current,
      intent: 'hot_routes',
    })
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

function reload() {
  loadFeed(true)
}

function openRoute(route) {
  if (!route) return
  try { uni.setStorageSync('currentRoute', route) } catch (_) {}
  uni.navigateTo({ url: '/pages/routes/detail' })
}
</script>

<style lang="scss">
@import '../../uni.scss';

.page {
  min-height: 100vh;
  background: $u-bg;
}

.page-subtitle {
  display: block;
  text-align: center;
  font-size: 22rpx;
  color: $u-text-mute;
  padding: 4rpx 0 16rpx;
}

// ── 时长 tabs ──────────────────────────────────────────────
.duration-tabs {
  display: flex;
  padding: 0 32rpx;
  background: $u-bg;
  border-bottom: 1rpx solid $u-line;
  margin-bottom: 6rpx;
}

.dur-tab {
  flex: 1;
  text-align: center;
  padding: 18rpx 0 16rpx;
  position: relative;
}

.dur-tab-text {
  font-size: 28rpx;
  color: $u-text-sub;
  font-weight: 500;
}

.dur-tab.active .dur-tab-text {
  color: $z-primary;
  font-weight: 800;
}

.dur-tab-underline {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 48rpx;
  height: 4rpx;
  border-radius: 2rpx;
  background: $z-primary;
}

// ── 列表 ────────────────────────────────────────────────────
.scroll-body {
  position: relative;
  background: $u-bg;
}

.hint {
  text-align: center;
  color: $u-text-mute;
  font-size: 24rpx;
  padding: 60rpx 0;
}

.state-card {
  margin: 40rpx 24rpx 0;
  background: $u-bg;
  border-radius: 18rpx;
  padding: 36rpx 28rpx;
  text-align: center;
  box-shadow: $u-shadow;
}

.state-title { display: block; font-size: 28rpx; font-weight: 800; color: $u-text; margin-bottom: 8rpx; }
.state-sub   { display: block; font-size: 22rpx; color: $u-text-sub; margin-bottom: 24rpx; }
.state-btn {
  display: inline-flex; align-items: center; justify-content: center;
  height: 64rpx; padding: 0 32rpx; border-radius: 12rpx;
  background: $z-primary; color: #fff; font-size: 24rpx; font-weight: 700;
}

.route-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  padding: 16rpx 24rpx 32rpx;
}

.route-card {
  background: $u-bg;
  border-radius: 20rpx;
  padding: 16rpx;
  display: flex;
  gap: 16rpx;
  box-shadow: $u-shadow;
  cursor: pointer;
}

.route-thumb {
  width: 160rpx;
  height: 160rpx;
  border-radius: 14rpx;
  overflow: hidden;
  background: $u-bg-soft;
  flex-shrink: 0;
}

.route-thumb-img { width: 100%; height: 100%; }

.route-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.route-title {
  display: block;
  font-size: 28rpx;
  font-weight: 800;
  color: $u-text;
  margin-bottom: 6rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.route-summary {
  display: block;
  font-size: 22rpx;
  color: $u-text-sub;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  margin-bottom: 10rpx;
}

.route-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12rpx;
}

.meta-left {
  display: flex;
  gap: 14rpx;
  flex: 1;
  min-width: 0;
}

.meta-item {
  font-size: 20rpx;
  color: $u-text-mute;
}

.meta-dist {
  font-size: 22rpx;
  color: $z-primary;
  font-weight: 700;
  flex-shrink: 0;
}
</style>
