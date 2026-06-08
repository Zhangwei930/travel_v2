<template>
  <view class="cy-page">
    <!-- Header -->
    <view class="cy-home-header" :style="{ paddingTop: statusBarH + 'px' }">
      <view class="cy-hh-left">
        <view class="cy-hh-weather">
          <view class="cy-weather-icon">
            <CyIcon name="sun" :size="36" />
          </view>
          <text class="cy-weather-text">{{ weatherText }}</text>
          <text class="cy-hh-range">· 15公里内推荐</text>
        </view>
        <view class="cy-hh-loc" @tap="onSearch">
          <CyIcon name="pin-outline-green" :size="26" />
          <text class="cy-hh-loc-text">{{ locText }}</text>
        </view>
      </view>
    </view>

    <scroll-view scroll-y class="cy-scroll" :style="{ paddingBottom: tabBarH }" :show-scrollbar="false">

      <!-- 大卡块：出游助手 → 你的位置 → 4入口 -->
      <view class="cy-section-head cy-entry-section-head">
        <text class="cy-section-title">出游助手</text>
      </view>
      <view class="cy-entry-block">
        <text class="cy-et-subtitle">已根据你的位置，为你准备了4种出游方式</text>
        <view class="cy-entry-grid">
          <cy-entry-card icon-type="place"  title="按场所索引"   desc="景点 / 周边 / 趣游"   @tap="goEntry('place_index')" />
          <cy-entry-card icon-type="nearby" title="附近现在适合去" desc="短距离 / 即刻推荐"  @tap="goEntry('nearby_now')" />
          <cy-entry-card icon-type="routes" title="精选路线"     desc="2小时 / 半日 / 一日" @tap="goEntry('hot_routes')" />
          <cy-entry-card v-if="consultOn" icon-type="chat" title="直接咨询" desc="告诉我你的需求" @tap="goEntry('assistant')" />
        </view>
      </view>

      <!-- 附近现在适合去 -->
      <view class="cy-section">
        <view class="cy-section-head">
          <text class="cy-section-title">附近现在适合去</text>
          <text class="cy-section-more" @tap="goNearby">更多 ›</text>
        </view>
        <view v-if="locationError" class="cy-hint-card">
          <text>未获取到定位，请开启位置权限后获取附近真实推荐</text>
          <view class="cy-hint-actions">
            <view class="cy-hint-btn" @tap="retryLocation">重新定位</view>
            <view class="cy-hint-btn cy-hint-btn--ghost" @tap="useDefaultFeed">使用默认城市</view>
          </view>
        </view>
        <view v-else-if="feedError" class="cy-hint-card">
          <text>附近推荐加载失败，请检查网络后重试</text>
          <view class="cy-hint-btn" @tap="retryLocation">重新加载</view>
        </view>
        <view v-else-if="fallbackUsed" class="cy-hint-card">
          <text>已按{{ cityStore.current || '成都' }}生成默认推荐，开启定位可获得附近真实推荐</text>
          <view class="cy-hint-btn" @tap="retryLocation">重新定位</view>
        </view>
        <view class="cy-nearby-card">
          <view v-if="feedLoading && !nearbyVisible.length" class="cy-hint-muted"><text>正在加载附近推荐…</text></view>
          <view v-else-if="!nearbyVisible.length && !feedLoading" class="cy-hint-muted"><text>附近暂无可推荐地点</text></view>
          <view
            v-for="(poi, i) in nearbyVisible"
            :key="poi.id"
            class="cy-nearby-row"
            :class="{ 'cy-nearby-row--divider': i > 0 }"
            @tap="goPoi(poi.id)"
          >
            <image :src="poiThumb(poi)" class="cy-nearby-thumb" mode="aspectFill" lazy-load @error="onPoiImageError(poi)" />
            <view class="cy-nearby-body">
              <text class="cy-nearby-name">{{ poi.name }}</text>
              <view class="cy-nearby-tags">
                <text v-for="tag in (poi.tags || []).slice(0, 3)" :key="tag" class="cy-nearby-tag">{{ tag }}</text>
              </view>
            </view>
            <view class="cy-nearby-right">
              <text class="cy-nearby-dist">{{ poi.distance }}</text>
              <view class="cy-nearby-rating">
                <CyIcon name="star-yellow" :size="26" />
                <text class="cy-nearby-rnum">{{ (poi.rating || (4.0 + (poi.id % 10) / 10)).toFixed(1) }}</text>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 精选路线 横滑 -->
      <view class="cy-section">
        <view class="cy-section-head">
          <text class="cy-section-title">精选路线</text>
          <text class="cy-section-more" @tap="goRoutes()">更多 ›</text>
        </view>
        <view v-if="feedLoading && !loaded" class="cy-hint-muted"><text>正在加载精选路线…</text></view>
        <view v-else class="cy-routes-card">
          <view class="cy-routes-row">
            <cy-route-card
              v-for="entry in loaded ? routeDurationEntries : []"
              :key="entry.id"
              :title="entry.title"
              :sub="entry.sub"
              :stops="entry.stops"
              @tap="goRoutes(entry.id)"
            />
          </view>
        </view>
      </view>

      <view style="height: 32rpx;" />
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onLoad, onShow } from '@dcloudio/uni-app'
import { api } from '../../api/index.js'
import CyEntryCard from '../../components/cy/cy-entry-card.vue'
import CyRouteCard from '../../components/cy/cy-route-card.vue'
import CyIcon from '../../components/cy/cy-icon.vue'
import { useCityStore } from '../../store/city.js'
import { setAssistantContext, setHomeFeedCache } from '../../api/storage.js'
import { poiImage } from '../../api/assets.js'
import { setTabBarSelected } from '../../api/tabbar.js'

