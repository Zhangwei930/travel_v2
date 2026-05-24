<template>
  <view class="page">
    <view class="header" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="header-row">
        <view class="back-btn" @tap="goBack">
          <svg xmlns="http://www.w3.org/2000/svg" width="9" height="16" viewBox="0 0 9 16">
            <path d="M7.5 1.5L2 8l5.5 6.5" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
          </svg>
        </view>
        <view class="header-text">
          <text class="header-mono mono">ROUTE · {{ route?.no || 'R-??' }}</text>
          <text class="header-title serif">{{ route?.title || '路线详情' }}</text>
        </view>
      </view>
      <view class="header-meta">
        <text class="meta-item">🕐 {{ route?.duration || '半日' }}</text>
        <text class="meta-item">📍 {{ stopCount }} 站</text>
        <text v-if="route?.budget" class="meta-item">💰 {{ route.budget }}</text>
      </view>
    </view>

    <scroll-view scroll-y class="scroll-body" :style="{ paddingBottom: actionBarHeight }" :show-scrollbar="false">
      <!-- 地图预览 -->
      <view class="map-card">
        <map
          v-if="mappableStops.length"
          class="route-map"
          :latitude="center.lat"
          :longitude="center.lng"
          :markers="markers"
          :polyline="polyline"
          :scale="13"
          show-location
        />
        <view v-else class="map-empty">
          <text class="map-empty-icon">🗺</text>
          <text class="map-empty-text">该路线暂无可定位的站点</text>
        </view>
      </view>

      <!-- 路线摘要 -->
      <view v-if="route?.summary" class="summary-card">
        <text class="summary-text">{{ route.summary }}</text>
      </view>

      <!-- 路线节点 -->
      <view class="section">
        <z-section-header no="S" title="路线节点" :sub="`${stopCount} 站 · 顺路推荐`" />
        <view class="timeline">
          <view
            v-for="(stop, idx) in stops"
            :key="stop.name + idx"
            class="timeline-item"
          >
            <view class="timeline-marker">
              <text class="timeline-no mono">{{ String(idx + 1).padStart(2, '0') }}</text>
              <view v-if="idx < stops.length - 1" class="timeline-line" />
            </view>
            <view class="timeline-card">
              <view class="timeline-head">
                <text class="stop-name serif">{{ stop.name }}</text>
                <text v-if="stop.distance" class="stop-dist">{{ stop.distance }}</text>
              </view>
              <text v-if="stop.reason" class="stop-reason">{{ stop.reason }}</text>
              <view class="stop-actions">
                <text v-if="stop.stay_duration" class="stop-stay mono">停留 {{ stop.stay_duration }}</text>
                <view
                  class="stop-nav"
                  :class="{ disabled: stop.lat == null || stop.lng == null }"
                  @tap.stop="navTo(stop)"
                >到这里</view>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 提示与避坑 -->
      <view v-if="route?.tips || defaultTips.length" class="section">
        <z-section-header no="T" title="提示与避坑" sub="出行前请核实当日营业与天气" />
        <view class="tip-card">
          <text v-if="route?.tips" class="tip-text">{{ route.tips }}</text>
          <view v-else>
            <text v-for="t in defaultTips" :key="t" class="tip-item">· {{ t }}</text>
          </view>
        </view>
      </view>
    </scroll-view>

    <!-- 底部主操作 -->
    <view class="action-bar" :style="{ paddingBottom: safeBottom }">
      <view class="primary-action" :class="{ disabled: !firstNavStop }" @tap="navAll">跟着路线导航</view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const statusBarHeight = ref(44)
const safeBottom = ref('18px')
const actionBarHeight = ref('148rpx')

const route = ref(null)

const stops = computed(() => Array.isArray(route.value?.stops) ? route.value.stops : [])
const stopCount = computed(() => stops.value.length)

const mappableStops = computed(() =>
  stops.value.filter(s => s.lat != null && s.lng != null).map((s, idx) => ({ ...s, _idx: idx }))
)

const markers = computed(() =>
  mappableStops.value.map(s => ({
    id: s._idx,
    latitude: Number(s.lat),
    longitude: Number(s.lng),
    title: s.name,
    iconPath: '',
    width: 28,
    height: 28,
    callout: {
      content: `${s._idx + 1}. ${s.name}`,
      color: '#ffffff',
      bgColor: '#0D4F4A',
      padding: 6,
      borderRadius: 6,
      display: 'ALWAYS',
    },
  }))
)

const polyline = computed(() => {
  if (mappableStops.value.length < 2) return []
  return [{
    points: mappableStops.value.map(s => ({ latitude: Number(s.lat), longitude: Number(s.lng) })),
    color: '#0D4F4ACC',
    width: 4,
    arrowLine: true,
  }]
})

const center = computed(() => {
  if (!mappableStops.value.length) return { lat: 30.67, lng: 104.06 }
  const lats = mappableStops.value.map(s => Number(s.lat))
  const lngs = mappableStops.value.map(s => Number(s.lng))
  return {
    lat: (Math.min(...lats) + Math.max(...lats)) / 2,
    lng: (Math.min(...lngs) + Math.max(...lngs)) / 2,
  }
})

const firstNavStop = computed(() => mappableStops.value[0] || null)

const defaultTips = [
  '出发前确认每站营业/开放时间',
  '相邻两站间步行 / 公交时间已纳入推荐时长',
  '雨天或恶劣天气优先选择室内站点',
]

function loadRoute() {
  try {
    const cached = uni.getStorageSync('currentRoute')
    if (cached && cached.id != null) {
      route.value = cached
    }
  } catch (_) {}
}

function goBack() {
  const stack = getCurrentPages()
  if (stack.length > 1) uni.navigateBack()
  else uni.switchTab({ url: '/pages/index/index' })
}

