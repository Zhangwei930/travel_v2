<template>
  <view class="page">
    <!-- ══ HEADER 白色 ════════════════════════════════════════ -->
    <view class="header" :style="{ paddingTop: statusBarHeight + 'px' }">
      <text class="header-mono mono">§ SCENES · INDEX</text>
      <text class="header-title serif">按场景索引</text>
      <text class="header-sub">选择场景，AI 推荐最合适的地点和路线</text>

      <!-- 场景胶囊横滑 -->
      <scroll-view scroll-x class="chips-scroll" :show-scrollbar="false">
        <view class="chips-row">
          <view
            v-for="s in scenes"
            :key="s.id"
            class="scene-chip"
            :style="{
              background: active === s.id ? s.color : '#F5F1EB',
              color: active === s.id ? '#fff' : '#1A2E2C',
            }"
            @tap="setActive(s.id)"
          >
            <text class="chip-no mono" :style="{ opacity: active === s.id ? 0.85 : 0.5 }">{{ s.no }}</text>
            <text class="chip-icon">{{ s.icon }}</text>
            <text class="chip-label">{{ s.label }}</text>
          </view>
        </view>
      </scroll-view>
    </view>

    <!-- ══ 滚动内容区 ═══════════════════════════════════════════ -->
    <scroll-view
      scroll-y
      class="scroll-body"
      :style="{ paddingBottom: tabBarHeight }"
      :show-scrollbar="false"
    >
      <!-- ── Scene Hero ────────────────────────────────────────── -->
      <view v-if="currentScene" class="scene-hero" :style="{ background: `linear-gradient(135deg, ${currentScene.color}, ${currentScene.color}DD)` }">
        <view class="hero-inner">
          <text class="hero-icon">{{ currentScene.icon }}</text>
          <view class="hero-text">
            <text class="hero-mono mono">SCENE · {{ currentScene.no }}</text>
            <text class="hero-title serif">{{ currentScene.label }}</text>
            <text class="hero-desc">{{ currentScene.desc }}</text>
          </view>
        </view>
      </view>

      <!-- ── 装备清单（仅当后端返回非空时显示）─────────────────── -->
      <view v-if="currentScene && gearList.length" class="section gear-section">
        <view class="gear-card">
          <view class="gear-head">
            <text class="gear-title serif">🎒 装备清单</text>
            <text class="gear-count mono">{{ gearList.length }} 件</text>
          </view>
          <view class="gear-grid">
            <view v-for="item in gearList" :key="item" class="gear-item">
              <view class="gear-check" :style="{ borderColor: currentScene.color }">
                <svg xmlns="http://www.w3.org/2000/svg" width="9" height="9" viewBox="0 0 9 9">
                  <path d="M1.5 4.5l2 2 4-4" :stroke="currentScene.color" stroke-width="1.8" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </view>
              <text class="gear-label">{{ item }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- ── §R 推荐路线 ─────────────────────────────────────────── -->
      <view class="section">
        <z-section-header
          no="R"
          :title="'推荐路线'"
          :sub="(currentScene?.label ?? '场景') + ' · 已策划'"
        />
        <view v-if="!sceneRoutes.length" class="list-empty mono">暂无该场景路线</view>
        <view class="routes-list">
          <view
            v-for="route in sceneRoutes"
            :key="route.id"
            class="route-card"
            @tap="goResult(route)"
          >
            <view class="route-cover">
              <image :src="route.img" class="route-img" mode="aspectFill" lazy-load />
              <!-- 底部渐变遮罩 -->
              <view class="route-cover-mask" />
              <!-- R-0x 编号 -->
              <view class="route-no-badge" :style="{ color: route.color }">
                <text class="mono">{{ route.no }}</text>
              </view>
              <!-- 底部信息 -->
              <view class="route-cover-info">
                <text class="route-cover-title serif">{{ route.title }}</text>
                <text class="route-cover-meta">🕐 {{ route.duration }} · 💰 {{ route.budget }} · 📍 {{ route.poi }}站</text>
              </view>
            </view>
            <view class="route-body">
              <text class="route-summary">{{ route.summary }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- ── §P 推荐地点 ─────────────────────────────────────────── -->
      <view class="section">
        <z-section-header
          no="P"
          :title="'推荐地点'"
          :sub="(currentScene?.label ?? '场景') + ' · POI'"
        />

        <view v-if="!scenePois.length" class="list-empty mono">暂无该场景地点</view>
        <!-- 钓鱼场景：单列大卡 -->
        <view v-if="isFish" class="poi-list-single">
          <view
            v-for="poi in scenePois"
            :key="poi.id"
            class="poi-card-large"
            @tap="goPoi(poi.id)"
          >
            <view class="poi-large-img-wrap">
              <image :src="poi.img" class="poi-large-img" mode="aspectFill" lazy-load />
              <view class="poi-badge-no mono">{{ poi.no }}</view>
              <view class="poi-badge-dist">{{ poi.dist }}</view>
            </view>
            <view class="poi-large-body">
              <text class="poi-large-name serif">{{ poi.name }}</text>
              <text class="poi-large-meta">🕐 {{ poi.time }} · {{ poi.budget }}</text>
            </view>
          </view>
        </view>

        <!-- 其他场景：2 列网格 -->
        <view v-else class="poi-grid">
          <view
            v-for="poi in scenePois"
            :key="poi.id"
            class="poi-grid-card"
            @tap="goPoi(poi.id)"
          >
            <view class="poi-grid-img-wrap">
              <image :src="poi.img" class="poi-grid-img" mode="aspectFill" lazy-load />
              <view class="poi-badge-no mono">{{ poi.no }}</view>
              <view class="poi-badge-dist">{{ poi.dist }}</view>
            </view>
            <view class="poi-grid-body">
              <text class="poi-grid-name serif">{{ poi.name }}</text>
              <text class="poi-grid-meta">🕐 {{ poi.time }} · {{ poi.budget }}</text>
            </view>
          </view>
        </view>
      </view>
    </scroll-view>

    <!-- ══ 底部 Tab Bar ════════════════════════════════════════ -->
    <z-tab-bar current="scenes" />
  </view>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { api } from '../../api/mock.js'
import { useCityStore } from '../../store/city.js'
import { consumePendingScene } from '../../api/storage.js'
import ZSectionHeader from '../../components/ZSectionHeader.vue'
import ZTabBar from '../../components/ZTabBar.vue'

const cityStore = useCityStore()

const statusBarHeight = ref(44)
const tabBarHeight    = ref('80px')

const scenes = ref([])
const active = ref('fish')  // 默认钓鱼

const currentScene = computed(() => scenes.value.find(s => s.id === active.value) || scenes.value[0] || null)
const isFish       = computed(() => active.value === 'fish')
const gearList     = ref([])

const sceneRoutes  = ref([])
const scenePois    = ref([])

async function loadScene(id) {
  // 先清空，避免切换场景时残留上一个场景的装备
  gearList.value = []
  const city = cityStore.current
  // 优先用 store 缓存的坐标，缺失时不阻塞（后端用 city 中心兜底）
  const lat = cityStore.coords?.lat ?? null
  const lng = cityStore.coords?.lng ?? null
  try {
    const [routes, pois] = await Promise.all([
      api.getSceneRoutes(id, city),
      api.getScenePois(id, city, lat, lng),
    ])
    sceneRoutes.value = routes
    scenePois.value   = pois
  } catch (e) {
    uni.showToast({ title: '场景数据加载失败', icon: 'none' })
  }
  try {
    const gear = await api.getGearList(id)
    gearList.value = Array.isArray(gear) ? gear : []
  } catch (_) {
    gearList.value = []
  }
}

// 没有缓存坐标时主动定位一次（用户没经过首页直接进 scenes 的场景）
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

watch(active, loadScene)

function applyPendingScene() {
  const pendingScene = consumePendingScene()
  if (!pendingScene) return false
  if (pendingScene !== active.value) {
    active.value = pendingScene
  } else {
    loadScene(active.value)
  }
  return true
}

function applyHomeLocationContext(context = {}) {
  const lat = Number(context.lat)
  const lng = Number(context.lng)
  if (Number.isFinite(lat) && Number.isFinite(lng)) cityStore.setCoords(lat, lng)
  if (context.city) cityStore.setFromLocation(context.city)
}

onMounted(async () => {
  try {
    const sys = uni.getSystemInfoSync()
    statusBarHeight.value = sys.statusBarHeight || 44
    const tabH = (sys.safeAreaInsets?.bottom || 18) + 56
    tabBarHeight.value = tabH + 'px'
  } catch (_) {}

  // 拿到坐标后再加载场景数据，确保 POI 是当地真实景点
  await ensureLocation()
  try {
    scenes.value = await api.getScenes()
  } catch (e) {
    uni.showToast({ title: '场景列表加载失败', icon: 'none' })
  }
  const loadedByPendingScene = applyPendingScene()
  if (!loadedByPendingScene) loadScene(active.value)

  // 监听从首页传过来的场景切换事件
  uni.$on('switchScene', (sceneId) => {
    active.value = sceneId
  })
  uni.$on('homeLocationContext', applyHomeLocationContext)
  // 城市切换时重新加载场景数据
  uni.$on('cityChanged', () => loadScene(active.value))
})

onShow(() => {
  applyPendingScene()
})

onUnmounted(() => {
  uni.$off('switchScene')
  uni.$off('homeLocationContext', applyHomeLocationContext)
  uni.$off('cityChanged')
})

function setActive(id) {
  active.value = id
}

const TAG_SCENE = { '亲子': 'family', '情侣': 'couple', '雨天': 'rainy', '低预算': 'budget', '钓鱼': 'fish', '拍照': 'photo', '夜游': 'night', 'Citywalk': 'walk', '适老': 'old' }

async function goResult(route) {
  uni.showLoading({ title: '生成中…', mask: true })
  try {
    const plan = await api.generateTrip({
      city: cityStore.current, scene: TAG_SCENE[route.tag] || '', preferences: [route.tag],
    })
    if (!plan || !Array.isArray(plan.stops) || plan.stops.length === 0) {
      throw new Error('plan-invalid')
    }
    uni.setStorageSync('lastPlan', plan)
    uni.hideLoading()
    uni.navigateTo({ url: `/pages/result/result?generated=1&no=${encodeURIComponent(plan.no)}` })
  } catch (_) {
    uni.hideLoading()
    uni.showToast({ title: '生成失败，请稍后再试', icon: 'none' })
  }
}

function goPoi(id) {
  uni.navigateTo({ url: `/pages/poi/detail?id=${id}` })
}
</script>

<style lang="scss">
@import '../../uni.scss';

.list-empty {
  color: $z-muted;
  font-family: $mono;
  font-size: $font-mono;
  padding: 20rpx 0;
  display: block;
}

.page {
  min-height: 100vh;
  background: $z-bg;
}

// ── Header 白色 ──────────────────────────────────────────────
.header {
  background: $z-card;
  padding: 0 32rpx 0;
}

.header-mono {
  display: block;
  font-size: 20rpx;
  color: $z-muted;
  letter-spacing: 3rpx;
  margin-bottom: 8rpx;
  padding-top: 16rpx;
}

.header-title {
  display: block;
  font-size: 42rpx;
  font-weight: 900;
  color: $z-text;
  margin-bottom: 6rpx;
}

.header-sub {
  display: block;
  font-size: 24rpx;
  color: $z-muted;
  margin-bottom: 26rpx;
}

// 场景胶囊横滑
.chips-scroll {
  width: 100%;
  margin-left: -32rpx;
  padding-left: 32rpx;
}

.chips-row {
  display: flex;
  gap: 12rpx;
  padding-bottom: 22rpx;
  padding-right: 32rpx;
  white-space: nowrap;
}

.scene-chip {
  display: inline-flex;
  align-items: center;
  gap: 10rpx;
  padding: 12rpx 24rpx;
  border-radius: $radius-pill;
  font-size: 24rpx;
  font-weight: 700;
  white-space: nowrap;
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.2s;
}

.chip-no {
  font-size: 18rpx;
}

.chip-icon {
  font-size: 26rpx;
}

.chip-label {
  font-size: 24rpx;
}

// ── Scene Hero ───────────────────────────────────────────────
.scene-hero {
  margin: 24rpx 32rpx 0;
  border-radius: 26rpx;
  padding: 30rpx 32rpx;
}

.hero-inner {
  display: flex;
  align-items: center;
  gap: 22rpx;
}

.hero-icon {
  font-size: 64rpx;
  flex-shrink: 0;
}

.hero-text {
  flex: 1;
}

.hero-mono {
  display: block;
  font-size: 20rpx;
  color: rgba(255, 255, 255, 0.7);
  letter-spacing: 2.4rpx;
  margin-bottom: 4rpx;
}

.hero-title {
  display: block;
  color: $z-card;
  font-size: 38rpx;
  font-weight: 900;
  margin-bottom: 4rpx;
}

.hero-desc {
  display: block;
  color: rgba(255, 255, 255, 0.85);
  font-size: 24rpx;
}

// ── 通用 section ─────────────────────────────────────────────
.section {
  padding: 32rpx 32rpx 0;
}

// ── 装备清单 ─────────────────────────────────────────────────
.gear-card {
  background: $z-card;
  border-radius: $radius-card;
  padding: 26rpx 28rpx;
  box-shadow: 0 2rpx 10rpx rgba(13, 79, 74, 0.05);
}

.gear-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 18rpx;
}

.gear-title {
  font-size: 27rpx;
  font-weight: 800;
  color: $z-text;
}

.gear-count {
  font-size: 20rpx;
  color: $z-muted;
  letter-spacing: 1rpx;
}

.gear-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8rpx 28rpx;
}

