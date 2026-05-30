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

    <!-- 距离范围（全局，多页复用）+ 数量提示 -->
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
      <text v-if="!loading && allPois.length" class="cy-count-text">
        共{{ allPois.length }}个<text v-if="active !== 'all'"> · 显示{{ visiblePois.length }}</text>
      </text>
    </view>

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
import { useCityStore, RADIUS_OPTIONS } from '../../store/city.js'
import { setAssistantContext } from '../../api/storage.js'
import CyNavBar from '../../components/cy/cy-nav-bar.vue'
import CyPlaceCard from '../../components/cy/cy-place-card.vue'
import ZTabBar from '../../components/ZTabBar.vue'

const cityStore = useCityStore()
const tabBarH = ref('80px')
const sceneId = ref('')
const scenes  = ref([])
const currentScene = computed(() => scenes.value.find(s => s.id === sceneId.value) || null)

const ALL = { id: 'all', label: '全部', re: null }
const DEFAULT_FILTERS = [
  ALL,
  { id: 'park',   label: '公园',   re: /公园|绿地|植物园/ },
  { id: 'amuse',  label: '乐园',   re: /乐园|游乐|主题/ },
  { id: 'museum', label: '博物馆', re: /博物|展馆|美术|纪念/ },
  { id: 'indoor', label: '室内',   re: /室内|商场|影院|科技|书店/ },
]
// 各场景定制子类目，让筛选更贴合（无定制则用默认）
const SCENE_FILTERS = {
  family: [ALL,
    { id: 'amuse',  label: '乐园',   re: /乐园|游乐|主题/ },
    { id: 'ocean',  label: '海洋馆', re: /海洋|水族|海底/ },
    { id: 'science',label: '科技馆', re: /科技|科学|天文/ },
    { id: 'zoo',    label: '动植物', re: /动物园|植物园|生态/ },
    { id: 'park',   label: '公园',   re: /公园|绿地/ },
    { id: 'indoor', label: '室内',   re: /室内|商场|儿童|乐高/ }],
  couple: [ALL,
    { id: 'park',   label: '公园',   re: /公园|绿地/ },
    { id: 'water',  label: '湖景',   re: /湖|江|河|湿地|滨/ },
    { id: 'town',   label: '古镇',   re: /古镇|老街|街区/ },
    { id: 'art',    label: '文艺',   re: /美术|博物|展|文创/ },
    { id: 'night',  label: '夜景',   re: /夜|观景|塔/ }],
  rainy: [ALL,
    { id: 'museum', label: '博物馆', re: /博物|展馆|美术|纪念/ },
    { id: 'science',label: '科技馆', re: /科技|科学/ },
    { id: 'mall',   label: '商场',   re: /商场|购物|广场/ },
    { id: 'ocean',  label: '水族馆', re: /海洋|水族/ },
    { id: 'cinema', label: '影院',   re: /影院|电影/ }],
  night: [ALL,
    { id: 'market', label: '夜市',   re: /夜市|小吃|美食/ },
    { id: 'bar',    label: '酒吧',   re: /酒吧|清吧/ },
    { id: 'mall',   label: '商圈',   re: /商业|步行街|广场|购物/ },
    { id: 'water',  label: '江边',   re: /江|河|湖|滨/ },
    { id: 'view',   label: '夜景',   re: /夜景|观景|塔/ }],
  walk: [ALL,
    { id: 'park',   label: '公园',   re: /公园|绿地/ },
    { id: 'green',  label: '绿道',   re: /绿道|步道|健身/ },
    { id: 'town',   label: '古镇',   re: /古镇|老街|街区/ },
    { id: 'water',  label: '江边',   re: /江|河|湖|滨/ }],
  photo: [ALL,
    { id: 'town',   label: '古镇',   re: /古镇|老街|街区/ },
    { id: 'flower', label: '花海',   re: /花|植物园|公园/ },
    { id: 'water',  label: '湖景',   re: /湖|江|河|湿地/ },
    { id: 'art',    label: '文艺',   re: /美术|博物|文创|网红/ }],
  fish: [ALL,
    { id: 'reservoir', label: '水库', re: /水库/ },
    { id: 'wetland',   label: '湿地', re: /湿地/ },
    { id: 'pond',      label: '鱼塘', re: /鱼塘|垂钓|钓/ },
    { id: 'park',      label: '公园', re: /公园|湖/ }],
  old: [ALL,
    { id: 'park',   label: '公园',   re: /公园|绿地/ },
    { id: 'town',   label: '古镇',   re: /古镇|老街/ },
    { id: 'museum', label: '博物馆', re: /博物|展馆|纪念/ },
    { id: 'temple', label: '寺庙',   re: /寺|庙|观/ }],
  budget: [ALL,
    { id: 'park',   label: '公园',   re: /公园|绿地|广场/ },
    { id: 'museum', label: '博物馆', re: /博物|展馆|美术/ },
    { id: 'green',  label: '绿道',   re: /绿道|步道/ },
    { id: 'water',  label: '江湖',   re: /江|河|湖/ }],
}

const filters = computed(() => SCENE_FILTERS[sceneId.value] || DEFAULT_FILTERS)

const active = ref('all')
const allPois = ref([])
const loading = ref(false)
const brokenPoi = ref({})

const visiblePois = computed(() => {
  const f = filters.value.find(x => x.id === active.value) || filters.value[0]
  if (!f.re) return allPois.value
  return allPois.value.filter(p => f.re.test(catText(p)))
})

function catText(p) { return ((p.cat || p.category || '') + ' ' + (p.name || '')).toLowerCase() }
function setFilter(id) { active.value = id }
function setRadius(km) {
  if (cityStore.radiusKm === km) return
  cityStore.setRadius(km)        // 写全局 + 持久化，其他页面复用
  if (sceneId.value) loadScene(sceneId.value)
}
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
    const pois = await api.getScenePois(id, cityStore.current, cityStore.coords?.lat ?? null, cityStore.coords?.lng ?? null, cityStore.radiusKm)
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

// ── 距离范围行 ─────────────────────────────────────────────
.cy-radius-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 14rpx 24rpx;
  background: #fff;
  border-bottom: 1rpx solid $cy-border;
}

.cy-radius-label { font-size: 26rpx; color: $cy-muted; margin-right: 4rpx; }
.cy-count-text { margin-left: auto; font-size: 24rpx; color: $cy-muted; }

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

  &--active {
    background: $cy-green;
    color: #fff;
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