function navTo(stop) {
  if (stop?.lat == null || stop?.lng == null) {
    uni.showToast({ title: '该站点暂无坐标', icon: 'none' })
    return
  }
  uni.openLocation({
    latitude: Number(stop.lat),
    longitude: Number(stop.lng),
    name: stop.name,
    address: stop.reason || '',
  })
}

function navAll() {
  if (!firstNavStop.value) {
    uni.showToast({ title: '该路线暂无可导航站点', icon: 'none' })
    return
  }
  navTo(firstNavStop.value)
}

onMounted(() => {
  try {
    const sys = uni.getSystemInfoSync()
    statusBarHeight.value = sys.statusBarHeight || 44
    const sb = Math.max(sys.safeAreaInsets?.bottom || 18, 18)
    safeBottom.value = sb + 'px'
    actionBarHeight.value = (sb + 92) + 'px'
  } catch (_) {}
  loadRoute()
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
  background: $z-primary;
  padding: 0 32rpx 24rpx;
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
  background: rgba(255, 255, 255, 0.18);
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
  color: rgba(255, 255, 255, 0.6);
  letter-spacing: 2rpx;
  margin-bottom: 4rpx;
}

.header-title {
  display: block;
  font-size: 38rpx;
  font-weight: 900;
  color: $z-card;
  line-height: 1.2;
}

.header-meta {
  display: flex;
  gap: 18rpx;
  margin-top: 18rpx;
  padding-left: 82rpx;
  flex-wrap: wrap;
}

.meta-item {
  color: rgba(255, 255, 255, 0.85);
  font-size: 22rpx;
}

// ── Map ─────────────────────────────────────────────────────
.scroll-body { position: relative; }

.map-card {
  margin: -28rpx 28rpx 0;
  background: $z-card;
  border-radius: 22rpx;
  overflow: hidden;
  box-shadow: 0 6rpx 24rpx rgba(13, 79, 74, 0.12);
  position: relative;
  z-index: 1;
}

.route-map {
  width: 100%;
  height: 380rpx;
}

.map-empty {
  height: 220rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  color: $z-muted;
}

.map-empty-icon { font-size: 60rpx; }
.map-empty-text { font-size: 23rpx; }

// ── Summary ─────────────────────────────────────────────────
.summary-card {
  margin: 22rpx 28rpx 0;
  background: $z-card;
  border-radius: 18rpx;
  padding: 22rpx 26rpx;
  box-shadow: 0 2rpx 10rpx rgba(13, 79, 74, 0.05);
}

.summary-text {
  display: block;
  font-size: 24rpx;
  color: $z-text2;
  line-height: 1.6;
}

// ── Section ─────────────────────────────────────────────────
.section { padding: 28rpx 28rpx 0; }

// ── Timeline ────────────────────────────────────────────────
.timeline {
  display: flex;
  flex-direction: column;
  gap: 4rpx;
  margin-top: 8rpx;
}

.timeline-item {
  display: flex;
  align-items: stretch;
  gap: 16rpx;
}

.timeline-marker {
  width: 60rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
}

.timeline-no {
  width: 48rpx;
  height: 48rpx;
  border-radius: 24rpx;
  background: $z-primary;
  color: $z-card;
  font-size: 20rpx;
  font-weight: 900;
  letter-spacing: 1rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 18rpx;
  z-index: 1;
}

.timeline-line {
  flex: 1;
  width: 4rpx;
  background: rgba(13, 79, 74, 0.18);
  margin-top: 4rpx;
}

.timeline-card {
  flex: 1;
  min-width: 0;
  margin: 12rpx 0 18rpx;
  background: $z-card;
  border-radius: 16rpx;
  padding: 18rpx 22rpx;
  box-shadow: 0 2rpx 10rpx rgba(13, 79, 74, 0.05);
}

.timeline-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 12rpx;
}

.stop-name {
  flex: 1;
  min-width: 0;
  font-size: 27rpx;
  font-weight: 800;
  color: $z-text;
  line-height: 1.25;
}

.stop-dist {
  font-size: 20rpx;
  color: $z-muted;
  flex-shrink: 0;
}

.stop-reason {
  display: block;
  font-size: 22rpx;
  color: $z-text2;
  line-height: 1.5;
  margin-top: 8rpx;
}

.stop-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 14rpx;
  gap: 14rpx;
}

.stop-stay {
  color: $z-muted;
  font-size: 19rpx;
  letter-spacing: 1rpx;
}

.stop-nav {
  height: 52rpx;
  min-width: 96rpx;
  padding: 0 18rpx;
  border-radius: 10rpx;
  background: rgba(13, 79, 74, 0.08);
  color: $z-primary;
  font-size: 22rpx;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;

  &.disabled {
    background: rgba(0, 0, 0, 0.06);
    color: $z-muted;
  }
}

// ── Tips ────────────────────────────────────────────────────
.tip-card {
  margin-top: 12rpx;
  background: $z-card;
  border-radius: 16rpx;
  padding: 20rpx 22rpx;
  box-shadow: 0 2rpx 10rpx rgba(13, 79, 74, 0.05);
}

.tip-text,
.tip-item {
  display: block;
  font-size: 22rpx;
  color: $z-text2;
  line-height: 1.6;
}

// ── Action bar ──────────────────────────────────────────────
.action-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.98);
  border-top: 1rpx solid $z-border;
  padding: 16rpx 28rpx 0;
  z-index: 9;
}

.primary-action {
  height: 92rpx;
  border-radius: 18rpx;
  background: $z-primary;
  color: $z-card;
  font-size: 30rpx;
  font-weight: 900;
  display: flex;
  align-items: center;
  justify-content: center;

  &.disabled { background: $z-muted; }
}
</style>
