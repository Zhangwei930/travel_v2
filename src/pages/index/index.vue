<template>
  <view class="page">
    <u-nav-bar title="出游助手" :show-back="false" right-icon="search" @right="onSearch" />

    <scroll-view
      scroll-y
      class="scroll-body"
      :style="{ paddingBottom: tabBarHeight }"
      :show-scrollbar="false"
    >
      <!-- 位置 + 天气 -->
      <view class="loc-row">
        <view class="loc-left">
          <view class="loc-pin">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none">
              <path d="M12 22s-8-7-8-13a8 8 0 1116 0c0 6-8 13-8 13z" stroke="#1A7A73" stroke-width="2"/>
              <circle cx="12" cy="9" r="3" stroke="#1A7A73" stroke-width="2"/>
            </svg>
          </view>
          <text class="loc-text">{{ locText }}</text>
        </view>
        <view class="loc-right">
          <view class="weather-line">
            <text class="weather-icon">{{ weatherIcon }}</text>
            <text class="weather-text">{{ weatherText }}</text>
          </view>
          <text class="radius-text">3~5km推荐范围</text>
        </view>
      </view>

      <!-- 出游助手 mascot pill -->
      <view class="mascot-card">
        <view class="mascot-avatar">
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">
            <rect x="8" y="11" width="16" height="13" rx="4" fill="#fff"/>
            <circle cx="13" cy="17" r="1.6" fill="#0D4F4A"/>
            <circle cx="19" cy="17" r="1.6" fill="#0D4F4A"/>
            <rect x="14" y="20" width="4" height="1.4" rx="0.7" fill="#0D4F4A"/>
            <rect x="15" y="7" width="2" height="4" rx="1" fill="#fff"/>
            <circle cx="16" cy="6" r="1.4" fill="#fff"/>
          </svg>
        </view>
        <view class="mascot-text">
          <text class="mascot-title">出游助手</text>
          <text class="mascot-sub">已根据您的位置，为您准备了 4 种出游方式</text>
        </view>
      </view>

      <!-- 4 入口 -->
      <view class="entry-grid">
        <view
          v-for="entry in entries"
          :key="entry.id"
          class="entry-card"
          :class="'tint-' + entry.id"
          @tap="goEntry(entry.id)"
        >
          <view class="entry-icon-wrap">
            <!-- place_index -->
            <svg v-if="entry.id === 'place_index'" xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none">
              <path d="M12 22s-8-7-8-13a8 8 0 1116 0c0 6-8 13-8 13z" stroke="#8B6914" stroke-width="2"/>
              <circle cx="12" cy="9" r="3" fill="#8B6914"/>
            </svg>
            <!-- nearby_now -->
            <svg v-else-if="entry.id === 'nearby_now'" xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="9" stroke="#1A7A73" stroke-width="2"/>
              <path d="M12 6v6l4 2" stroke="#1A7A73" stroke-width="2" stroke-linecap="round"/>
            </svg>
            <!-- hot_routes -->
            <svg v-else-if="entry.id === 'hot_routes'" xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none">
              <rect x="4" y="7" width="16" height="13" rx="2" stroke="#C03E1F" stroke-width="2"/>
              <path d="M9 7V5a2 2 0 012-2h2a2 2 0 012 2v2" stroke="#C03E1F" stroke-width="2"/>
            </svg>
            <!-- assistant -->
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none">
              <path d="M21 12a8 8 0 01-12.5 6.6L3 20l1.4-5.5A8 8 0 1121 12z" stroke="#0D4F4A" stroke-width="2" stroke-linejoin="round"/>
            </svg>
          </view>
          <text class="entry-label">{{ entryLabel(entry.id) }}</text>
          <text class="entry-desc">{{ entryDesc(entry.id) }}</text>
        </view>
      </view>

      <!-- 附近现在适合去 -->
      <view class="section">
        <view class="section-head">
          <text class="section-title">附近现在适合去</text>
          <text class="section-more" @tap="goNearby">更多 ›</text>
        </view>
        <view v-if="locationError" class="hint-card">
          <text>开启定位后才能推荐附近真实可去的地点</text>
          <view class="hint-btn" @tap="loadFeed()">重新定位</view>
        </view>
        <view v-else-if="!nearbyVisible.length" class="hint-card mute">
          <text>{{ feedLoading ? '正在加载附近推荐…' : '附近暂无可推荐地点' }}</text>
        </view>
        <view v-else class="poi-list">
          <view
            v-for="poi in nearbyVisible"
            :key="poi.id"
            class="poi-card"
            @tap="goPoi(poi.id)"
          >
            <view class="poi-thumb">
              <image v-if="poi.img" :src="poi.img" class="poi-thumb-img" mode="aspectFill" lazy-load />
              <view v-else class="poi-thumb-fallback">
                <text>📍</text>
              </view>
            </view>
            <view class="poi-content">
              <view class="poi-line1">
                <text class="poi-name">{{ poi.name }}</text>
                <text class="poi-dist">{{ poi.distance }}</text>
              </view>
              <view class="poi-tags">
                <text
                  v-for="tag in (poi.tags || []).slice(0, 3)"
                  :key="tag"
                  class="poi-tag"
                >{{ tag }}</text>
              </view>
              <view class="poi-line3">
                <text class="poi-cat">{{ poi.category || '地点' }}</text>
                <view class="poi-rating">
                  <text class="rating-star">★</text>
                  <text class="rating-num">{{ poi.rating || (4.0 + (poi.id % 10) / 10).toFixed(1) }}</text>
                </view>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 精选路线 -->
      <view class="section">
        <view class="section-head">
          <text class="section-title">精选路线</text>
          <text class="section-more" @tap="goRoutes">更多 ›</text>
        </view>
        <view v-if="!routes.length" class="hint-card mute">
          <text>{{ feedLoading ? '正在加载精选路线…' : '暂无精选路线' }}</text>
        </view>
        <scroll-view v-else scroll-x class="routes-scroll" :show-scrollbar="false">
          <view class="routes-row">
            <view
              v-for="route in routes"
              :key="route.id"
              class="route-card"
              @tap="openRoute(route)"
            >
              <view class="route-cover">
                <image
                  v-if="route.img || routeFallbackImg(route)"
                  :src="route.img || routeFallbackImg(route)"
                  class="route-img"
                  mode="aspectFill"
                  lazy-load
                />
                <view v-else class="route-img-fallback" />
              </view>
              <view class="route-body">
                <text class="route-title">{{ route.title }}</text>
                <text class="route-meta">{{ route.duration || '半日' }} · {{ route.stops?.length || 0 }}站</text>
              </view>
            </view>
          </view>
        </scroll-view>
      </view>
    </scroll-view>

    <z-tab-bar current="home" />
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onLoad, onShow } from '@dcloudio/uni-app'
import { api } from '../../api/mock.js'
import ZTabBar from '../../components/ZTabBar.vue'
import UNavBar from '../../components/UNavBar.vue'
import { useCityStore } from '../../store/city.js'
import { setAssistantContext, setHomeFeedCache } from '../../api/storage.js'

