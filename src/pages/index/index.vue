<template>
  <view class="page">
    <view class="header" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="header-top">
        <view class="city-btn" @tap="onCityTap">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none">
            <path d="M12 22s-8-7-8-13a8 8 0 1116 0c0 6-8 13-8 13z" stroke="#fff" stroke-width="2"/>
            <circle cx="12" cy="9" r="3" stroke="#fff" stroke-width="2"/>
          </svg>
          <text class="city-name">{{ cityLabel }}</text>
          <svg xmlns="http://www.w3.org/2000/svg" width="11" height="11" viewBox="0 0 24 24" fill="none">
            <path d="M3 12a9 9 0 0115.5-6.4M21 12a9 9 0 01-15.5 6.4M21 3v6h-6M3 21v-6h6" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </view>
        <view v-if="weather" class="weather-pill">
          <text class="weather-icon">{{ weather.icon }}</text>
          <text class="weather-text">{{ weather.temp }}° {{ weather.cond }}</text>
        </view>
      </view>

      <text class="issue-label mono">LOCATION FIRST · TRAVEL ASSISTANT</text>
      <text class="main-title serif">出游助手</text>
      <text class="main-sub">{{ headerSub }}</text>
    </view>

    <scroll-view
      scroll-y
      class="scroll-body"
      :style="{ paddingBottom: tabBarHeight }"
      :scroll-into-view="scrollTarget"
      scroll-with-animation
      :show-scrollbar="false"
    >
      <view v-if="feedLoading && !loaded" class="locating-panel">
        <view class="locating-pulse">
          <text>⌖</text>
        </view>
        <text class="locating-title serif">正在获取当前位置</text>
        <text class="locating-sub">定位成功后，会立即推荐附近可导航的目的地。</text>
      </view>

      <view v-else-if="locationError" class="location-gate">
        <text class="gate-title serif">需要开启定位后，才能推荐附近目的地</text>
        <text class="gate-sub">系统不会在未定位时展示假附近数据。</text>
        <view class="gate-actions">
          <view class="primary-btn" @tap="loadFeed()">重新定位</view>
          <view class="secondary-btn" @tap="goEntry('place_index')">按场所索引</view>
        </view>
      </view>

      <template v-else>
        <view class="assistant-home">
          <view class="summary-grid">
            <view class="summary-item">
              <text class="summary-label mono">当前位置</text>
              <text class="summary-city serif">{{ cityStore.current }}</text>
            </view>
            <view class="summary-item">
              <text class="summary-label mono">附近位置</text>
              <text class="summary-value">{{ locationText }}</text>
            </view>
            <view class="summary-item">
              <text class="summary-label mono">天气</text>
              <text class="summary-value">{{ weatherText }}</text>
            </view>
            <view class="summary-item">
              <text class="summary-label mono">默认推荐距离</text>
              <text class="summary-value">{{ radiusText }}</text>
            </view>
          </view>
          <text class="assistant-home-kicker mono">TRAVEL ASSISTANT</text>
          <text class="assistant-home-title serif">出游助手</text>
          <text class="assistant-home-sub">选择一个入口，进入推荐结果、路线或咨询。</text>
          <text class="intent-title serif">你现在想怎么出去玩？</text>
          <view class="intent-grid">
            <view
              v-for="entry in entries"
              :key="entry.id"
              class="intent-card"
              @tap="goEntry(entry.id)"
            >
              <text class="intent-icon">{{ entryIcon(entry.id) }}</text>
              <text class="intent-label">{{ entry.title }}</text>
            </view>
          </view>
        </view>

        <view id="nearby_now" class="section">
          <z-section-header
            no="01"
            title="附近推荐"
            sub="定位后实时推荐可导航目的地"
            action="换一批"
            @action="refreshNearby"
          />
          <view v-if="!nearbyVisible.length" class="list-empty mono">暂无附近推荐</view>
          <view class="poi-list">
            <view
              v-for="poi in nearbyVisible"
              :key="poi.id"
              class="poi-card"
              @tap="goPoi(poi.id)"
            >
              <view class="poi-score">
                <text class="score-num">{{ poi.score }}</text>
                <text class="score-label">推荐</text>
              </view>
              <view class="poi-content">
                <view class="poi-header-row">
                  <view class="poi-title-wrap">
                    <text class="poi-name serif">{{ poi.name }}</text>
                    <text class="poi-cat">{{ poi.category || '地点' }} · {{ poi.distance }}</text>
                  </view>
                  <text class="poi-time">{{ poi.drive_time || '可导航' }}</text>
                </view>
                <text class="poi-reason" :numberOfLines="2">{{ poi.reason }}</text>
                <view class="poi-tags">
                  <z-tag
                    v-for="tag in poi.tags.slice(0, 4)"
                    :key="tag"
                    :label="tag"
                    color="#0D4F4A"
                    :small="true"
                  />
                  <text class="kb-badge mono">{{ poi.kb_status }}</text>
                </view>
                <view class="poi-actions">
                  <text class="source-note">{{ poi.source === 'kb' ? '知识库推荐' : '地图数据推荐' }}</text>
                  <view class="nav-btn" :class="{ disabled: !poi.nav_ready }" @tap.stop="openNav(poi)">导航</view>
                </view>
              </view>
            </view>
          </view>
        </view>

        <view id="routes" class="section">
          <z-section-header
            no="02"
            title="路线推荐"
            sub="2小时 / 半日 / 一日精选路线"
            action="全部"
            @action="goRoutes"
          />
          <view v-if="!routes.length" class="list-empty mono">暂无精选路线</view>
          <view class="routes-list">
            <view
              v-for="route in routes.slice(0, 3)"
              :key="route.id"
              class="route-card location-route"
              @tap="goRoutes"
            >
              <view class="route-body">
                <view class="route-head">
                  <view>
                    <text class="route-title serif">{{ route.title }}</text>
                    <text class="route-summary" :numberOfLines="2">{{ route.summary }}</text>
                  </view>
                  <text class="route-duration">{{ route.duration }}</text>
                </view>
                <view class="route-stops">
                  <view v-for="stop in route.stops.slice(0, 3)" :key="stop.name" class="route-stop">
                    <text class="stop-dot" />
                    <text class="stop-name">{{ stop.name }}</text>
                    <text class="stop-dist">{{ stop.distance }}</text>
                  </view>
                </view>
                <view class="poi-actions">
                  <text class="source-note">{{ route.budget ? '预算 ' + route.budget : '附近路线' }}</text>
                  <view class="nav-btn" @tap.stop="openRoute(route)">查看详情</view>
                </view>
              </view>
            </view>
          </view>
        </view>
      </template>
    </scroll-view>

    <z-tab-bar current="home" />
  </view>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { onLoad, onShow } from '@dcloudio/uni-app'
