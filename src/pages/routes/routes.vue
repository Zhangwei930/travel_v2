<template>
  <view class="page">
    <view class="header" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="top-row">
        <view class="back-btn" @tap="goBack">‹</view>
        <view class="title-wrap">
          <text class="kicker mono">FEATURED ROUTES</text>
          <text class="title serif">精选路线</text>
          <text class="sub">{{ cityStore.current }} · {{ weatherText }}</text>
        </view>
        <view class="reload-btn" @tap="reload">刷新</view>
      </view>
    </view>

    <scroll-view scroll-y class="scroll-body" :show-scrollbar="false">
      <view v-if="loading" class="state-card">
        <text class="state-icon">⌖</text>
        <text class="state-title serif">正在获取精选路线</text>
        <text class="state-sub">路线基于当前位置和附近 3-5km 推荐。</text>
      </view>

      <view v-else-if="locationError" class="state-card">
        <text class="state-icon">!</text>
        <text class="state-title serif">需要开启定位</text>
        <text class="state-sub">没有当前位置时不展示附近路线。</text>
        <view class="primary-btn" @tap="reload">重新定位</view>
      </view>

      <view v-else class="section">
        <view v-if="!routes.length" class="empty mono">暂无精选路线</view>
        <view class="route-list">
          <view v-for="route in routes" :key="route.id" class="route-card" @tap="openRoute(route)">
            <view class="route-head">
              <view>
                <text class="route-title serif">{{ route.title }}</text>
                <text class="route-sub">{{ route.duration }} · {{ route.budget || '预算可控' }}</text>
              </view>
              <text class="route-badge">{{ route.stops?.length || 0 }}站</text>
            </view>
            <text class="reason" :numberOfLines="2">{{ route.summary }}</text>
            <view class="stops">
              <view v-for="stop in route.stops.slice(0, 4)" :key="stop.name" class="stop-row">
                <text class="dot" />
                <text class="stop-name">{{ stop.name }}</text>
                <text class="stop-dist">{{ stop.distance }}</text>
              </view>
            </view>
            <view class="card-foot">
              <text class="source">点击后导航到第一站</text>
              <view class="nav-btn" :class="{ disabled: !route.nav_ready }">路线导航</view>
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
import { getCoords, getHomeFeedCache, setHomeFeedCache } from '../../api/storage.js'
import { useCityStore } from '../../store/city.js'

const cityStore = useCityStore()
const statusBarHeight = ref(44)
const loading = ref(false)
const locationError = ref(false)
const weather = ref(null)
const routes = ref([])

const weatherText = computed(() => weather.value ? `${weather.value.temp}° ${weather.value.cond}` : '定位推荐')

onLoad(async (options) => {
  applyContext(options)
  try {
    const sys = uni.getSystemInfoSync()
    statusBarHeight.value = sys.statusBarHeight || 44
  } catch (_) {}
  await loadFeed(false)
})

function asNumber(value, fallback = null) {
  const num = Number(value)
  return Number.isFinite(num) ? num : fallback
}

function readText(value) {
  if (value == null) return ''
  try { return decodeURIComponent(String(value)) } catch (_) { return String(value) }
}

function applyContext(options = {}) {
  const lat = asNumber(options.lat, cityStore.coords?.lat ?? null)
  const lng = asNumber(options.lng, cityStore.coords?.lng ?? null)
  const city = readText(options.city) || cityStore.current
  if (lat != null && lng != null) cityStore.setCoords(lat, lng)
  if (city) cityStore.setFromLocation(city)
}

async function loadFeed(forceLocation) {
  loading.value = true
  locationError.value = false
  try {
    const cached = !forceLocation ? getHomeFeedCache() : null
    if (cached) {
      applyFeed(cached)
      return
    }

    let coords = cityStore.coords || getCoords()
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
    applyFeed(feed)
  } catch (_) {
    locationError.value = true
    routes.value = []
    weather.value = null
  } finally {
    loading.value = false
  }
}

function applyFeed(feed) {
  weather.value = feed.weather || null
  routes.value = feed.routes || []
}

function reload() {
  loadFeed(true)
}

function goBack() {
  uni.navigateBack()
}