const cityStore = useCityStore()
const statusBarH = ref(44)
const tabBarH = ref('80px')
const weather = ref(null)
const nearby = ref([])
const feedLoading = ref(false)
const loaded = ref(false)
const fallbackUsed = ref(false)
const locationError = ref(false)
const feedError = ref(false)   // 定位成功但 feed 请求失败（网络/超时），区别于定位失败
const brokenPoi = ref({})
const landmark = ref('')
const consultOn = ref(false)   // 在线咨询入口开关（后台控制）
function readConsultFlag() { try { consultOn.value = uni.getStorageSync('zhoumi_consult_on') === true } catch (_) {} }

const routeDurationEntries = [
  { id: '2h', title: '2小时游', sub: '短线组合 · 多条路线可选', stops: 2 },
  { id: 'half', title: '半日游', sub: '半天安排 · 多条路线可选', stops: 3 },
  { id: 'day', title: '一日游', sub: '全天串联 · 多条路线可选', stops: 5 },
]

const nearbyVisible = computed(() => nearby.value.slice(0, 3))
const homeFeedCity = computed(() => (cityStore.source === 'default' ? cityStore.current : ''))

const locText = computed(() => {
  if (cityStore.locating) return '定位中…'
  if (locationError.value) return '需要开启定位'
  if (!cityStore.coords) return '获取位置中…'
  if (fallbackUsed.value || cityStore.source === 'default') return `${cityStore.current || '成都'} · 默认推荐`
  const city = cityStore.current || '当前位置'
  return landmark.value ? `${city} · ${landmark.value}附近` : `${city} · 附近`
})

// mascotSub 已废弃（机器人 + 引导文字已删除），保留为不抛错的空值以兼容未观察到的外部引用
const mascotSub = computed(() =>
  locationError.value
    ? ''
    : fallbackUsed.value
    ? ''
    : ''
)

const weatherText = computed(() => {
  if (!weather.value) return ''
  return `${weather.value.cond || ''} ${weather.value.temp != null ? weather.value.temp + '°C' : ''}`.trim()
})

const timeSlot = computed(() => {
  const h = new Date().getHours()
  if (h < 11) return '上午'
  if (h < 14) return '中午'
  if (h < 18) return '下午'
  return '夜晚'
})

function poiThumb(poi) { return poiImage(poi, brokenPoi.value[poi?.id]) }
function onPoiImageError(poi) { if (poi?.id) brokenPoi.value = { ...brokenPoi.value, [poi.id]: (brokenPoi.value[poi.id] || 0) + 1 } }

