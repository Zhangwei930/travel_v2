<template>
  <view class="cy-page">
    <cy-nav-bar title="附近现在适合去" :right-icon="consultOn ? 'search' : ''" @right="onSearch" />

    <scroll-view scroll-x class="cy-filter-scroll" :show-scrollbar="false">
      <view class="cy-filter-row">
        <view
          v-for="f in filters"
          :key="f.id"
          class="cy-filter-chip"
          :class="{ 'cy-filter-chip--active': isFilterActive(f.id) }"
          @tap="setFilter(f.id)"
        >
          <text>{{ f.label }}</text>
        </view>
      </view>
    </scroll-view>

    <!-- 距离范围（全局，与场景页共用同一设置） -->
    <view class="cy-radius-row">
      <text class="cy-radius-label">范围</text>
      <view
        v-for="km in RADIUS_OPTIONS"
        :key="km"
        class="cy-radius-chip"
        :class="{ 'cy-radius-chip--active': cityStore.radiusKm === km }"
        @tap="setRadius(km)"
      >
        <text>{{ km }}km</text>
      </view>
    </view>

    <scroll-view scroll-y class="cy-scroll" :style="{ height: scrollH ? scrollH + 'px' : '70vh', paddingBottom: safeBottom }" :show-scrollbar="false" @scrolltolower="loadMore">
      <view v-if="loading && !pois.length" class="cy-hint-muted"><text>正在加载附近推荐…</text></view>
      <view v-else-if="locationError" class="cy-state-card">
        <text class="cy-state-title">需要开启定位</text>
        <text class="cy-state-sub">允许位置权限后系统才会推荐真实可去的地点</text>
        <view class="cy-state-btn" @tap="reload">重新定位</view>
      </view>
      <view v-else-if="!filteredPois.length && !loading" class="cy-hint-muted"><text>该筛选下暂无匹配地点</text></view>

      <view class="cy-poi-list">
        <cy-place-card
          v-for="poi in visiblePois"
          :key="poi.id"
          :name="poi.name"
          :distance="poi.distance"
          :desc="poi.reason || poi.category || ''"
          :image="poiThumb(poi)"
          :rating="ratingFor(poi)"
          :tags="poi.tags || []"
          @tap="goPoi(poi.id)"
          @img-error="onPoiImageError(poi)"
        />
      </view>

      <view v-if="filteredPois.length && visiblePois.length >= filteredPois.length" class="cy-list-end">
        <text>— 没有更多了 —</text>
      </view>
    </scroll-view>

    <ZTabBar current="home" />
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '../../api/index.js'
import { poiImage } from '../../api/assets.js'
import { useCityStore, RADIUS_OPTIONS } from '../../store/city.js'
import { setAssistantContext } from '../../api/storage.js'
import { useScrollHeight } from '../../composables/useScrollHeight.js'
import CyNavBar from '../../components/cy/cy-nav-bar.vue'
import CyPlaceCard from '../../components/cy/cy-place-card.vue'
import ZTabBar from '../../components/ZTabBar.vue'

const cityStore = useCityStore()
const safeBottom = ref('40rpx')
const { height: scrollH, measure: measureScroll } = useScrollHeight('.cy-scroll')

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
const consultOn = ref(false)
const brokenPoi = ref({})

const PAGE_SIZE = 20
const displayCount = ref(PAGE_SIZE)

function parseDistKm(text) {
  if (!text) return Number.POSITIVE_INFINITY
  const m = String(text).match(/([0-9.]+)\s*(km|m|公里|米)?/)
  if (!m) return Number.POSITIVE_INFINITY
  const n = parseFloat(m[1])
  return /^m|米$/i.test(m[2] || '') ? n / 1000 : n
}

const filteredPois = computed(() => {
  // 始终按距离由近到远排序（位置类列表，避免顺序看起来是乱的）
  let arr = [...pois.value].sort((a, b) => parseDistKm(a.distance) - parseDistKm(b.distance))
  if (active.value === 'free')    return arr.filter(p => (p.tags || []).some(t => /免费|免门票/.test(t)))
  if (active.value === 'indoor')  return arr.filter(p => (p.tags || []).some(t => /室内/.test(t)) || /博物|商场|书店|展馆|影院|咖啡/.test(p.category || ''))
  if (active.value === 'recommend') return arr.filter(p => (p.score ?? 0) >= 60)
  return arr
})
// 仅渲染前 displayCount 条，触底再加载
const visiblePois = computed(() => filteredPois.value.slice(0, displayCount.value))

function loadMore() {
  if (displayCount.value < filteredPois.value.length) displayCount.value += PAGE_SIZE
}
function isFilterActive(id) {
  return active.value === id || (active.value === 'all' && id === 'recommend')
}
function setFilter(id) { active.value = id; displayCount.value = PAGE_SIZE }
function setRadius(km) {
  if (cityStore.radiusKm === km) return
  cityStore.setRadius(km)        // 全局，与场景页共用
  reload()
}
function ratingFor(p) {
  if (p.rating) return Number(p.rating).toFixed(1)
  return (4.3 + ((p.id ?? 0) % 10) / 20).toFixed(1)
}
function poiThumb(poi) { return poiImage(poi, brokenPoi.value[poi?.id]) }
function onPoiImageError(poi) {
  if (poi?.id) brokenPoi.value = { ...brokenPoi.value, [poi.id]: (brokenPoi.value[poi.id] || 0) + 1 }
}