function openRoute(route) {
  const stop = (route?.stops || []).find(s => s.lat != null && s.lng != null)
  if (!stop) {
    uni.showToast({ title: '该路线暂无可导航站点', icon: 'none' })
    return
  }
  uni.openLocation({
    latitude: Number(stop.lat),
    longitude: Number(stop.lng),
    name: stop.name,
    address: stop.reason || '',
  })
}
</script>

<style lang="scss">
@import '../../uni.scss';

.page {
  min-height: 100vh;
  background: $z-bg;
}

.header {
  background: $z-primary;
  padding: 0 28rpx 34rpx;
}

.top-row {
  display: flex;
  align-items: center;
  gap: 18rpx;
  padding-top: 18rpx;
}

.back-btn,
.reload-btn {
  height: 62rpx;
  border-radius: 12rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  color: $z-card;
  background: rgba(255, 255, 255, 0.14);
  flex-shrink: 0;
}

.back-btn {
  width: 62rpx;
  font-size: 44rpx;
}

.reload-btn {
  padding: 0 20rpx;
  font-size: 23rpx;
  font-weight: 800;
}

.title-wrap {
  flex: 1;
  min-width: 0;
}

.kicker {
  display: block;
  color: rgba(255, 255, 255, 0.58);
  font-size: 18rpx;
  margin-bottom: 2rpx;
}

.title {
  display: block;
  color: $z-card;
  font-size: 36rpx;
  font-weight: 900;
  margin-bottom: 4rpx;
}

.sub {
  display: block;
  color: rgba(255, 255, 255, 0.72);
  font-size: 22rpx;
}

.scroll-body {
  height: calc(100vh - 160rpx);
}

.section {
  padding: 26rpx 28rpx 48rpx;
}

.state-card {
  margin: 28rpx;
  background: $z-card;
  border-radius: 18rpx;
  padding: 46rpx 30rpx;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 2rpx 10rpx rgba(13, 79, 74, 0.05);
}

.state-icon {
  width: 88rpx;
  height: 88rpx;
  border-radius: 44rpx;
  background: rgba(13, 79, 74, 0.08);
  color: $z-primary;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 38rpx;
  font-weight: 900;
  margin-bottom: 20rpx;
}

.state-title {
  font-size: 32rpx;
  font-weight: 900;
  color: $z-text;
  margin-bottom: 8rpx;
}

.state-sub,
.empty {
  color: $z-muted;
  font-size: 24rpx;
}

.primary-btn {
  margin-top: 24rpx;
  height: 64rpx;
  padding: 0 28rpx;
  border-radius: 12rpx;
  background: $z-primary;
  color: $z-card;
  font-size: 24rpx;
  font-weight: 800;
  display: flex;
  align-items: center;
}

.route-list {
  display: flex;
  flex-direction: column;
  gap: 18rpx;
}

.route-card {
  background: $z-card;
  border-radius: 16rpx;
  padding: 20rpx;
  display: flex;
  flex-direction: column;
  gap: 14rpx;
  box-shadow: 0 2rpx 10rpx rgba(13, 79, 74, 0.05);
}

.route-head,
.card-foot {
  display: flex;
  justify-content: space-between;
  gap: 16rpx;
}

.route-title {
  display: block;
  color: $z-text;
  font-size: 29rpx;
  font-weight: 900;
  line-height: 1.25;
  margin-bottom: 6rpx;
}

.route-sub,
.source,
.stop-dist {
  color: $z-muted;
  font-size: 21rpx;
}

.reason {
  display: block;
  color: $z-text2;
  font-size: 23rpx;
  line-height: 1.5;
}

.route-badge {
  height: 46rpx;
  padding: 0 16rpx;
  border-radius: 10rpx;
  background: rgba(255, 107, 53, 0.12);
  color: $z-accent;
  display: flex;
  align-items: center;
  font-size: 22rpx;
  font-weight: 800;
  flex-shrink: 0;
}

.stops {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}

.stop-row {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.dot {
  width: 12rpx;
  height: 12rpx;
  border-radius: 6rpx;
  background: $z-primary;
  flex-shrink: 0;
}

.stop-name {
  flex: 1;
  min-width: 0;
  color: $z-text2;
  font-size: 24rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-foot {
  align-items: center;
}

.nav-btn {
  height: 58rpx;
  min-width: 108rpx;
  padding: 0 20rpx;
  border-radius: 10rpx;
  background: $z-primary;
  color: $z-card;
  font-size: 24rpx;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.nav-btn.disabled {
  background: $z-muted;
}
</style>