async function loadFeed(options = {}) {
  if (cityStore.locating) return
  cityStore.locating = true
  feedLoading.value = true
  locationError.value = false
  feedError.value = false
  fallbackUsed.value = options.useDefault === true
  try {
    let coords
    if (options.useDefault) {
      cityStore.setDefaultLocation()
      coords = { latitude: cityStore.coords.lat, longitude: cityStore.coords.lng }
    } else if (cityStore.hasRealLocation && !options.forceLocate) {
      coords = { latitude: cityStore.coords.lat, longitude: cityStore.coords.lng }
    } else {
      coords = await new Promise((resolve, reject) => {
        uni.getLocation({ type: 'gcj02', success: resolve, fail: reject })
      })
      cityStore.locationDenied = false
      cityStore.setCoords(coords.latitude, coords.longitude)
    }
    const feed = await api.getHomeFeed({
      lat: coords.latitude,
      lng: coords.longitude,
      city: homeFeedCity.value,
    })
    if (feed?.location?.city) cityStore.setFromLocation(feed.location.city)
    if (feed?.location?.landmark) {
      landmark.value = feed.location.landmark
      cityStore.landmark = feed.location.landmark
      try { uni.setStorageSync('zhoumi_landmark', feed.location.landmark) } catch (_) {}
    }
    weather.value = feed.weather || null
    nearby.value = (feed.nearby_now || []).filter(p => p.nav_ready && p.lat != null && p.lng != null)
    setHomeFeedCache(feed)
    loaded.value = true
  } catch (err) {
    if (!options.useDefault && !cityStore.hasRealLocation) {
      locationError.value = true
      cityStore.locationDenied = true
    } else {
      feedError.value = true   // 已有定位但 feed 请求失败 → 给重试入口，别静默空白
    }
    nearby.value = []
  } finally {
    cityStore.locating = false
    feedLoading.value = false
  }
}

onLoad(async () => {
  try {
    const sys = uni.getWindowInfo()
    statusBarH.value = sys.statusBarHeight || 44
    tabBarH.value = ((sys.safeAreaInsets?.bottom || 18) + 56) + 'px'
  } catch (_) {}
  await loadFeed()
})

onShow(() => {
  setTabBarSelected(0)
  readConsultFlag()
  if (!loaded.value && !cityStore.locating && !locationError.value) loadFeed()
})

function buildCtx() {
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
    const ctx = buildCtx()
    setAssistantContext(ctx)
    uni.switchTab({ url: '/pages/assistant/chat', success: () => uni.$emit('assistantContext', ctx) })
  } else if (id === 'nearby_now') {
    uni.navigateTo({ url: '/pages/nearby/index' })
  } else if (id === 'hot_routes') {
    goRoutes()
  }
}

function goNearby() { uni.navigateTo({ url: '/pages/nearby/index' }) }
function goRoutes(duration = '') {
  if (typeof duration !== 'string') duration = ''
  uni.navigateTo({ url: `/pages/routes/routes${duration ? `?duration=${duration}` : ''}` })
}

function retryLocation() { loadFeed({ forceLocate: true }) }
function useDefaultFeed() {
  cityStore.setDefaultLocation()
  loadFeed({ useDefault: true })
}

function goPoi(id) {
  uni.navigateTo({ url: `/pages/poi/detail?id=${id}&lat=${cityStore.coords?.lat || ''}&lng=${cityStore.coords?.lng || ''}` })
}

function onSearch() {
  const ctx = { ...buildCtx(), intent: 'search' }
  setAssistantContext(ctx)
  uni.switchTab({ url: '/pages/assistant/chat', success: () => uni.$emit('assistantContext', ctx) })
}
</script>

<style lang="scss">
@import '../../uni.scss';

.cy-page {
  min-height: 100vh;
  background: $cy-bg;
  font-family: "PingFang SC", "HarmonyOS Sans SC", "Noto Sans SC", -apple-system, system-ui, sans-serif;
  overflow-x: hidden;
}

.cy-scroll { flex: 1; }

// ── Header ─────────────────────────────────────────────────
.cy-home-header {
  background: #fff;
  padding: 20rpx 36rpx 20rpx;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  border-bottom: 1rpx solid $cy-border;
}

.cy-hh-left {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  flex: 1;
  min-width: 0;
}

.cy-hh-title {
  font-size: 48rpx;
  font-weight: 800;
  color: $cy-green;
}

