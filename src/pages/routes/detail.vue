<template>
  <view class="cy-page">
    <cy-nav-bar :title="route?.title || '路线详情'" />

    <!-- 标签行 -->
    <scroll-view scroll-x class="cy-tags-scroll" :show-scrollbar="false" v-if="routeTags.length">
      <view class="cy-tags-row">
        <view class="cy-rtag" v-for="tag in routeTags" :key="tag">{{ tag }}</view>
      </view>
    </scroll-view>

    <scroll-view scroll-y class="cy-scroll" :style="{ paddingBottom: safeBottomPx }" :show-scrollbar="false">
      <!-- 描述 -->
      <view class="cy-summary" v-if="route?.summary">
        <text>{{ route.summary }}</text>
      </view>

      <!-- meta 行 -->
      <view class="cy-meta-row">
        <view class="cy-meta-chip">
          <CyIcon name="clock-green" :size="28" />
          <text class="cy-meta-text">约{{ route?.duration || '半日' }}</text>
        </view>
        <view class="cy-meta-chip">
          <CyIcon name="pin-outline-green" :size="28" />
          <text class="cy-meta-text">{{ stopCount }}个地点</text>
        </view>
        <view class="cy-meta-chip" v-if="totalDistText">
          <CyIcon name="nav-green" :size="28" />
          <text class="cy-meta-text">约{{ totalDistText }}</text>
        </view>
      </view>

      <!-- 地图 -->
      <view class="cy-map-card">
        <map
          v-if="mappableStops.length"
          class="cy-map"
          :latitude="center.lat"
          :longitude="center.lng"
          :markers="markers"
          :polyline="polyline"
          :scale="13"
          show-location
        />
        <view v-else class="cy-map-empty">
          <CyIcon name="map-muted" :size="84" />
          <text class="cy-map-empty-text">该路线暂无可定位的站点</text>
        </view>
      </view>

      <!-- 路线地点 -->
      <view class="cy-section">
        <text class="cy-section-title">路线地点</text>

        <view class="cy-timeline">
          <view v-for="(stop, idx) in stops" :key="stop.name + idx" class="cy-timeline-item">
            <view class="cy-tl-marker">
              <view class="cy-tl-num">{{ idx + 1 }}</view>
              <view v-if="idx < stops.length - 1" class="cy-tl-line" />
            </view>
            <view class="cy-tl-content" @tap="goPoi(stop)">
              <view class="cy-tl-head">
                <text class="cy-tl-name">{{ stop.name }}</text>
                <text v-if="stop.distance" class="cy-tl-dist">{{ stop.distance }}</text>
              </view>
              <text v-if="stop.reason" class="cy-tl-reason">{{ stop.reason }}</text>
            </view>
          </view>
        </view>
      </view>
    </scroll-view>

    <!-- 底部 CTA -->
    <view class="cy-action-bar" :style="{ paddingBottom: safeBottomBarPx }">
      <button class="cy-act-icon cy-share-btn" open-type="share">
        <CyIcon name="share-dark" :size="50" />
        <text class="cy-act-icon-label">发给朋友</text>
      </button>
      <button class="cy-act-icon cy-share-btn" open-type="shareTimeline">
        <CyIcon name="share-dark" :size="50" />
        <text class="cy-act-icon-label">朋友圈</text>
      </button>
      <view class="cy-nav-btn" :class="{ disabled: !mappableStops.length }" @tap="chooseNavStop">
        <text>跟着路线导航</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { onShareAppMessage, onShareTimeline } from '@dcloudio/uni-app'
import CyNavBar from '../../components/cy/cy-nav-bar.vue'
import CyIcon from '../../components/cy/cy-icon.vue'

const safeBottomPx = ref('140rpx')
const safeBottomBarPx = ref('24rpx')
const route = ref(null)

const stops = computed(() => Array.isArray(route.value?.stops) ? route.value.stops : [])
const stopCount = computed(() => stops.value.length)

const routeTags = computed(() => {
  const tags = route.value?.tags || []
  if (tags.length) return tags
  const t = []
  if (route.value?.duration?.includes('2小时')) t.push('轻松')
  if (route.value?.summary?.includes('亲子') || route.value?.title?.includes('亲子')) t.push('亲子')
  return t
})

