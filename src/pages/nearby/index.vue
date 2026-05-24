<template>
  <view class="page">
    <view class="header" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="header-row">
        <view class="back-btn" @tap="goBack">
          <svg xmlns="http://www.w3.org/2000/svg" width="9" height="16" viewBox="0 0 9 16">
            <path d="M7.5 1.5L2 8l5.5 6.5" stroke="#1A2E2C" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
          </svg>
        </view>
        <view class="header-text">
          <text class="header-mono mono">§ NEARBY · NOW</text>
          <text class="header-title serif">附近现在适合去</text>
        </view>
      </view>
      <text class="header-sub">{{ subText }}</text>

      <scroll-view scroll-x class="filter-scroll" :show-scrollbar="false">
        <view class="filter-row">
          <view
            v-for="f in filters"
            :key="f.id"
            class="filter-chip"
            :class="{ active: active === f.id }"
            @tap="setFilter(f.id)"
          >
            <text class="filter-label">{{ f.label }}</text>
          </view>
        </view>
      </scroll-view>
    </view>

    <scroll-view
      scroll-y
      class="scroll-body"
      :style="{ paddingBottom: safeBottom }"
      :show-scrollbar="false"
      @scrolltolower="onReachBottom"
    >
      <view v-if="loading && !pois.length" class="state-card mono">
        正在加载附近推荐…
      </view>
      <view v-else-if="locationError" class="state-card">
        <text class="state-title serif">需要定位后才能展示附近</text>
        <text class="state-sub mono">允许位置权限后系统才会推荐真实可去的地点</text>
        <view class="state-btn" @tap="reload">重新定位</view>
      </view>
      <view v-else-if="!visiblePois.length" class="state-card mono">
        没有匹配该筛选的地点，换一个筛选项试试
      </view>

      <view class="poi-list">
        <view
          v-for="poi in visiblePois"
          :key="poi.id"
          class="poi-card"
          @tap="goPoi(poi.id)"
        >
          <view class="poi-score">
            <text class="score-num">{{ poi.score ?? '—' }}</text>
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
            <text class="poi-reason">{{ poi.reason }}</text>
            <view class="poi-tags">
              <z-tag
                v-for="tag in (poi.tags || []).slice(0, 4)"
                :key="tag"
                :label="tag"
                color="#0D4F4A"
                :small="true"
              />
              <text v-if="poi.kb_status" class="kb-badge mono">{{ poi.kb_status }}</text>
            </view>
            <view class="poi-actions">
              <text class="source-note">{{ poi.source === 'kb' ? '知识库推荐' : '地图数据推荐' }}</text>
              <view class="nav-btn" :class="{ disabled: !poi.nav_ready }" @tap.stop="openNav(poi)">导航</view>
            </view>
          </view>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '../../api/mock.js'
import { useCityStore } from '../../store/city.js'
import ZTag from '../../components/ZTag.vue'

const cityStore = useCityStore()
const statusBarHeight = ref(44)
const safeBottom = ref('80rpx')

const filters = [
  { id: 'all',       label: '全部' },
  { id: 'recommend', label: '推荐' },
  { id: 'nearest',   label: '最近' },
  { id: 'free',      label: '免费' },
  { id: 'indoor',    label: '室内' },
]

const active = ref('all')
const pois = ref([])
const loading = ref(false)
const locationError = ref(false)
const weather = ref(null)

const subText = computed(() => {
  if (locationError.value) return '尚未获取到定位'
  const loc = cityStore.current || '当前位置'
  const w = weather.value ? `${weather.value.icon || ''}${weather.value.temp}°${weather.value.cond}` : ''
  return `${loc}${w ? ' · ' + w : ''}`
})

function parseDistanceKm(text) {
  if (!text) return Number.POSITIVE_INFINITY
  const s = String(text).trim().toLowerCase()
  const m = s.match(/([0-9.]+)\s*(km|m|公里|米)?/)
  if (!m) return Number.POSITIVE_INFINITY
  const n = parseFloat(m[1])
  const unit = m[2] || ''
  if (unit === 'm' || unit === '米') return n / 1000
  return n
}

function tagsContain(poi, kw) {
  return (poi.tags || []).some(t => String(t).includes(kw))
}

function categoryIndoor(poi) {
  const c = (poi.category || '') + ''
  return ['博物馆', '商场', '书店', '展馆', '室内', '美术馆', '科技馆', '咖啡', '影院'].some(k => c.includes(k))
}

const visiblePois = computed(() => {
  let arr = [...pois.value]
  if (active.value === 'nearest') {
    arr.sort((a, b) => parseDistanceKm(a.distance) - parseDistanceKm(b.distance))
  } else if (active.value === 'free') {
    arr = arr.filter(p => tagsContain(p, '免费') || tagsContain(p, '免门票'))
  } else if (active.value === 'indoor') {
    arr = arr.filter(p => tagsContain(p, '室内') || categoryIndoor(p))
  } else if (active.value === 'recommend') {
    arr = arr.filter(p => (p.score ?? 0) >= 60)
  }
  // 'all' 不动
  return arr
})

function setFilter(id) {
  if (active.value === id) return
  active.value = id
}