const cityStore = useCityStore()

const tabBarHeight = ref('80px')
const weather = ref(null)
const defaultEntries = [
  { id: 'place_index', title: '按场所索引' },
  { id: 'nearby_now',  title: '附近适合去' },
  { id: 'hot_routes',  title: '精选路线' },
  { id: 'assistant',   title: '直接咨询' },
]
const entries = ref(defaultEntries)
const nearby = ref([])
const routes = ref([])
const loaded = ref(false)
const feedLoading = ref(false)
const locationError = ref(false)

const nearbyVisible = computed(() => nearby.value.slice(0, 3))

const locText = computed(() => {
  if (cityStore.locating) return '定位中…'
  if (locationError.value) return '需要定位'
  return cityStore.current || '当前位置'
})

const weatherIcon = computed(() => weather.value?.icon || '☀️')
const weatherText = computed(() => {
  if (!weather.value) return '获取中'
  return `${weather.value.cond || ''} ${weather.value.temp != null ? weather.value.temp + '°C' : ''}`.trim()
})

const timeSlot = computed(() => {
  const hour = new Date().getHours()
  if (hour < 11) return '上午'
  if (hour < 14) return '中午'
  if (hour < 18) return '下午'
  return '夜晚'
})

function entryLabel(id) {
  return {
    place_index: '按场所索引',
    nearby_now:  '附近适合去',
    hot_routes:  '精选路线',
    assistant:   '直接咨询',
  }[id] || ''
}

function entryDesc(id) {
  return {
    place_index: '景点、活动、好去处',
    nearby_now:  '5公里以内推荐',
    hot_routes:  '路线规划、节假日推荐',
    assistant:   '智能 AI 出游问答',
  }[id] || ''
}

const ROUTE_FALLBACKS = [
  'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=600',
  'https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?w=600',
  'https://images.unsplash.com/photo-1495774856032-8b90bbb32b32?w=600',
]
function routeFallbackImg(route) {
  if (!route?.id) return ROUTE_FALLBACKS[0]
  const idx = Math.abs(String(route.id).split('').reduce((a, c) => a + c.charCodeAt(0), 0)) % ROUTE_FALLBACKS.length
  return ROUTE_FALLBACKS[idx]
}

function normalizeEntries(feedEntries) {
  const byId = new Map((feedEntries || []).map(item => [item.id, item]))
  return defaultEntries.map(item => ({ ...item, ...(byId.get(item.id) || {}) }))
}