import { api } from '../../api/mock.js'
import ZSectionHeader from '../../components/ZSectionHeader.vue'
import ZTag from '../../components/ZTag.vue'
import ZTabBar from '../../components/ZTabBar.vue'
import { useCityStore } from '../../store/city.js'
import { setAssistantContext, setHomeFeedCache } from '../../api/storage.js'

const cityStore = useCityStore()

const statusBarHeight = ref(44)
const tabBarHeight = ref('80px')
const weather = ref(null)
const defaultEntries = [
  { id: 'place_index', title: '按场所索引' },
  { id: 'nearby_now', title: '附近现在适合去' },
  { id: 'hot_routes', title: '精选路线' },
  { id: 'assistant', title: '直接咨询' },
]
const entries = ref(defaultEntries)
const nearby = ref([])
const routes = ref([])
const loaded = ref(false)
const feedLoading = ref(false)
const locationError = ref(false)
const nearbyPage = ref(0)
const scrollTarget = ref('')
const radiusText = '3-5km'

const nearbyVisible = computed(() => {
  if (!nearby.value.length) return []
  const start = (nearbyPage.value * 3) % nearby.value.length
  return nearby.value.slice(start, start + 3).concat(
    nearby.value.slice(0, Math.max(0, start + 3 - nearby.value.length))
  ).slice(0, 3)
})

const cityLabel = computed(() => {
  if (cityStore.locating) return '定位中…'
  if (locationError.value) return '需要定位'
  return cityStore.current
})

