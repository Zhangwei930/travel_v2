<template>
  <view class="cy-page">
    <cy-nav-bar :title="currentScene?.label || '场景结果'" right-icon="search" @right="onSearch" />

    <!-- 筛选 chips -->
    <scroll-view scroll-x class="cy-filter-scroll" :show-scrollbar="false">
      <view class="cy-filter-row">
        <view
          v-for="f in filters"
          :key="f.id"
          class="cy-filter-chip"
          :class="{ 'cy-filter-chip--active': active === f.id }"
          @tap="setFilter(f.id)"
        >
          <text>{{ f.label }}</text>
        </view>
      </view>
    </scroll-view>

    <scroll-view
      scroll-y
      class="cy-scroll"
      :style="{ paddingBottom: tabBarH }"
      :show-scrollbar="false"
    >
      <view v-if="loading" class="cy-hint-muted"><text>加载中…</text></view>
      <view v-else-if="!visiblePois.length" class="cy-hint-muted"><text>该筛选下暂无地点</text></view>

      <view class="cy-poi-list">
        <cy-place-card
          v-for="poi in visiblePois"
          :key="poi.id"
          :name="poi.name"
          :distance="poi.dist || poi.distance"
          :desc="poi.reason || poi.cat || poi.category || ''"
          :image="poiThumb(poi)"
          :rating="ratingFor(poi)"
          :tags="poi.tags || []"
          @tap="goPoi(poi.id)"
          @img-error="onPoiImageError(poi)"
        />
      </view>
    </scroll-view>

    <ZTabBar current="scenes" />
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { api } from '../../api/index.js'
import { poiImage } from '../../api/assets.js'
import { useCityStore } from '../../store/city.js'
import { setAssistantContext } from '../../api/storage.js'
import CyNavBar from '../../components/cy/cy-nav-bar.vue'
import CyPlaceCard from '../../components/cy/cy-place-card.vue'
import ZTabBar from '../../components/ZTabBar.vue'

const cityStore = useCityStore()
const tabBarH = ref('80px')
const sceneId = ref('')
const scenes  = ref([])
const currentScene = computed(() => scenes.value.find(s => s.id === sceneId.value) || null)

const filters = [
  { id: 'all',    label: '全部',   match: () => true },
  { id: 'park',   label: '公园',   match: p => /公园|绿地/.test(catText(p)) },
  { id: 'park2',  label: '乐园',   match: p => /乐园|游乐|主题/i.test(catText(p)) },
  { id: 'museum', label: '博物馆', match: p => /博物|展馆|美术|纪念/.test(catText(p)) },
  { id: 'indoor', label: '室内',   match: p => /室内|商场|书店|影院|展馆|博物|科技/.test(catText(p)) || (p.tags || []).some(t => /室内|商场/.test(t)) },
]

const active = ref('all')
const allPois = ref([])
const loading = ref(false)
const brokenPoi = ref({})

const visiblePois = computed(() => {
  const f = filters.find(x => x.id === active.value) || filters[0]
  return allPois.value.filter(f.match)
})

function catText(p) { return ((p.cat || p.category || '') + ' ' + (p.name || '')).toLowerCase() }
function setFilter(id) { active.value = id }
function ratingFor(p) {
  if (p.rating) return Number(p.rating).toFixed(1)
  return (4.2 + ((p.id ?? 0) % 10) / 20).toFixed(1)
}
function poiThumb(poi) { return poiImage(poi, brokenPoi.value[poi?.id]) }
function onPoiImageError(poi) {
  if (poi?.id) brokenPoi.value = { ...brokenPoi.value, [poi.id]: (brokenPoi.value[poi.id] || 0) + 1 }
}

onLoad((options) => {
  if (options?.scene) sceneId.value = String(options.scene)
})

async function ensureLocation() {
  if (cityStore.coords?.lat != null) return
  try {
    const r = await new Promise((resolve) => {
      uni.getLocation({ type: 'gcj02', success: resolve, fail: () => resolve({}) })
    })
    if (r.latitude != null) {
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
    const pois = await api.getScenePois(id, cityStore.current, cityStore.coords?.lat ?? null, cityStore.coords?.lng ?? null)
    allPois.value = Array.isArray(pois) ? pois : []
  } catch (_) {
    uni.showToast({ title: '场景数据加载失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    const sys = uni.getWindowInfo()
    tabBarH.value = ((sys.safeAreaInsets?.bottom || 18) + 56) + 'px'
  } catch (_) {}
  await ensureLocation()
  try { scenes.value = await api.getScenes() } catch (_) {}
  if (sceneId.value) loadScene(sceneId.value)
})

function goPoi(id) { uni.navigateTo({ url: `/pages/poi/detail?id=${id}` }) }

function onSearch() {
  const context = {
    city: cityStore.current,
    lat: cityStore.coords?.lat ?? '',
    lng: cityStore.coords?.lng ?? '',
    scene: sceneId.value,
    intent: 'scene_search',
  }
  setAssistantContext(context)
  uni.switchTab({ url: '/pages/assistant/chat', success: () => uni.$emit('assistantContext', context) })
}
</script>

<style lang="scss">
@import '../../uni.scss';

.cy-page {
  min-height: 100vh;
  background: $cy-bg;
  font-family: "PingFang SC", "HarmonyOS Sans SC", "Noto Sans SC", -apple-system, system-ui, sans-serif;
}

.cy-scroll { position: relative; }

// ── 筛选 chips ─────────────────────────────────────────────
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
  justify-content: center;
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

// ── POI 列表 ───────────────────────────────────────────────
.cy-hint-muted {
  text-align: center;
  color: $cy-muted;
  font-size: 26rpx;
  padding: 60rpx 0;
}

.cy-poi-list {
  display: flex;
  flex-direction: column;
  padding: 20rpx 28rpx 32rpx;
}
</style>
