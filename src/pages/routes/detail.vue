<template>
  <view class="page">
    <u-nav-bar :title="route?.title || '路线详情'" />

    <scroll-view scroll-y class="scroll-body" :style="{ paddingBottom: safeBottom }" :show-scrollbar="false">
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

      <!-- 路线信息卡 -->
      <view class="info-card">
        <view class="info-row">
          <view class="info-item">
            <text class="info-label">预估耗时</text>
            <text class="info-val">{{ route?.duration || '半日' }}</text>
          </view>
          <view class="info-divider" />
          <view class="info-item">
            <text class="info-label">游玩站点</text>
            <text class="info-val">{{ stopCount }} 站</text>
          </view>
          <view v-if="route?.budget" class="info-divider" />
          <view v-if="route?.budget" class="info-item">
            <text class="info-label">预估开支</text>
            <text class="info-val">{{ route.budget }}</text>
          </view>
        </view>
        <view v-if="route?.summary" class="info-summary">
          <text>{{ route.summary }}</text>
        </view>
      </view>

      <!-- 路线节点 -->
      <view class="section">
        <view class="section-head">
          <text class="section-title">路线节点</text>
          <text class="section-sub">{{ stopCount }} 站 · 顺序推荐</text>
        </view>

        <view class="timeline">
          <view
            v-for="(stop, idx) in stops"
            :key="stop.name + idx"
            class="timeline-item"
          >
            <view class="timeline-marker">
              <view class="marker-dot" />
              <view v-if="idx < stops.length - 1" class="marker-line" />
            </view>
            <view class="timeline-content" @tap="goPoi(stop)">
              <view class="stop-head">
                <text class="stop-name">{{ stop.name }}</text>
                <text v-if="stop.distance" class="stop-dist">{{ stop.distance }}</text>
              </view>
              <text v-if="stop.reason" class="stop-reason">{{ stop.reason }}</text>
              <view class="stop-foot">
                <text v-if="stop.stay_duration" class="stop-stay">建议停留 {{ stop.stay_duration }}</text>
                <view
                  class="nav-tag"
                  :class="{ disabled: stop.lat == null || stop.lng == null }"
                  @tap.stop="navTo(stop)"
                >
                  <text>导航</text>
                </view>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 提示 -->
      <view class="section tips-section">
        <view class="section-head">
          <text class="section-title">出行提示</text>
        </view>
        <view class="tips-card">
          <text v-if="route?.tips">{{ route.tips }}</text>
          <template v-else>
            <text v-for="(t, i) in defaultTips" :key="i" class="tip-line">· {{ t }}</text>
          </template>
        </view>
      </view>
    </scroll-view>

    <!-- 底部导航 -->
    <view class="action-bar" :style="{ paddingBottom: safeBottomPadding }">
      <view class="nav-all-btn" :class="{ disabled: !mappableStops.length }" @tap="chooseNavStop">
        <text>选择站点导航</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import UNavBar from '../../components/UNavBar.vue'

const safeBottom = ref('120rpx')
const safeBottomPadding = ref('24rpx')

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
      bgColor: '#1A7A73',
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
    color: '#1A7A73CC',
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

const defaultTips = [
  '出发前请核实各站点当日营业时间',
  '相邻站间距离已按最优路线计算',
  '如遇天气变化，建议调整户外行程',
]

function loadRoute() {
  try {
    const cached = uni.getStorageSync('currentRoute')
    if (cached && cached.id != null) {
      route.value = cached
    }
  } catch (_) {}
}