const locationText = computed(() => {
  const lat = cityStore.coords?.lat
  const lng = cityStore.coords?.lng
  if (lat == null || lng == null) return '定位成功'
  return `${Number(lat).toFixed(4)}, ${Number(lng).toFixed(4)}`
})

const weatherText = computed(() => {
  if (!weather.value) return '定位后获取'
  return `${weather.value.icon || ''}${weather.value.temp}° ${weather.value.cond}`
})

const timeSlot = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6) return '凌晨'
  if (hour < 11) return '上午'
  if (hour < 14) return '中午'
  if (hour < 18) return '下午'
  if (hour < 22) return '晚上'
  return '深夜'
})

const headerSub = computed(() => {
  if (locationError.value) return '开启定位后推荐附近目的地'
  if (loaded.value) return `${cityStore.current} · ${weather.value?.advice ?? '已定位'} · ${radiusText}`
  return '获取定位中…'
})

function normalizeEntries(feedEntries) {
  const byId = new Map((feedEntries || []).map(item => [item.id, item]))
  return defaultEntries.map(item => ({ ...item, ...(byId.get(item.id) || {}), title: item.title }))
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
    nearbyPage.value = 0
    setHomeFeedCache(feed)
    loaded.value = true
  } catch (_) {
    cityStore.locationDenied = true
    locationError.value = true
    weather.value = null
    nearby.value = []
    routes.value = []
    loaded.value = false
    uni.showToast({ title: '需要开启定位后推荐附近目的地', icon: 'none' })
  } finally {
    cityStore.locating = false
    feedLoading.value = false
  }
}

onLoad(async () => {
  try {
    const sys = uni.getSystemInfoSync()
    statusBarHeight.value = sys.statusBarHeight || 44
    const tabH = (sys.safeAreaInsets?.bottom || 18) + 56
    tabBarHeight.value = tabH + 'px'
  } catch (_) {}
  await loadFeed()
})

onShow(() => {
  if (!loaded.value && !cityStore.locating) loadFeed()
})

function onCityTap() {
  uni.showLoading({ title: '重新定位中…' })
  loadFeed().finally(() => {
    uni.hideLoading()
    if (!locationError.value) {
      uni.showToast({ title: `当前定位：${cityStore.current}`, icon: 'none' })
    }
  })
}

function refreshNearby() {
  if (!nearby.value.length) return
  nearbyPage.value = (nearbyPage.value + 1) % Math.ceil(nearby.value.length / 3)
}

function scrollToSection(id) {
  scrollTarget.value = ''
  nextTick(() => {
    scrollTarget.value = id
  })
}

function entryIcon(id) {
  return {
    place_index: '□',
    nearby_now: '⌖',
    hot_routes: '↱',
    assistant: '＋',
  }[id] || '•'
}