async function loadFeed(intent = '') {
  if (cityStore.locating) return
  cityStore.locating = true
  feedLoading.value = true
  locationError.value = false
  try {
    const coords = await new Promise((resolve, reject) => {
      uni.getLocation({ type: 'gcj02', success: resolve, fail: reject })
    })
    cityStore.locationDenied = false
    cityStore.setCoords(coords.latitude, coords.longitude)

    const feed = await api.getHomeFeed({
      lat: coords.latitude,
      lng: coords.longitude,
      city: cityStore.current,
      intent,
    })
    if (feed?.location?.city) cityStore.setFromLocation(feed.location.city)
    weather.value = feed.weather || null
    entries.value = normalizeEntries(feed.entries)
    nearby.value = (feed.nearby_now || []).filter(p => p.nav_ready && p.lat != null && p.lng != null)
    routes.value = feed.routes || []
    setHomeFeedCache(feed)
    loaded.value = true
  } catch (_) {
    cityStore.locationDenied = true
    locationError.value = true
    weather.value = null
    nearby.value = []
    routes.value = []
    loaded.value = false
  } finally {
    cityStore.locating = false
    feedLoading.value = false
  }
}

onLoad(async () => {
  try {
    const sys = uni.getSystemInfoSync()
    const tabH = (sys.safeAreaInsets?.bottom || 18) + 56
    tabBarHeight.value = tabH + 'px'
  } catch (_) {}
  await loadFeed()
})

onShow(() => {
  if (!loaded.value && !cityStore.locating) loadFeed()
})

function buildAssistantContext() {
  return {
    lat: cityStore.coords?.lat ?? '',
    lng: cityStore.coords?.lng ?? '',
    city: cityStore.current,
    weather: weatherText.value,
    time_slot: timeSlot.value,
  }
}

function goEntry(id) {
  if (id === 'place_index') {
    uni.switchTab({ url: '/pages/scenes/scenes' })
  } else if (id === 'assistant') {
    const context = buildAssistantContext()
    setAssistantContext(context)
    uni.switchTab({
      url: '/pages/assistant/chat',
      success: () => uni.$emit('assistantContext', context),
    })
  } else if (id === 'nearby_now') {
    uni.navigateTo({ url: '/pages/nearby/index' })
  } else if (id === 'hot_routes') {
    goRoutes()
  }
}

function goNearby() {
  uni.navigateTo({ url: '/pages/nearby/index' })
}

function goRoutes() {
  uni.navigateTo({ url: '/pages/routes/routes' })
}

function goPoi(id) {
  const lat = cityStore.coords?.lat
  const lng = cityStore.coords?.lng
  uni.navigateTo({ url: `/pages/poi/detail?id=${id}&lat=${lat || ''}&lng=${lng || ''}` })
}

function openRoute(route) {
  if (!route) return
  try { uni.setStorageSync('currentRoute', route) } catch (_) {}
  uni.navigateTo({ url: '/pages/routes/detail' })
}

function onSearch() {
  uni.showToast({ title: '搜索功能开发中', icon: 'none' })
}
</script>

<style lang="scss">
@import '../../uni.scss';

.page {
  min-height: 100vh;
  background: $u-bg;
}

.scroll-body {
  position: relative;
}

// ── 位置 + 天气 ────────────────────────────────────────────
.loc-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 18rpx 32rpx 14rpx;
  gap: 18rpx;
}

.loc-left {
  display: flex;
  align-items: center;
  gap: 8rpx;
  flex: 1;
  min-width: 0;
}

.loc-pin {
  width: 28rpx;
  height: 28rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loc-text {
  font-size: 26rpx;
  color: $u-text;
  font-weight: 500;
}

.loc-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4rpx;
}

.weather-line {
  display: flex;
  align-items: center;
  gap: 6rpx;
}

.weather-icon { font-size: 24rpx; }

.weather-text {
  font-size: 24rpx;
  color: $u-text;
  font-weight: 500;
}

.radius-text {
  font-size: 20rpx;
  color: $u-text-mute;
}