function goPoi(stop) {
  if (!stop?.id) return
  uni.navigateTo({ url: `/pages/poi/detail?id=${stop.id}` })
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

function chooseNavStop() {
  if (!mappableStops.value.length) {
    uni.showToast({ title: '该路线暂无可导航站点', icon: 'none' })
    return
  }
  uni.showActionSheet({
    itemList: mappableStops.value.map(stop => `${stop._idx + 1}. ${stop.name}`),
    success: (res) => {
      const stop = mappableStops.value[res.tapIndex]
      if (stop) navTo(stop)
    },
  })
}

onMounted(() => {
  try {
    const sys = uni.getSystemInfoSync()
    const sb = Math.max(sys.safeAreaInsets?.bottom || 18, 18)
    safeBottomPadding.value = sb + 'px'
    safeBottom.value = (sb + 120) + 'rpx'
  } catch (_) {}
  loadRoute()
})
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

// ── 地图 ────────────────────────────────────────────────────
.map-card {
  height: 400rpx;
  background: $u-bg-soft;
}

.route-map {
  width: 100%;
  height: 100%;
}

.map-empty {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  color: $u-text-mute;
}

.map-empty-icon { font-size: 60rpx; }
.map-empty-text { font-size: 24rpx; }

// ── 信息卡 ──────────────────────────────────────────────────
.info-card {
  margin: -24rpx 32rpx 0;
  background: $u-bg;
  border-radius: 24rpx;
  padding: 32rpx;
  box-shadow: $u-shadow-lg;
  position: relative;
  z-index: 2;
}

.info-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.info-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4rpx;
}

.info-label {
  font-size: 20rpx;
  color: $u-text-mute;
}

.info-val {
  font-size: 30rpx;
  font-weight: 800;
  color: $u-text;
}

.info-divider {
  width: 1rpx;
  height: 40rpx;
  background: $u-line;
}

.info-summary {
  margin-top: 24rpx;
  padding-top: 24rpx;
  border-top: 1rpx solid $u-line;
  font-size: 24rpx;
  color: $u-text-sub;
  line-height: 1.6;
}

// ── 章节标题 ────────────────────────────────────────────────
.section {
  padding: 32rpx 32rpx 0;
}

.section-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 24rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: 800;
  color: $u-text;
}

.section-sub {
  font-size: 22rpx;
  color: $u-text-mute;
}

// ── 时间轴 ──────────────────────────────────────────────────
.timeline {
  display: flex;
  flex-direction: column;
}

.timeline-item {
  display: flex;
  gap: 24rpx;
}

.timeline-marker {
  width: 24rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
}

.marker-dot {
  width: 16rpx;
  height: 16rpx;
  border-radius: 8rpx;
  background: $z-primary;
  margin-top: 12rpx;
  position: relative;
  z-index: 1;
}

.marker-line {
  flex: 1;
  width: 2rpx;
  background: $u-line;
  margin-top: 4rpx;
}

.timeline-content {
  flex: 1;
  min-width: 0;
  padding-bottom: 40rpx;
}

.stop-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 12rpx;
  margin-bottom: 8rpx;
}

.stop-name {
  font-size: 28rpx;
  font-weight: 700;
  color: $u-text;
}

.stop-dist {
  font-size: 22rpx;
  color: $u-text-mute;
  flex-shrink: 0;
}

.stop-reason {
  display: block;
  font-size: 24rpx;
  color: $u-text-sub;
  line-height: 1.55;
  margin-bottom: 12rpx;
}

.stop-foot {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stop-stay {
  font-size: 20rpx;
  color: $u-text-mute;
}

.nav-tag {
  height: 48rpx;
  padding: 0 20rpx;
  border-radius: 24rpx;
  background: $u-tint-mint;
  color: $z-primary;
  font-size: 22rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;

  &.disabled {
    background: $u-bg-soft;
    color: $u-text-mute;
  }
}

// ── 提示卡 ──────────────────────────────────────────────────
.tips-section {
  padding-bottom: 40rpx;
}

.tips-card {
  background: $u-bg-soft;
  border-radius: 18rpx;
  padding: 24rpx;
  font-size: 24rpx;
  color: $u-text-sub;
  line-height: 1.6;
}

.tip-line { display: block; }

// ── 底部栏 ──────────────────────────────────────────────────
.action-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.96);
  backdrop-filter: blur(10px);
  padding: 20rpx 32rpx;
  z-index: 99;
  border-top: 1rpx solid $u-line;
}

.nav-all-btn {
  height: 96rpx;
  background: $z-primary;
  color: #fff;
  border-radius: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30rpx;
  font-weight: 800;
  box-shadow: 0 8rpx 20rpx rgba(13, 79, 74, 0.2);

  &.disabled {
    background: $u-text-mute;
    box-shadow: none;
  }
}
</style>
