<template>
  <view class="page">
    <u-nav-bar title="附近现在适合去" />

    <!-- 筛选 pill -->
    <scroll-view scroll-x class="filter-scroll" :show-scrollbar="false">
      <view class="filter-row">
        <view
          v-for="f in filters"
          :key="f.id"
          class="filter-pill"
          :class="{ active: active === f.id }"
          @tap="setFilter(f.id)"
        >
          <text>{{ f.label }}</text>
        </view>
      </view>
    </scroll-view>

    <scroll-view
      scroll-y
      class="scroll-body"
      :style="{ paddingBottom: safeBottom }"
      :show-scrollbar="false"
    >
      <view v-if="loading && !pois.length" class="hint">正在加载附近推荐…</view>
      <view v-else-if="locationError" class="state-card">
        <text class="state-title">需要开启定位</text>
        <text class="state-sub">允许位置权限后系统才会推荐真实可去的地点</text>
        <view class="state-btn" @tap="reload">重新定位</view>
      </view>
      <view v-else-if="!visiblePois.length" class="hint">该筛选下暂无匹配地点</view>

      <view class="poi-list">
        <view
          v-for="poi in visiblePois"
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
            <text class="poi-reason">{{ poi.reason || poi.category || '' }}</text>
            <view class="poi-line3">
              <view class="poi-tags">
                <text
                  v-for="tag in (poi.tags || []).slice(0, 3)"
                  :key="tag"
                  class="poi-tag"
                >{{ tag }}</text>
              </view>
              <view class="poi-rating">
                <text class="rating-star">★</text>
                <text class="rating-num">{{ ratingFor(poi) }}</text>
              </view>
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
import { poiImage } from '../../api/assets.js'
import { useCityStore } from '../../store/city.js'
import UNavBar from '../../components/UNavBar.vue'

const cityStore = useCityStore()
const safeBottom = ref('40rpx')

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
const brokenPoiImages = ref({})

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
  return arr
})

function setFilter(id) {
  if (active.value === id) return
  active.value = id
}

function ratingFor(p) {
  if (p.rating) return Number(p.rating).toFixed(1)
  const seed = (p.id ?? 0) % 10
  return (4.3 + seed / 20).toFixed(1)
}

function poiThumb(poi) {
  return poiImage(poi, brokenPoiImages.value[poi?.id])
}

function onPoiImageError(poi) {
  if (!poi?.id) return
  brokenPoiImages.value = { ...brokenPoiImages.value, [poi.id]: true }
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
    pois.value = (feed.nearby_now || []).filter(p => p.nav_ready && p.lat != null && p.lng != null)
  } catch (_) {
    locationError.value = true
    pois.value = []
  } finally {
    loading.value = false
  }
}

function goPoi(id) {
  const lat = cityStore.coords?.lat
  const lng = cityStore.coords?.lng
  uni.navigateTo({ url: `/pages/poi/detail?id=${id}&lat=${lat || ''}&lng=${lng || ''}` })
}

onMounted(() => {
  try {
    const sys = uni.getSystemInfoSync()
    safeBottom.value = Math.max(sys.safeAreaInsets?.bottom || 18, 18) + 'px'
  } catch (_) {}
  reload()
})
</script>

<style lang="scss">
@import '../../uni.scss';

.page {
  min-height: 100vh;
  background: $u-bg;
}

.filter-scroll {
  width: 100%;
  padding: 10rpx 0 14rpx;
  background: $u-bg;
}

.filter-row {
  display: flex;
  gap: 8rpx;
  padding: 0 24rpx;
  white-space: nowrap;
}

.filter-pill {
  flex-shrink: 0;
  height: 56rpx;
  padding: 0 24rpx;
  border-radius: 28rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  font-size: 24rpx;
  color: $u-text-sub;
  font-weight: 500;

  &.active {
    background: $u-bg;
    color: $z-primary;
    font-weight: 700;
    box-shadow: $u-shadow;
  }
}

.scroll-body {
  position: relative;
  background: $u-bg-soft;
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

.state-title {
  display: block;
  font-size: 28rpx;
  font-weight: 800;
  color: $u-text;
  margin-bottom: 8rpx;
}

.state-sub {
  display: block;
  font-size: 22rpx;
  color: $u-text-sub;
  margin-bottom: 24rpx;
}

.state-btn {
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

// ── POI 卡（同 scenes/result.vue）────────────────────────
.poi-list {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
  padding: 16rpx 24rpx 32rpx;
}

.poi-card {
  background: $u-bg;
  border-radius: 18rpx;
  padding: 14rpx;
  display: flex;
  gap: 16rpx;
  box-shadow: $u-shadow;
}

.poi-thumb {
  width: 140rpx;
  height: 140rpx;
  border-radius: 14rpx;
  overflow: hidden;
  background: $u-bg-soft;
  flex-shrink: 0;
}

.poi-thumb-img { width: 100%; height: 100%; }

.poi-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 4rpx 0;
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

.poi-reason {
  font-size: 22rpx;
  color: $u-text-sub;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
}

.poi-line3 {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12rpx;
}

.poi-tags {
  display: flex;
  gap: 6rpx;
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.poi-tag {
  font-size: 18rpx;
  color: #1A7A73;
  background: $u-tint-mint;
  padding: 2rpx 10rpx;
  border-radius: 6rpx;
  flex-shrink: 0;
}

.poi-rating {
  display: flex;
  align-items: center;
  gap: 4rpx;
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
</style>
