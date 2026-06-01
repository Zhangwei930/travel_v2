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

    <!-- 距离范围 -->
    <view class="cy-radius-row">
      <text class="cy-radius-label">范围</text>
      <view
        v-for="km in radiusOptions"
        :key="km"
        class="cy-radius-chip"
        :class="{ 'cy-radius-chip--active': activeRadius === km }"
        @tap="setRadius(km)"
      >
        <text>{{ km }}km</text>
      </view>
    </view>

    <!-- 排序方式 -->
    <view class="cy-radius-row">
      <text class="cy-radius-label">排序</text>
      <view
        v-for="opt in SORT_OPTIONS"
        :key="opt.id"
        class="cy-radius-chip"
        :class="{ 'cy-radius-chip--active': sortMode === opt.id }"
        @tap="setSort(opt.id)"
      >
        <text>{{ opt.label }}</text>
      </view>
    </view>

    <scroll-view
      scroll-y
      class="cy-scroll"
      :style="{ height: scrollH ? scrollH + 'px' : '70vh', paddingBottom: tabBarH }"
      :show-scrollbar="false"
      @scrolltolower="loadMore"
    >
      <view v-if="loading" class="cy-hint-muted"><text>加载中…</text></view>
      <view v-else-if="!filteredPois.length" class="cy-hint-muted"><text>该筛选下暂无地点</text></view>

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

      <view v-if="filteredPois.length && visiblePois.length >= filteredPois.length" class="cy-list-end">
        <text>— 没有更多了 —</text>
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
import { useScrollHeight } from '../../composables/useScrollHeight.js'
import CyNavBar from '../../components/cy/cy-nav-bar.vue'
import CyPlaceCard from '../../components/cy/cy-place-card.vue'
import ZTabBar from '../../components/ZTabBar.vue'

const cityStore = useCityStore()
const tabBarH = ref('80px')
const { height: scrollH, measure: measureScroll } = useScrollHeight('.cy-scroll')
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
    { id: 'ocean',  label: '海洋馆', re: /海洋|水族|海底/ },
    { id: 'science',label: '科技馆', re: /科技|科学|天文/ },
    { id: 'zoo',    label: '动植物', re: /动物园|植物园|生态/ },
    { id: 'park',   label: '公园',   re: /公园|绿地/ },
    { id: 'amuse',  label: '乐园',   re: /乐园|游乐|主题|儿童/ }],
  couple: [ALL,
    { id: 'water',  label: '湖景',   re: /湖|江|河|湿地|滨/ },
    { id: 'town',   label: '古镇',   re: /古镇|老街|街区/ },
    { id: 'park',   label: '公园',   re: /公园|绿地/ }],
  rainy: [ALL,
    { id: 'science',label: '科技馆', re: /科技|科学/ },
    { id: 'mall',   label: '商场',   re: /商场|购物|广场/ },
    { id: 'museum', label: '博物馆', re: /博物|展馆|美术|纪念/ }],
  night: [ALL,
    { id: 'market', label: '夜市',   re: /夜市|小吃|美食/ },
    { id: 'bar',    label: '酒吧',   re: /酒吧|清吧/ },
    { id: 'mall',   label: '商圈',   re: /商业|步行街|广场|购物/ }],
  walk: [ALL,
    { id: 'water',  label: '江边',   re: /江|河|湖|滨/ },
    { id: 'green',  label: '绿道',   re: /绿道|步道|健身/ },
    { id: 'town',   label: '古镇',   re: /古镇|老街|街区/ },
    { id: 'park',   label: '公园',   re: /公园|绿地/ }],
  photo: [ALL,
    { id: 'town',   label: '古镇',   re: /古镇|老街|街区/ },
    { id: 'flower', label: '花海',   re: /花|植物园|公园/ },
    { id: 'water',  label: '湖景',   re: /湖|江|河|湿地/ },
    { id: 'art',    label: '文艺',   re: /美术|博物|文创|网红/ }],
  fish: [ALL,
    { id: 'reservoir', label: '水库', re: /水库/ },
    { id: 'pond',      label: '钓场', re: /钓鱼|垂钓|钓场|鱼塘|渔场|钓鱼园/ }],
  old: [ALL,
    { id: 'town',   label: '古镇',   re: /古镇|老街/ },
    { id: 'museum', label: '博物馆', re: /博物|展馆|纪念/ },
    { id: 'park',   label: '公园',   re: /公园|绿地/ }],
  budget: [ALL,
    { id: 'water',  label: '江湖',   re: /江|河|湖/ },
    { id: 'green',  label: '绿道',   re: /绿道|步道/ },
    { id: 'museum', label: '博物馆', re: /博物|展馆|美术/ },
    { id: 'park',   label: '公园',   re: /公园|绿地|广场/ }],
  food: [ALL,
    { id: 'hotpot',  label: '火锅',   re: /火锅|串串|冒菜|麻辣烫|钵钵鸡/ },
    { id: 'sichuan', label: '川菜',   re: /川菜|家常|小炒|酒楼|饭庄|食府/ },
    { id: 'bbq',     label: '烧烤',   re: /烧烤|烤肉|烤鱼|铁板|江湖菜/ },
    { id: 'snack',   label: '小吃',   re: /小吃|面|粉|抄手|水饺|包子|快餐|钟水饺/ },
    { id: 'western', label: '西餐日韩', re: /西餐|牛排|披萨|汉堡|日料|韩式|料理|寿司|自助/ }],
  hike: [ALL,
    { id: 'mountain', label: '山峰',     re: /山|峰|岭|崖|峡/ },
    { id: 'forest',   label: '森林公园', re: /森林|国家.*公园|自然保护/ },
    { id: 'trail',    label: '徒步道',   re: /步道|栈道|古道/ },
    { id: 'scenic',   label: '风景区',   re: /风景|景区|景点/ }],
  cycle: [ALL,
    { id: 'lake',   label: '环湖', re: /湖/ },
    { id: 'river',  label: '江河', re: /江|河|滨/ },
    { id: 'green',  label: '绿道', re: /绿道|骑行|自行车|步道/ }],
  camp: [ALL,
    { id: 'lake',   label: '湖畔', re: /湖|水库|江|河|滨|溪/ },
    { id: 'forest', label: '森林', re: /森林|林/ },
    { id: 'wild',   label: '山野', re: /山|谷|郊野|旷野/ }],
}

