<template>
  <view class="page">
    <u-nav-bar :title="currentScene?.label || '场景结果'" right-icon="search" @right="onSearch" />

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
      :style="{ paddingBottom: tabBarHeight }"
      :show-scrollbar="false"
    >
      <view v-if="loading" class="hint">加载中…</view>
      <view v-else-if="!visiblePois.length" class="hint">该筛选下暂无地点</view>

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
              <text class="poi-dist">{{ poi.dist || poi.distance }}</text>
            </view>
            <text class="poi-reason">{{ poi.reason || poi.cat || '' }}</text>
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

    <z-tab-bar current="scenes" />
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { api } from '../../api/mock.js'
import { poiImage } from '../../api/assets.js'
import { useCityStore } from '../../store/city.js'
import { setAssistantContext } from '../../api/storage.js'
import ZTabBar from '../../components/ZTabBar.vue'
import UNavBar from '../../components/UNavBar.vue'

const cityStore = useCityStore()
const tabBarHeight = ref('80px')

const sceneId = ref('')
const scenes  = ref([])
const currentScene = computed(() => scenes.value.find(s => s.id === sceneId.value) || null)

const filters = [
  { id: 'all',     label: '全部',   match: () => true },
  { id: 'park',    label: '公园',   match: p => /公园|公园|绿地/.test(catText(p)) },
  { id: 'park2',   label: '乐园',   match: p => /乐园|游乐|主题|playground/i.test(catText(p)) },
  { id: 'museum',  label: '博物馆', match: p => /博物|展馆|美术|纪念/.test(catText(p)) },
  { id: 'indoor',  label: '室内',   match: p => /室内|商场|书店|影院|展馆|博物|科技|咖啡/.test(catText(p)) || (p.tags || []).some(t => /室内|商场/.test(t)) },
]

const active = ref('all')
const allPois = ref([])
const loading = ref(false)
const brokenPoiImages = ref({})

const visiblePois = computed(() => {
  const f = filters.find(x => x.id === active.value) || filters[0]
  return allPois.value.filter(f.match)
})

function catText(p) { return ((p.cat || p.category || '') + ' ' + (p.name || '')).toLowerCase() }
function setFilter(id) { active.value = id }

function ratingFor(p) {
  if (p.rating) return Number(p.rating).toFixed(1)
  const seed = (p.id ?? 0) % 10
  return (4.2 + seed / 20).toFixed(1)
}

function poiThumb(poi) {
  return poiImage(poi, brokenPoiImages.value[poi?.id])
}

function onPoiImageError(poi) {
  if (!poi?.id) return
  brokenPoiImages.value = { ...brokenPoiImages.value, [poi.id]: true }
}

onLoad((options) => {
  const raw = options?.scene
  if (raw) sceneId.value = String(raw)
})

async function ensureLocation() {
  if (cityStore.coords?.lat != null) return
  try {
    const r = await new Promise((resolve) => {
      uni.getLocation({ type: 'gcj02', success: resolve, fail: () => resolve({}) })
    })
    if (r.latitude != null && r.longitude != null) {
      cityStore.setCoords(r.latitude, r.longitude)
      try {
        const g = await api.geoCity(r.latitude, r.longitude)
        if (g?.city) cityStore.setFromLocation(g.city)
      } catch (_) {}
    }
  } catch (_) {}
}

async function loadScene(id) {
  if (!id) return
  loading.value = true
  try {
    const city = cityStore.current
    const lat = cityStore.coords?.lat ?? null
    const lng = cityStore.coords?.lng ?? null
    const pois = await api.getScenePois(id, city, lat, lng)
    allPois.value = Array.isArray(pois) ? pois : []
  } catch (_) {
    uni.showToast({ title: '场景数据加载失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    const sys = uni.getSystemInfoSync()
    const tabH = (sys.safeAreaInsets?.bottom || 18) + 56
    tabBarHeight.value = tabH + 'px'
  } catch (_) {}

  await ensureLocation()
  try {
    scenes.value = await api.getScenes()
  } catch (_) {}
  if (sceneId.value) loadScene(sceneId.value)
})

function goPoi(id) {
  uni.navigateTo({ url: `/pages/poi/detail?id=${id}` })
}

function onSearch() {
  const context = {
    city: cityStore.current,
    lat: cityStore.coords?.lat ?? '',
    lng: cityStore.coords?.lng ?? '',
    scene: sceneId.value,
    intent: 'scene_search',
  }
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

// ── 筛选 pill ──────────────────────────────────────────────
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

// ── POI 列表 ───────────────────────────────────────────────
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