const totalDistText = computed(() => {
  let total = 0
  stops.value.forEach(s => {
    const m = String(s.distance || '').match(/([0-9.]+)\s*(km|m|公里|米)?/i)
    if (m) {
      const n = parseFloat(m[1])
      total += /^m|米$/i.test(m[2] || '') ? n / 1000 : n
    }
  })
  return total > 0 ? total.toFixed(1) + 'km' : (route.value?.distance || '')
})

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
    width: 28, height: 28,
    callout: {
      content: `${s._idx + 1}. ${s.name}`,
      color: '#ffffff',
      bgColor: '#1A8870',
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
    color: '#1A8870CC',
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

function goPoi(stop) {
  if (!stop?.id) return
  uni.navigateTo({ url: `/pages/poi/detail?id=${stop.id}` })
}

function navTo(stop) {
  if (stop?.lat == null || stop?.lng == null) {
    uni.showToast({ title: '该站点暂无坐标', icon: 'none' })
    return
  }
  uni.openLocation({ latitude: Number(stop.lat), longitude: Number(stop.lng), name: stop.name, address: stop.reason || '' })
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

function onShare() {
  uni.showShareMenu({ withShareTicket: false, menus: ['shareAppMessage', 'shareTimeline'] })
}

onShareAppMessage(() => {
  const r = route.value
  const cover = r?.stops?.find(s => s.img)?.img || r?.img || ''
  return {
    title: r ? `${r.title}｜${r.duration || '半日'}路线推荐` : '发现一条好路线',
    path: r?.id ? `/pages/routes/detail?id=${r.id}` : '/pages/index/index',
    imageUrl: cover,
  }
})

onShareTimeline(() => {
  const r = route.value
  const cover = r?.stops?.find(s => s.img)?.img || r?.img || ''
  return {
    title: r ? `${r.title}，${r.duration || '半日'}·${stopCount.value}个地点` : '今天的出游路线',
    query: r?.id ? `id=${r.id}` : '',
    imageUrl: cover,
  }
})

onMounted(() => {
  try {
    const sys = uni.getWindowInfo()
    const sb = Math.max(sys.safeAreaInsets?.bottom || 18, 18)
    safeBottomBarPx.value = sb + 'px'
    safeBottomPx.value = (sb + 120) + 'rpx'
  } catch (_) {}
  try {
    const cached = uni.getStorageSync('currentRoute')
    if (cached && cached.id != null) route.value = cached
  } catch (_) {}
})
</script>

<style lang="scss">
@import '../../uni.scss';

.cy-page {
  min-height: 100vh;
  background: $cy-bg;
  font-family: "PingFang SC", "HarmonyOS Sans SC", "Noto Sans SC", -apple-system, system-ui, sans-serif;
}

// ── 标签行 ─────────────────────────────────────────────────
.cy-tags-scroll { background: #fff; }

.cy-tags-row {
  display: flex;
  gap: 12rpx;
  padding: 16rpx 28rpx;
  white-space: nowrap;
}

.cy-rtag {
  padding: 8rpx 24rpx;
  background: $cy-green-l;
  border-radius: 9999rpx;
  font-size: 24rpx;
  color: $cy-green-d;
  font-weight: 600;
}

// ── 描述 + meta ─────────────────────────────────────────────
.cy-summary {
  padding: 24rpx 28rpx 0;
  font-size: 26rpx;
  color: $cy-text-sub;
  line-height: 1.6;
}

.cy-meta-row {
  display: flex;
  gap: 16rpx;
  padding: 20rpx 28rpx;
  flex-wrap: wrap;
}

.cy-meta-chip {
  display: flex;
  align-items: center;
  gap: 6rpx;
  background: $cy-green-ls;
  border-radius: 12rpx;
  padding: 8rpx 18rpx;
}

.cy-meta-text { font-size: 24rpx; color: $cy-text-sub; }

// ── 地图 ───────────────────────────────────────────────────
.cy-map-card {
  margin: 0 28rpx 24rpx;
  height: 400rpx;
  background: $cy-green-ls;
  border-radius: 24rpx;
  overflow: hidden;
  border: 1rpx solid $cy-green-line;
}

.cy-map { width: 100%; height: 100%; }

.cy-map-empty {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  color: $cy-muted;
}

.cy-map-empty-text { font-size: 24rpx; }

// ── 时间轴 ─────────────────────────────────────────────────
.cy-section {
  padding: 24rpx 28rpx 0;
}

.cy-section-title {
  display: block;
  font-size: 30rpx;
  font-weight: 800;
  color: $cy-text;
  margin-bottom: 24rpx;
}

.cy-timeline { display: flex; flex-direction: column; }

.cy-timeline-item {
  display: flex;
  gap: 20rpx;
  margin-bottom: 16rpx;
}

.cy-tl-marker {
  width: 56rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
}

.cy-tl-num {
  width: 56rpx;
  height: 56rpx;
  border-radius: 28rpx;
  background: $cy-green-d;
  color: #fff;
  font-size: 24rpx;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  z-index: 1;
}

.cy-tl-line {
  flex: 1;
  width: 2rpx;
  background: $cy-green-line;
  margin-top: 4rpx;
}

.cy-tl-content {
  flex: 1;
  min-width: 0;
  background: #fff;
  border-radius: 20rpx;
  padding: 20rpx 24rpx;
  border: 1rpx solid $cy-border;
}

.cy-tl-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 12rpx;
  margin-bottom: 8rpx;
}

.cy-tl-name {
  font-size: 30rpx;
  font-weight: 700;
  color: $cy-text;
}

.cy-tl-dist {
  font-size: 24rpx;
  color: $cy-green;
  font-weight: 600;
  flex-shrink: 0;
}

.cy-tl-reason {
  display: block;
  font-size: 24rpx;
  color: $cy-text-sub;
  line-height: 1.55;
}

// ── 底部 CTA ───────────────────────────────────────────────
.cy-action-bar {
  position: fixed;
  left: 0; right: 0; bottom: 0;
  background: rgba(255,255,255,0.96);
  backdrop-filter: blur(10px);
  padding: 20rpx 28rpx;
  z-index: 99;
  border-top: 1rpx solid $cy-border;
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.cy-act-icon {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4rpx;
  flex-shrink: 0;
  width: 80rpx;
}

.cy-act-icon-label { font-size: 20rpx; color: $cy-text-sub; }

.cy-share-btn {
  background: transparent;
  border: none;
  padding: 0;
  margin: 0;
  line-height: 1;
  &::after { border: none; }
}

.cy-nav-btn {
  height: 100rpx;
  background: $cy-green-d;
  color: #fff;
  border-radius: 50rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 34rpx;
  font-weight: 800;
  letter-spacing: 2rpx;
  box-shadow: 0 8rpx 20rpx rgba(15,94,77,0.25);

  &.disabled {
    background: $cy-muted;
    box-shadow: none;
  }
}
</style>