const filters = computed(() => SCENE_FILTERS[sceneId.value] || DEFAULT_FILTERS)
const HIKE_RADIUS_OPTIONS = [150]
const radiusOptions = computed(() => sceneId.value === 'hike' ? HIKE_RADIUS_OPTIONS : RADIUS_OPTIONS)
const activeRadius = computed(() => sceneId.value === 'hike' ? 150 : cityStore.radiusKm)

const SORT_OPTIONS = [{ id: 'distance', label: '距离' }, { id: 'hot', label: '热度' }]
const sortMode = ref('distance')

const active = ref('all')
const allPois = ref([])
const loading = ref(false)
const brokenPoi = ref({})

const PAGE_SIZE = 20
const displayCount = ref(PAGE_SIZE)   // 已展示条数，触底自增（无分页、无总数显示）

// 互斥归类：每个 POI 只归第一个命中的类目（按 filters 顺序，具体在前、兜底在后）
function catOf(p) {
  const txt = catText(p)
  for (const f of filters.value) {
    if (f.re && f.re.test(txt)) return f.id
  }
  return ''   // 一个类目都不匹配，仅出现在「全部」
}
const filteredPois = computed(() => {
  if (active.value === 'all') return allPois.value
  return allPois.value.filter(p => catOf(p) === active.value)
})
// 仅渲染前 displayCount 条，往下拉触底再加载更多
const visiblePois = computed(() => filteredPois.value.slice(0, displayCount.value))

function loadMore() {
  if (displayCount.value < filteredPois.value.length) displayCount.value += PAGE_SIZE
}

function catText(p) { return ((p.cat || p.category || '') + ' ' + (p.name || '')).toLowerCase() }
function setFilter(id) { active.value = id; displayCount.value = PAGE_SIZE }
function setRadius(km) {
  const next = Number(km)
  if (activeRadius.value === next) return
  if (sceneId.value !== 'hike') cityStore.setRadius(next)    // 15/30/50 仍写全局 + 持久化，其他页面复用
  if (sceneId.value) loadScene(sceneId.value)
}
function setSort(mode) {
  if (sortMode.value === mode) return
  sortMode.value = mode
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
    const pois = await api.getScenePois(id, cityStore.current, cityStore.coords?.lat ?? null, cityStore.coords?.lng ?? null, activeRadius.value, sortMode.value)
    allPois.value = Array.isArray(pois) ? pois : []
    displayCount.value = PAGE_SIZE   // 重新加载后回到第一屏
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
  measureScroll()
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
  height: 100vh;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  background: $cy-bg;
  font-family: "PingFang SC", "HarmonyOS Sans SC", "Noto Sans SC", -apple-system, system-ui, sans-serif;
}

/* scroll-view 必须有约束高度才会内部滚动并触发 @scrolltolower（否则整页滚动、加载不出更多） */
.cy-scroll { position: relative; flex: 1; min-height: 0; }

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

.cy-list-end {
  text-align: center;
  padding: 24rpx 0 8rpx;
  font-size: 22rpx;
  color: $cy-muted;
}

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