// ── Mascot card ─────────────────────────────────────────────
.mascot-card {
  margin: 14rpx 32rpx 24rpx;
  background: linear-gradient(135deg, #D7EBE5 0%, #C5E0D6 100%);
  border-radius: 24rpx;
  padding: 22rpx 24rpx;
  display: flex;
  align-items: center;
  gap: 18rpx;
}

.mascot-avatar {
  width: 72rpx;
  height: 72rpx;
  border-radius: 24rpx;
  background: $z-primary;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.mascot-text { flex: 1; min-width: 0; }

.mascot-title {
  display: block;
  font-size: 30rpx;
  font-weight: 800;
  color: $u-text;
  margin-bottom: 4rpx;
}

.mascot-sub {
  display: block;
  font-size: 22rpx;
  color: $u-text-sub;
  line-height: 1.4;
}

// ── 4 入口 ──────────────────────────────────────────────────
.entry-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14rpx;
  padding: 0 32rpx;
}

.entry-card {
  border-radius: 20rpx;
  padding: 22rpx 20rpx 24rpx;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
  min-height: 160rpx;
  cursor: pointer;

  &.tint-place_index { background: $u-tint-beige; }
  &.tint-nearby_now  { background: $u-tint-mint; }
  &.tint-hot_routes  { background: $u-tint-coral; }
  &.tint-assistant   { background: $u-tint-deep; }
}

.entry-icon-wrap {
  width: 56rpx;
  height: 56rpx;
  border-radius: 16rpx;
  background: rgba(255, 255, 255, 0.65);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 6rpx;
}

.entry-label {
  display: block;
  font-size: 28rpx;
  font-weight: 800;
  color: $u-text;
}

.entry-desc {
  display: block;
  font-size: 20rpx;
  color: $u-text-sub;
  line-height: 1.35;
}

// ── 通用 section ───────────────────────────────────────────
.section {
  padding: 28rpx 32rpx 0;
}

.section-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 16rpx;
}

.section-title {
  font-size: 30rpx;
  font-weight: 800;
  color: $u-text;
}

.section-more {
  font-size: 22rpx;
  color: $u-text-mute;
  cursor: pointer;
}

// ── POI 横向卡 ──────────────────────────────────────────────
.poi-list {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}

.poi-card {
  background: $u-bg;
  border-radius: 18rpx;
  padding: 14rpx;
  display: flex;
  gap: 16rpx;
  box-shadow: $u-shadow;
  cursor: pointer;
}

.poi-thumb {
  width: 120rpx;
  height: 120rpx;
  border-radius: 14rpx;
  overflow: hidden;
  flex-shrink: 0;
  background: $u-bg-soft;
}

.poi-thumb-img { width: 100%; height: 100%; }

.poi-thumb-fallback {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40rpx;
  color: $u-text-mute;
}

.poi-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.poi-line1 {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 12rpx;
}

.poi-name {
  font-size: 28rpx;
  font-weight: 800;
  color: $u-text;
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.poi-dist {
  font-size: 22rpx;
  color: $u-text-mute;
  flex-shrink: 0;
}

.poi-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6rpx;
  margin: 4rpx 0;
}

.poi-tag {
  font-size: 18rpx;
  color: #1A7A73;
  background: $u-tint-mint;
  padding: 2rpx 10rpx;
  border-radius: 6rpx;
}

.poi-line3 {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.poi-cat {
  font-size: 20rpx;
  color: $u-text-sub;
}

.poi-rating {
  display: flex;
  align-items: center;
  gap: 4rpx;
}

.rating-star {
  color: #F59E0B;
  font-size: 22rpx;
  line-height: 1;
}

.rating-num {
  font-size: 22rpx;
  color: $u-text;
  font-weight: 600;
}

// ── 精选路线 横滑 ──────────────────────────────────────────
.routes-scroll {
  width: 100%;
  margin: 0 -32rpx;
  padding-left: 32rpx;
}

.routes-row {
  display: flex;
  gap: 16rpx;
  padding-right: 32rpx;
  padding-bottom: 8rpx;
  white-space: nowrap;
}

.route-card {
  width: 240rpx;
  flex-shrink: 0;
  border-radius: 18rpx;
  background: $u-bg;
  overflow: hidden;
  box-shadow: $u-shadow;
  cursor: pointer;
  display: inline-block;
  white-space: normal;
}

.route-cover {
  width: 100%;
  height: 160rpx;
  overflow: hidden;
  background: $u-bg-soft;
}

.route-img { width: 100%; height: 100%; }

.route-img-fallback {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #D7EBE5, #C5E0D6);
}

.route-body { padding: 14rpx; }

.route-title {
  display: block;
  font-size: 24rpx;
  font-weight: 800;
  color: $u-text;
  line-height: 1.2;
  margin-bottom: 6rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.route-meta {
  font-size: 20rpx;
  color: $u-text-mute;
}

// ── Hint / error cards ─────────────────────────────────────
.hint-card {
  background: $u-bg-soft;
  border-radius: 16rpx;
  padding: 24rpx;
  font-size: 24rpx;
  color: $u-text-sub;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16rpx;

  &.mute { color: $u-text-mute; }
}

.hint-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 64rpx;
  padding: 0 32rpx;
  border-radius: 12rpx;
  background: $z-primary;
  color: #fff;
  font-size: 24rpx;
  font-weight: 700;
}
</style>