.gear-item {
  display: flex;
  align-items: center;
  gap: 14rpx;
  font-size: 23rpx;
  color: $z-text2;
  padding: 8rpx 0;
}

.gear-check {
  width: 30rpx;
  height: 30rpx;
  border-radius: 8rpx;
  border: 3rpx solid;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.gear-label {
  font-size: 23rpx;
  color: $z-text2;
}

// ── 路线卡片 ─────────────────────────────────────────────────
.routes-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.route-card {
  background: $z-card;
  border-radius: $radius-card;
  overflow: hidden;
  box-shadow: 0 2rpx 12rpx rgba(13, 79, 74, 0.06);
  cursor: pointer;
}

.route-cover {
  height: 230rpx;
  position: relative;
  overflow: hidden;
}

.route-img {
  width: 100%;
  height: 100%;
}

.route-cover-mask {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(13, 79, 74, 0.72), transparent 60%);
}

.route-no-badge {
  position: absolute;
  top: 16rpx;
  left: 22rpx;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 10rpx;
  padding: 4rpx 14rpx;
  font-size: 20rpx;
  font-weight: 700;
  letter-spacing: 1rpx;
  z-index: 1;
}

.route-cover-info {
  position: absolute;
  bottom: 18rpx;
  left: 22rpx;
  right: 22rpx;
  z-index: 1;
}