.cy-hh-loc {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.cy-hh-loc-text {
  font-size: 24rpx;
  font-weight: 500;
  color: $cy-text;
}


.cy-hh-search {
  width: 60rpx;
  height: 44rpx;
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.cy-hh-weather {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.cy-weather-icon {
  width: 36rpx;
  height: 36rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cy-weather-text {
  font-size: 24rpx;
  color: $cy-text;
  font-weight: 500;
}

.cy-hh-range {
  font-size: 24rpx;
  color: $cy-muted;
  white-space: nowrap;
}

// ── 大卡块 ─────────────────────────────────────────────────
.cy-entry-section-head {
  padding: 28rpx 28rpx 0;
  margin-bottom: 20rpx;
}

.cy-entry-block {
  margin: 0 28rpx 0;
  background: $cy-green-ls;
  border-radius: 32rpx;
  padding: 28rpx 28rpx 32rpx;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.cy-et-subtitle {
  font-size: 26rpx;
  color: $cy-text-sub;
  line-height: 1.4;
  margin-top: 4rpx;
}

.cy-et-sub {
  font-size: 26rpx;
  color: $cy-text-sub;
  line-height: 1.4;
}

.cy-entry-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18rpx;
  width: 100%;
}

// ── Sections ───────────────────────────────────────────────
.cy-section {
  padding: 28rpx 28rpx 0;
}

.cy-section-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 20rpx;
}

.cy-section-title {
  font-size: 32rpx;
  font-weight: 800;
  color: $cy-text;
}

.cy-section-more {
  font-size: 26rpx;
  color: $cy-muted;
}

// ── 附近地点卡 ─────────────────────────────────────────────
.cy-nearby-card {
  background: #fff;
  border-radius: 32rpx;
  border: 1rpx solid $cy-border;
  padding: 0 28rpx 12rpx;
  overflow: hidden;
}

.cy-nearby-row {
  display: flex;
  align-items: center;
  gap: 24rpx;
  padding: 20rpx 0;
}

.cy-nearby-row--divider {
  border-top: 1rpx solid $cy-border;
}

.cy-nearby-thumb {
  width: 144rpx;
  height: 144rpx;
  border-radius: 20rpx;
  flex-shrink: 0;
  background: $cy-green-ls;
  overflow: hidden;
}

.cy-nearby-body {
  flex: 1;
  min-width: 0;
}

.cy-nearby-name {
  display: block;
  font-size: 30rpx;
  font-weight: 700;
  color: $cy-text;
}

.cy-nearby-tags {
  margin-top: 12rpx;
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.cy-nearby-tag {
  font-size: 24rpx;
  color: $cy-green;
}

.cy-nearby-right {
  text-align: right;
  flex-shrink: 0;
  padding-top: 4rpx;
}

.cy-nearby-dist {
  display: block;
  font-size: 26rpx;
  color: $cy-green;
  font-weight: 600;
}

.cy-nearby-rating {
  margin-top: 16rpx;
  display: flex;
  align-items: center;
  gap: 4rpx;
  justify-content: flex-end;
}

.cy-nearby-rnum { font-size: 26rpx; color: $cy-text; font-weight: 600; }

// ── 路线卡 ─────────────────────────────────────────────────
.cy-routes-card {
  background: #fff;
  border-radius: 32rpx;
  border: 1rpx solid $cy-border;
  padding: 24rpx 28rpx 24rpx;
}

.cy-routes-row {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

// ── Hints ──────────────────────────────────────────────────
.cy-hint-muted {
  padding: 32rpx;
  text-align: center;
  font-size: 26rpx;
  color: $cy-muted;
}

.cy-hint-card {
  background: $cy-green-ls;
  border-radius: 16rpx;
  padding: 24rpx;
  font-size: 24rpx;
  color: $cy-text-sub;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 16rpx;
}

.cy-hint-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16rpx;
  flex-wrap: wrap;
}

.cy-hint-btn {
  height: 60rpx;
  padding: 0 32rpx;
  border-radius: 30rpx;
  background: $cy-green;
  color: #fff;
  font-size: 24rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cy-hint-btn--ghost {
  background: #fff;
  color: $cy-green;
  border: 1rpx solid $cy-green-line;
}
</style>
