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
          <text class="radius-text">默认推荐距离 3-5km</text>
        </view>
      </view>

      <!-- 出游助手 mascot pill -->
      <view class="mascot-card">
        <view class="mascot-avatar">
          <text class="mascot-avatar-text">助</text>
        </view>
        <view class="mascot-text">
          <text class="mascot-title">出游助手</text>
          <text class="mascot-sub">{{ mascotSub }}</text>
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
            <text class="entry-icon">{{ entryIcon(entry.id) }}</text>
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
        <view v-if="fallbackLocationUsed" class="hint-card">
          <text>未获取到定位，当前展示{{ cityStore.current || DEFAULT_CITY }}默认推荐</text>
          <view class="hint-btn" @tap="loadFeed()">重新定位</view>
        </view>
        <view v-if="!nearbyVisible.length" class="hint-card mute">
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
              <image
                :src="poiThumb(poi)"
                class="poi-thumb-img"
                mode="aspectFill"
                lazy-load
                @error="onPoiImageError(poi)"
              />
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
                <text v-if="poi.kb_status" class="poi-tag kb-tag">{{ kbLabel(poi.kb_status) }}</text>
              </view>
              <view class="poi-line3">
                <text class="poi-cat">{{ poi.category || '地点' }}</text>
                <view class="poi-rating">
                  <text class="rating-star">★</text>
                  <text class="rating-num">{{ poi.rating || (4.0 + (poi.id % 10) / 10).toFixed(1) }}</text>
                </view>
                <view class="poi-nav" @tap.stop="navPoi(poi)">导航</view>
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
                  :src="routeThumb(route)"
                  class="route-img"
                  mode="aspectFill"
                  lazy-load
                  @error="onRouteImageError(route)"
                />
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
import { DEFAULT_CITY, useCityStore } from '../../store/city.js'
import { setAssistantContext, setHomeFeedCache } from '../../api/storage.js'
import { poiImage, routeImage } from '../../api/assets.js'

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
const fallbackLocationUsed = ref(false)
const brokenPoiImages = ref({})
const brokenRouteImages = ref({})

const nearbyVisible = computed(() => nearby.value.slice(0, 3))

const locText = computed(() => {
  if (cityStore.locating) return '定位中…'
  if (fallbackLocationUsed.value) return `${cityStore.current || DEFAULT_CITY} · 默认推荐`
  return cityStore.current || '当前位置'
})

const mascotSub = computed(() => (
  fallbackLocationUsed.value
    ? '定位未开启，已先为您准备默认城市出游方式'
    : '已根据您的位置，为您准备了 4 种出游方式'
))

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

function entryIcon(id) {
  return {
    place_index: '址',
    nearby_now:  '近',
    hot_routes:  '线',
    assistant:   '问',
  }[id] || '游'
}

function kbLabel(status) {
  return {
    hit: '知识库',
    unchanged: '知识库',
    partial: '部分收录',
    stale: '待更新',
    miss: '地图来源',
  }[status] || '地图来源'
}

function poiThumb(poi) {
  return poiImage(poi, brokenPoiImages.value[poi?.id])
}

function routeThumb(route) {
  return routeImage(route, brokenRouteImages.value[route?.id])
}

function onPoiImageError(poi) {
  if (!poi?.id) return
  brokenPoiImages.value = { ...brokenPoiImages.value, [poi.id]: true }
}

function onRouteImageError(route) {
  if (!route?.id) return
  brokenRouteImages.value = { ...brokenRouteImages.value, [route.id]: true }
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
  fallbackLocationUsed.value = false
  try {
    let coords
    try {
      coords = await new Promise((resolve, reject) => {
        uni.getLocation({ type: 'gcj02', success: resolve, fail: reject })
      })
      cityStore.locationDenied = false
      cityStore.setCoords(coords.latitude, coords.longitude)
    } catch (_) {
      cityStore.setDefaultLocation()
      locationError.value = true
      fallbackLocationUsed.value = true
      coords = { latitude: cityStore.coords.lat, longitude: cityStore.coords.lng }
    }

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

function navPoi(poi) {
  if (!poi?.lat || !poi?.lng) {
    uni.showToast({ title: '暂无坐标，无法导航', icon: 'none' })
    return
  }
  uni.openLocation({
    latitude: Number(poi.lat),
    longitude: Number(poi.lng),
    name: poi.name,
    address: poi.address || poi.category || '',
  })
}

function openRoute(route) {
  if (!route) return
  try { uni.setStorageSync('currentRoute', route) } catch (_) {}
  uni.navigateTo({ url: '/pages/routes/detail' })
}

function onSearch() {
  const context = { ...buildAssistantContext(), intent: 'search' }
  setAssistantContext(context)
  uni.switchTab({
    url: '/pages/assistant/chat',
    success: () => uni.$emit('assistantContext', context),
  })
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

.mascot-avatar-text {
  color: #fff;
  font-size: 34rpx;
  font-weight: 900;
  line-height: 1;
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

.entry-icon {
  font-size: 28rpx;
  font-weight: 900;
  color: $z-primary;
  line-height: 1;
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

.kb-tag {
  color: $u-text-sub;
  background: $u-bg-soft;
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

.poi-nav {
  height: 42rpx;
  padding: 0 18rpx;
  border-radius: 21rpx;
  background: $z-primary;
  color: $z-card;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20rpx;
  font-weight: 800;
  flex-shrink: 0;
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
  margin-bottom: 16rpx;

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