.route-cover-title {
  display: block;
  color: $z-card;
  font-size: 30rpx;
  font-weight: 800;
  margin-bottom: 6rpx;
}

.route-cover-meta {
  display: block;
  color: rgba(255, 255, 255, 0.85);
  font-size: 22rpx;
}

.route-body {
  padding: 20rpx 26rpx;
}

.route-summary {
  display: block;
  font-size: 24rpx;
  color: $z-muted;
  line-height: 1.5;
}

// ── §P 推荐地点（单列大卡，钓鱼） ────────────────────────────
.poi-list-single {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.poi-card-large {
  background: $z-card;
  border-radius: $radius-card;
  overflow: hidden;
  box-shadow: 0 2rpx 12rpx rgba(13, 79, 74, 0.06);
  cursor: pointer;
}

.poi-large-img-wrap {
  height: 200rpx;
  position: relative;
  overflow: hidden;
}

.poi-large-img {
  width: 100%;
  height: 100%;
}

.poi-badge-no {
  position: absolute;
  top: 10rpx;
  left: 10rpx;
  background: rgba(0, 0, 0, 0.6);
  color: $z-card;
  font-size: 18rpx;
  padding: 3rpx 10rpx;
  border-radius: 8rpx;
  letter-spacing: 1rpx;
}

.poi-badge-dist {
  position: absolute;
  top: 10rpx;
  right: 10rpx;
  background: rgba(0, 0, 0, 0.6);
  color: $z-card;
  font-size: 18rpx;
  padding: 3rpx 10rpx;
  border-radius: 8rpx;
}

.poi-large-body {
  padding: 16rpx 22rpx;
}

.poi-large-name {
  display: block;
  font-size: 25rpx;
  font-weight: 700;
  color: $z-text;
  margin-bottom: 6rpx;
}

.poi-large-meta {
  display: block;
  font-size: 20rpx;
  color: $z-muted;
}

// ── §P 推荐地点（2 列网格） ────────────────────────────────────
.poi-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18rpx;
}

.poi-grid-card {
  background: $z-card;
  border-radius: $radius-small;
  overflow: hidden;
  box-shadow: 0 2rpx 12rpx rgba(13, 79, 74, 0.06);
  cursor: pointer;
}

.poi-grid-img-wrap {
  height: 168rpx;
  position: relative;
  overflow: hidden;
}

.poi-grid-img {
  width: 100%;
  height: 100%;
}

.poi-grid-body {
  padding: 16rpx 20rpx;
}

.poi-grid-name {
  display: block;
  font-size: 25rpx;
  font-weight: 700;
  color: $z-text;
  margin-bottom: 4rpx;
}

.poi-grid-meta {
  display: block;
  font-size: 20rpx;
  color: $z-muted;
}
</style>