async function reload() {
  loading.value = true
  locationError.value = false
  try {
    let coords = cityStore.coords
    if (!coords?.lat) {
      const r = await new Promise((resolve, reject) => {
        uni.getLocation({ type: 'gcj02', success: resolve, fail: reject })
      })
      cityStore.setCoords(r.latitude, r.longitude)
      coords = cityStore.coords
    }
    const city = cityStore.source === 'default' ? cityStore.current : ''
    const feed = await api.getHomeFeed({ lat: coords.lat, lng: coords.lng, city, intent: 'nearby_now', radius: cityStore.radiusKm })
    if (feed?.location?.city) cityStore.setFromLocation(feed.location.city)
    pois.value = (feed.nearby_now || []).filter(p => p.nav_ready && p.lat != null && p.lng != null)
    displayCount.value = PAGE_SIZE
  } catch (_) {
    locationError.value = true
    pois.value = []
  } finally {
    loading.value = false
  }
}

function goPoi(id) {
  uni.navigateTo({ url: `/pages/poi/detail?id=${id}&lat=${cityStore.coords?.lat || ''}&lng=${cityStore.coords?.lng || ''}` })
}

function onSearch() {
  if (!consultOn.value) return
  const context = {
    city: cityStore.current,
    lat: cityStore.coords?.lat ?? '',
    lng: cityStore.coords?.lng ?? '',
    intent: 'nearby_search',
  }
  setAssistantContext(context)
  uni.switchTab({ url: '/pages/assistant/chat', success: () => uni.$emit('assistantContext', context) })
}

onMounted(() => {
  try {
    const sys = uni.getWindowInfo()
    safeBottom.value = (Math.max(sys.safeAreaInsets?.bottom || 18, 18) + 84) + 'px'
  } catch (_) {}
  try { consultOn.value = uni.getStorageSync('zhoumi_consult_on') === true } catch (_) {}
  reload()
  measureScroll()
})
</script>

<style lang="scss">
@import '../../uni.scss';

.cy-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  background: $cy-bg;
  font-family: "PingFang SC", "HarmonyOS Sans SC", "Noto Sans SC", -apple-system, system-ui, sans-serif;
}

/* scroll-view 必须有约束高度才会内部滚动并触发 @scrolltolower（否则整页滚动、加载不出更多） */
.cy-scroll { flex: 1; min-height: 0; }

.cy-filter-scroll {
  width: 100%;
  background: #fff;
  border-bottom: 1rpx solid $cy-border;
}

.cy-filter-row {
  display: flex;
  gap: 12rpx;
  padding: 16rpx 24rpx;
  white-space: nowrap;
}

.cy-filter-chip {
  flex-shrink: 0;
  height: 60rpx;
  padding: 0 36rpx;
  border-radius: 16rpx;
  display: inline-flex;
  align-items: center;
  background: #F4F5F6;
  font-size: 28rpx;
  color: $cy-text-sub;
  font-weight: 500;

  &--active {
    background: $cy-green-l;
    color: $cy-green;
    font-weight: 700;
  }
}

.cy-radius-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 14rpx 24rpx;
  background: #fff;
  border-bottom: 1rpx solid $cy-border;
}
.cy-radius-label { font-size: 26rpx; color: $cy-muted; margin-right: 4rpx; }
.cy-radius-chip {
  height: 52rpx;
  padding: 0 28rpx;
  border-radius: 26rpx;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #F4F5F6;
  font-size: 26rpx;
  color: $cy-text-sub;
  font-weight: 500;
  &--active { background: $cy-green; color: #fff; font-weight: 700; }
}
.cy-list-end { text-align: center; padding: 24rpx 0 8rpx; font-size: 22rpx; color: $cy-muted; }

.cy-hint-muted {
  text-align: center;
  color: $cy-muted;
  font-size: 26rpx;
  padding: 60rpx 0;
}

.cy-state-card {
  margin: 40rpx 24rpx 0;
  background: $cy-card;
  border-radius: 20rpx;
  padding: 40rpx 28rpx;
  text-align: center;
  box-shadow: $cy-shadow;
}

.cy-state-title {
  display: block;
  font-size: 30rpx;
  font-weight: 800;
  color: $cy-text;
  margin-bottom: 8rpx;
}

.cy-state-sub {
  display: block;
  font-size: 24rpx;
  color: $cy-text-sub;
  margin-bottom: 24rpx;
}

.cy-state-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 72rpx;
  padding: 0 40rpx;
  border-radius: 36rpx;
  background: $cy-green;
  color: #fff;
  font-size: 26rpx;
  font-weight: 700;
}

.cy-poi-list {
  display: flex;
  flex-direction: column;
  padding: 20rpx 28rpx 32rpx;
}
</style>