function goEntry(id) {
  if (id === 'place_index') {
    const context = buildAssistantContext()
    uni.switchTab({
      url: '/pages/scenes/scenes',
      success: () => uni.$emit('homeLocationContext', context),
    })
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

function buildAssistantContext() {
  return {
    lat: cityStore.coords?.lat ?? '',
    lng: cityStore.coords?.lng ?? '',
    city: cityStore.current,
    weather: weatherText.value,
    time_slot: timeSlot.value,
  }
}

function buildContextQuery() {
  const context = buildAssistantContext()
  return '?' + Object.keys(context)
    .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(context[key])}`)
    .join('&')
}

function goRoutes() {
  uni.navigateTo({ url: `/pages/routes/routes${buildContextQuery()}` })
}

function goPoi(id) {
  const lat = cityStore.coords?.lat
  const lng = cityStore.coords?.lng
  uni.navigateTo({ url: `/pages/poi/detail?id=${id}&lat=${lat || ''}&lng=${lng || ''}` })
}

function openNav(poi) {
  if (!poi?.nav_ready || poi.lat == null || poi.lng == null) {
    uni.showToast({ title: '该地点暂无可用坐标', icon: 'none' })
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
</script>

<style lang="scss">
@import '../../uni.scss';

.page {
  min-height: 100vh;
  background: $z-bg;
}

.list-empty {
  color: $z-muted;
  font-family: $mono;
  font-size: $font-mono;
  padding: 20rpx 0;
  display: block;
}

// ── Header ──────────────────────────────────────────────────
.header {
  background: linear-gradient(180deg, $z-primary 0%, $z-primary 70%, $z-bg 100%);
  padding: 0 32rpx 48rpx;
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 28rpx;
  padding-top: 16rpx;
}

.city-btn {
  display: flex;
  align-items: center;
  gap: 10rpx;
  cursor: pointer;
}

.city-name {
  color: $z-card;
  font-size: 28rpx;
  font-weight: 700;
}

.weather-pill {
  display: flex;
  align-items: center;
  gap: 10rpx;
  background: rgba(255, 255, 255, 0.15);
  border-radius: $radius-pill;
  padding: 8rpx 20rpx;
}

.weather-icon { font-size: 26rpx; }

.weather-text {
  color: $z-card;
  font-size: 24rpx;
  font-weight: 600;
}

.issue-label {
  display: block;
  font-size: 20rpx;
  color: rgba(255, 255, 255, 0.55);
  letter-spacing: 3rpx;
  margin-bottom: 10rpx;
}

.main-title {
  display: block;
  color: $z-card;
  font-size: 48rpx;
  font-weight: 900;
  letter-spacing: 2rpx;
  margin-bottom: 10rpx;
}

.main-sub {
  display: block;
  color: rgba(255, 255, 255, 0.65);
  font-size: 24rpx;
}

// ── 滚动区 ──────────────────────────────────────────────────
.scroll-body {
  position: relative;
}

// ── AI 输入卡 ───────────────────────────────────────────────
.ai-card-wrap {
  margin: -36rpx 28rpx 0;
  position: relative;
  z-index: 2;
}

.ai-card {
  background: $z-card;
  border-radius: 28rpx;
  padding: 24rpx 28rpx;
  box-shadow: 0 16rpx 48rpx rgba(13, 79, 74, 0.12);
  display: flex;
  align-items: center;
  gap: 20rpx;
  cursor: pointer;
}

.ai-icon {
  width: 68rpx;
  height: 68rpx;
  border-radius: 34rpx;
  background: linear-gradient(135deg, $z-accent 0%, $z-accent-l 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.ai-content {
  flex: 1;
  min-width: 0;
}

.ai-title {
  display: block;
  font-size: 27rpx;
  font-weight: 700;
  color: $z-text;
  margin-bottom: 4rpx;
}

.ai-hint {
  display: block;
  font-size: 21rpx;
  color: $z-muted;
}

.ai-btn {
  background: $z-primary;
  border-radius: 18rpx;
  padding: 10rpx 18rpx;
  flex-shrink: 0;
}

.ai-btn-text {
  color: $z-card;
  font-size: 23rpx;
  font-weight: 700;
}

// ── 通用 Section 间距 ────────────────────────────────────────
.section {
  padding: 36rpx 32rpx 0;
}

// ── §01 场景宫格 ─────────────────────────────────────────────
.scenes-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16rpx;
}

.scene-card {
  background: $z-card;
  border-radius: 22rpx;
  padding: 24rpx 18rpx;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 14rpx;
  cursor: pointer;
  box-shadow: 0 2rpx 8rpx rgba(13, 79, 74, 0.05);
  position: relative;
}

.scene-no {
  position: absolute;
  top: 14rpx;
  right: 18rpx;
  font-size: 18rpx;
  color: $z-muted;
  letter-spacing: 1rpx;
  font-weight: 700;
}

.scene-icon-bg {
  width: 68rpx;
  height: 68rpx;
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.scene-icon-emoji {
  font-size: 36rpx;
}

.scene-info {
  width: 100%;
}

.scene-label {
  display: block;
  font-size: 25rpx;
  font-weight: 700;
  color: $z-text;
  line-height: 1.2;
  margin-bottom: 4rpx;
}

.scene-desc {
  display: block;
  font-size: 19rpx;
  color: $z-muted;
}

// ── §02 POI 卡片 ─────────────────────────────────────────────
.poi-list {
  display: flex;
  flex-direction: column;
  gap: 18rpx;
}

.poi-card {
  background: $z-card;
  border-radius: 26rpx;
  padding: 22rpx;
  box-shadow: 0 2rpx 12rpx rgba(13, 79, 74, 0.06);
  display: flex;
  gap: 22rpx;
  cursor: pointer;
}

.poi-img-wrap {
  width: 160rpx;
  height: 160rpx;
  border-radius: 20rpx;
  overflow: hidden;
  flex-shrink: 0;
  position: relative;
}

.poi-img {
  width: 100%;
  height: 100%;
}

.poi-dist-badge {
  position: absolute;
  bottom: 8rpx;
  left: 8rpx;
  background: rgba(0, 0, 0, 0.55);
  color: $z-card;
  font-size: 18rpx;
  padding: 3rpx 10rpx;
  border-radius: $radius-pill;
}

.poi-content {
  flex: 1;
  min-width: 0;
}

.poi-header-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12rpx;
  margin-bottom: 6rpx;
}

.poi-no {
  display: block;
  font-size: 19rpx;
  color: $z-muted;
  letter-spacing: 1rpx;
  margin-bottom: 4rpx;
}

.poi-name {
  display: block;
  font-size: 29rpx;
  font-weight: 800;
  color: $z-text;
  line-height: 1.2;
}

.poi-time {
  font-size: 20rpx;
  color: $z-muted;
  white-space: nowrap;
  margin-top: 4rpx;
}

.poi-cat {
  display: block;
  font-size: 21rpx;
  color: $z-muted;
  margin-bottom: 10rpx;
}

.poi-reason {
  display: block;
  font-size: 23rpx;
  color: $z-text2;
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 12rpx;
}

.poi-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8rpx;
}

// ── §03 路线横滑 ─────────────────────────────────────────────
.routes-scroll {
  width: 100%;
}

.routes-row {
  display: flex;
  gap: 20rpx;
  padding-bottom: 8rpx;
  white-space: nowrap;
}

.route-card {
  min-width: 440rpx;
  flex-shrink: 0;
  background: $z-card;
  border-radius: 26rpx;
  overflow: hidden;
  box-shadow: 0 2rpx 12rpx rgba(13, 79, 74, 0.06);
  cursor: pointer;
  display: inline-block;
  white-space: normal;
}

.route-cover {
  height: 200rpx;
  position: relative;
  overflow: hidden;
}

.route-img {
  width: 100%;
  height: 100%;
}

.route-no-badge {
  position: absolute;
  top: 16rpx;
  left: 22rpx;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 10rpx;
  padding: 4rpx 14rpx;
  font-size: 20rpx;
  font-weight: 700;
  letter-spacing: 1rpx;
}

.route-cover-title {
  position: absolute;
  bottom: 16rpx;
  left: 22rpx;
  color: $z-card;
  font-size: 28rpx;
  font-weight: 800;
  text-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.5);
}

.route-body {
  padding: 18rpx 22rpx;
}

.route-summary {
  display: block;
  font-size: 22rpx;
  color: $z-muted;
  line-height: 1.5;
  margin-bottom: 12rpx;
  // 2 行截断（H5/WXML 均支持）
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.route-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.route-meta-text {
  font-size: 20rpx;
  color: $z-muted;
}

// ── 越用越准横幅 ─────────────────────────────────────────────
.tip-banner {
  margin: 28rpx 32rpx 0;
  background: linear-gradient(135deg, rgba(244, 185, 66, 0.13) 0%, rgba(255, 107, 53, 0.07) 100%);
  border: 1rpx solid rgba(244, 185, 66, 0.27);
  border-radius: 26rpx;
  padding: 24rpx 28rpx;
  display: flex;
  align-items: center;
  gap: 22rpx;
}

.tip-icon {
  font-size: 44rpx;
}

.tip-content {
  flex: 1;
}

.tip-title {
  display: block;
  font-size: 26rpx;
  font-weight: 800;
  color: $z-text;
  margin-bottom: 4rpx;
}

.tip-sub {
  display: block;
  font-size: 22rpx;
  color: $z-muted;
}

// ── 定位兜底 ────────────────────────────────────────────────
.location-gate {
  margin: -28rpx 32rpx 0;
  background: $z-card;
  border-radius: $radius-card;
  padding: 34rpx 32rpx;
  box-shadow: 0 12rpx 36rpx rgba(13, 79, 74, 0.12);
}

.gate-title {
  display: block;
  font-size: 34rpx;
  font-weight: 900;
  color: $z-text;
  line-height: 1.25;
  margin-bottom: 10rpx;
}

.gate-sub {
  display: block;
  font-size: 24rpx;
  color: $z-muted;
  line-height: 1.45;
  margin-bottom: 26rpx;
}

.gate-actions {
  display: flex;
  gap: 16rpx;
}

.primary-btn,
.secondary-btn,
.nav-btn {
  height: 64rpx;
  padding: 0 24rpx;
  border-radius: 12rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24rpx;
  font-weight: 800;
}

.primary-btn,
.nav-btn {
  color: $z-card;
  background: $z-primary;
}

.secondary-btn {
  color: $z-primary;
  background: rgba(13, 79, 74, 0.08);
}

.nav-btn.disabled {
  background: $z-muted;
}

// ── 四入口 ─────────────────────────────────────────────────
.intent-wrap {
  margin: -36rpx 28rpx 0;
  position: relative;
  z-index: 2;
  background: $z-card;
  border-radius: $radius-card;
  padding: 26rpx;
  box-shadow: 0 16rpx 48rpx rgba(13, 79, 74, 0.12);
}

.intent-title {
  display: block;
  font-size: 30rpx;
  font-weight: 900;
  color: $z-text;
  margin-bottom: 18rpx;
}

.intent-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14rpx;
}

.intent-card {
  min-height: 104rpx;
  border-radius: 16rpx;
  background: $z-bg;
  border: 1rpx solid $z-border;
  padding: 18rpx;
  display: flex;
  align-items: center;
  gap: 14rpx;
}

.intent-icon {
  width: 48rpx;
  height: 48rpx;
  border-radius: 14rpx;
  background: $z-primary;
  color: $z-card;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
  font-weight: 900;
}

.intent-label {
  flex: 1;
  min-width: 0;
  font-size: 24rpx;
  font-weight: 800;
  color: $z-text;
  line-height: 1.25;
}

// ── 定位推荐卡 ─────────────────────────────────────────────
.poi-score {
  width: 92rpx;
  height: 92rpx;
  border-radius: 18rpx;
  background: rgba(13, 79, 74, 0.08);
  color: $z-primary;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.score-num {
  font-size: 30rpx;
  font-weight: 900;
  line-height: 1;
}

.score-label {
  font-size: 18rpx;
  margin-top: 4rpx;
}

.poi-title-wrap {
  flex: 1;
  min-width: 0;
}

.poi-reason {
  white-space: normal;
}

.kb-badge {
  padding: 4rpx 10rpx;
  border-radius: 8rpx;
  background: rgba(13, 79, 74, 0.08);
  color: $z-primary;
  font-size: 18rpx;
}

.poi-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16rpx;
  margin-top: 16rpx;
}

.source-note {
  flex: 1;
  min-width: 0;
  font-size: 21rpx;
  color: $z-muted;
}

// ── 路线列表 ────────────────────────────────────────────────
.routes-list {
  display: flex;
  flex-direction: column;
  gap: 18rpx;
}

.routes-list .route-card {
  min-width: 0;
  width: 100%;
  display: block;
}

.location-route {
  white-space: normal;
}

.route-head {
  display: flex;
  justify-content: space-between;
  gap: 20rpx;
  margin-bottom: 16rpx;
}

.route-title {
  display: block;
  font-size: 30rpx;
  font-weight: 900;
  color: $z-text;
  margin-bottom: 8rpx;
}

.route-duration {
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

.route-stops {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}

.route-stop {
  display: flex;
  align-items: center;
  gap: 12rpx;
  min-height: 36rpx;
}

.stop-dot {
  width: 12rpx;
  height: 12rpx;
  border-radius: 6rpx;
  background: $z-primary;
  flex-shrink: 0;
}

.stop-name {
  flex: 1;
  min-width: 0;
  font-size: 24rpx;
  color: $z-text2;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.stop-dist {
  font-size: 21rpx;
  color: $z-muted;
  flex-shrink: 0;
}

// ── 首页体验重排：定位优先、入口清晰 ─────────────────────────
.header {
  background: $z-primary;
  padding: 0 32rpx 72rpx;
}

.header-top {
  margin-bottom: 34rpx;
}

.issue-label {
  color: rgba(255, 255, 255, 0.62);
  letter-spacing: 1.5rpx;
}

.main-title {
  font-size: 46rpx;
  letter-spacing: 0;
}

.main-sub {
  max-width: 640rpx;
  line-height: 1.45;
}

.locating-panel {
  margin: -46rpx 28rpx 0;
  background: $z-card;
  border-radius: 20rpx;
  padding: 48rpx 34rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  box-shadow: 0 14rpx 42rpx rgba(13, 79, 74, 0.14);
}

.locating-pulse {
  width: 96rpx;
  height: 96rpx;
  border-radius: 48rpx;
  background: rgba(13, 79, 74, 0.1);
  color: $z-primary;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 44rpx;
  font-weight: 900;
  margin-bottom: 24rpx;
}

.locating-title {
  font-size: 34rpx;
  font-weight: 900;
  color: $z-text;
  margin-bottom: 8rpx;
}

.locating-sub {
  font-size: 24rpx;
  color: $z-muted;
  line-height: 1.5;
}

.assistant-home {
  margin: -46rpx 28rpx 0;
  position: relative;
  z-index: 2;
  background: $z-card;
  border-radius: 20rpx;
  padding: 26rpx;
  box-shadow: 0 14rpx 42rpx rgba(13, 79, 74, 0.14);
}

.assistant-home-kicker {
  display: block;
  color: $z-muted;
  font-size: 18rpx;
  margin-bottom: 6rpx;
}

.assistant-home-title {
  display: block;
  color: $z-text;
  font-size: 36rpx;
  font-weight: 900;
  margin-bottom: 6rpx;
}

.assistant-home-sub {
  display: block;
  color: $z-muted;
  font-size: 23rpx;
  line-height: 1.45;
  margin-bottom: 22rpx;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12rpx;
  padding-bottom: 22rpx;
  margin-bottom: 22rpx;
  border-bottom: 1rpx solid $z-border;
}

.summary-item {
  min-height: 96rpx;
  border-radius: 14rpx;
  background: $z-bg;
  padding: 16rpx;
}

.location-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 18rpx;
  padding-bottom: 22rpx;
  margin-bottom: 22rpx;
  border-bottom: 1rpx solid $z-border;
}

.summary-label {
  display: block;
  color: $z-muted;
  font-size: 18rpx;
  margin-bottom: 4rpx;
}

.summary-city {
  display: block;
  color: $z-text;
  font-size: 30rpx;
  font-weight: 900;
  line-height: 1.2;
}

.summary-value {
  display: block;
  color: $z-text;
  font-size: 24rpx;
  font-weight: 800;
  line-height: 1.3;
  word-break: break-all;
}

.summary-weather {
  height: 56rpx;
  padding: 0 18rpx;
  border-radius: 12rpx;
  background: rgba(13, 79, 74, 0.08);
  color: $z-primary;
  display: flex;
  align-items: center;
  gap: 8rpx;
  font-size: 23rpx;
  font-weight: 800;
  flex-shrink: 0;
}

.intent-wrap,
.location-gate {
  border-radius: 20rpx;
}

.intent-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10rpx;
}

.intent-card {
  min-height: 132rpx;
  padding: 16rpx 10rpx;
  flex-direction: column;
  justify-content: center;
  text-align: center;
  gap: 12rpx;
}

.intent-icon {
  border-radius: 12rpx;
  font-size: 26rpx;
}

.intent-label {
  font-size: 21rpx;
  line-height: 1.25;
}

.section {
  padding-top: 30rpx;
}

.poi-card,
.route-card,
.scene-card {
  border-radius: 16rpx;
  box-shadow: 0 2rpx 10rpx rgba(13, 79, 74, 0.05);
}

.poi-card {
  padding: 20rpx;
}

.poi-score {
  width: 84rpx;
  height: 84rpx;
  border-radius: 16rpx;
}

.poi-name {
  font-size: 28rpx;
}

.nav-btn {
  min-width: 108rpx;
  height: 58rpx;
  border-radius: 10rpx;
}
</style>