async function reload() {
  loading.value = true
  locationError.value = false
  try {
    let coords = cityStore.coords
    if (!coords?.lat) {
      coords = await new Promise((resolve, reject) => {
        uni.getLocation({ type: 'gcj02', success: resolve, fail: reject })
      }).then(r => {
        cityStore.setCoords(r.latitude, r.longitude)
        return cityStore.coords
      })
    }

    const feed = await api.getHomeFeed({
      lat: coords.lat,
      lng: coords.lng,
      city: cityStore.current,
      intent: 'nearby_now',
    })
    if (feed?.location?.city) cityStore.setFromLocation(feed.location.city)
    weather.value = feed.weather || null
    pois.value = (feed.nearby_now || []).filter(p => p.nav_ready && p.lat != null && p.lng != null)
  } catch (_) {
    locationError.value = true
    pois.value = []
  } finally {
    loading.value = false
  }
}

function onReachBottom() {
  // 当前 home feed 不分页，留给后端分页接口接入
}

function goBack() {
  const stack = getCurrentPages()
  if (stack.length > 1) uni.navigateBack()
  else uni.switchTab({ url: '/pages/index/index' })
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

onMounted(() => {
  try {
    const sys = uni.getSystemInfoSync()
    statusBarHeight.value = sys.statusBarHeight || 44
    safeBottom.value = Math.max(sys.safeAreaInsets?.bottom || 18, 18) + 'px'
  } catch (_) {}
  reload()
})
</script>

<style lang="scss">
@import '../../uni.scss';

.page {
  min-height: 100vh;
  background: $z-bg;
}

// ── Header ──────────────────────────────────────────────────
.header {
  background: $z-card;
  padding: 0 32rpx 16rpx;
}

.header-row {
  display: flex;
  align-items: center;
  gap: 18rpx;
  padding-top: 16rpx;
}

.back-btn {
  width: 64rpx;
  height: 64rpx;
  border-radius: 32rpx;
  background: rgba(13, 79, 74, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.header-text {
  flex: 1;
  min-width: 0;
}

.header-mono {
  display: block;
  font-size: 20rpx;
  color: $z-muted;
  letter-spacing: 3rpx;
  margin-bottom: 4rpx;
}

.header-title {
  display: block;
  font-size: 38rpx;
  font-weight: 900;
  color: $z-text;
}

.header-sub {
  display: block;
  font-size: 22rpx;
  color: $z-muted;
  padding: 14rpx 0 0;
}

// ── Filter chips ────────────────────────────────────────────
.filter-scroll {
  width: 100%;
  margin: 18rpx -32rpx 0;
  padding-left: 32rpx;
}

.filter-row {
  display: flex;
  gap: 10rpx;
  padding-right: 32rpx;
  white-space: nowrap;
  padding-bottom: 4rpx;
}

.filter-chip {
  display: inline-flex;
  align-items: center;
  padding: 10rpx 22rpx;
  border-radius: $radius-pill;
  background: $z-bg;
  border: 1rpx solid $z-border;
  flex-shrink: 0;

  &.active {
    background: $z-primary;
    border-color: $z-primary;

    .filter-label { color: $z-card; }
  }
}

.filter-label {
  font-size: 22rpx;
  font-weight: 700;
  color: $z-text2;
}

// ── List ────────────────────────────────────────────────────
.scroll-body {
  position: relative;
}

.poi-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  padding: 22rpx 28rpx 32rpx;
}

.poi-card {
  background: $z-card;
  border-radius: 18rpx;
  padding: 20rpx;
  box-shadow: 0 2rpx 10rpx rgba(13, 79, 74, 0.05);
  display: flex;
  gap: 18rpx;
  cursor: pointer;
}

.poi-score {
  width: 84rpx;
  height: 84rpx;
  border-radius: 16rpx;
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

.poi-title-wrap {
  flex: 1;
  min-width: 0;
}

.poi-name {
  display: block;
  font-size: 28rpx;
  font-weight: 800;
  color: $z-text;
  line-height: 1.2;
}

.poi-cat {
  display: block;
  font-size: 21rpx;
  color: $z-muted;
  margin-top: 4rpx;
}

.poi-time {
  font-size: 20rpx;
  color: $z-muted;
  white-space: nowrap;
  margin-top: 4rpx;
}

.poi-reason {
  display: block;
  font-size: 22rpx;
  color: $z-text2;
  line-height: 1.5;
  margin: 8rpx 0 12rpx;
}

.poi-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8rpx;
  align-items: center;
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
  margin-top: 14rpx;
}

.source-note {
  flex: 1;
  min-width: 0;
  font-size: 20rpx;
  color: $z-muted;
}

.nav-btn {
  min-width: 108rpx;
  height: 58rpx;
  border-radius: 10rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24rpx;
  font-weight: 800;
  color: $z-card;
  background: $z-primary;

  &.disabled { background: $z-muted; }
}

// ── State cards ─────────────────────────────────────────────
.state-card {
  margin: 32rpx 28rpx;
  background: $z-card;
  border-radius: 18rpx;
  padding: 32rpx 28rpx;
  text-align: center;
  color: $z-muted;
}

.state-title {
  display: block;
  font-size: 30rpx;
  font-weight: 900;
  color: $z-text;
  margin-bottom: 8rpx;
}

.state-sub {
  display: block;
  font-size: 22rpx;
  margin-bottom: 18rpx;
}

.state-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0 28rpx;
  height: 64rpx;
  border-radius: 12rpx;
  background: $z-primary;
  color: $z-card;
  font-size: 24rpx;
  font-weight: 800;
}
</style>
