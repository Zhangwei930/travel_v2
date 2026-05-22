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
      <view class="scene-hero" :style="{ background: `linear-gradient(135deg, ${currentScene.color}, ${currentScene.color}DD)` }">
        <view class="hero-inner">
          <text class="hero-icon">{{ currentScene.icon }}</text>
          <view class="hero-text">
            <text class="hero-mono mono">SCENE · {{ currentScene.no }}</text>
            <text class="hero-title serif">{{ currentScene.label }}</text>
            <text class="hero-desc">{{ currentScene.desc }}</text>
          </view>
        </view>
      </view>

      <!-- ── 钓鱼专属：装备清单 ─────────────────────────────────── -->
      <view v-if="isFish" class="section gear-section">
        <view class="gear-card">
          <view class="gear-head">
            <text class="gear-title serif">🎒 装备清单</text>
            <text class="gear-count mono">{{ gearList.length }} ITEMS</text>
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
          <view class="gear-footer">
            <text class="gear-footer-label">⏰ 黄金时段</text>
            <text class="gear-golden" :style="{ color: currentScene.color }">05:30 – 10:00 · 18:00 – 20:00</text>
          </view>
        </view>
      </view>

      <!-- ── §R 推荐路线 ─────────────────────────────────────────── -->
      <view class="section">
        <z-section-header
          no="R"
          :title="'推荐路线'"
          :sub="currentScene.label + ' · 已策划'"
        />
        <view class="routes-list">
          <view
            v-for="route in sceneRoutes"
            :key="route.id"
            class="route-card"
            @tap="goResult(route.id)"
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
          :sub="currentScene.label + ' · POI'"
        />

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
import { SCENES, GEAR_LIST, api } from '../../api/mock.js'
import ZSectionHeader from '../../components/ZSectionHeader.vue'
import ZTabBar from '../../components/ZTabBar.vue'

const statusBarHeight = ref(44)
const tabBarHeight    = ref('80px')

const scenes = ref(SCENES)
const active = ref('fish')  // 默认钓鱼

const currentScene = computed(() => scenes.value.find(s => s.id === active.value) || scenes.value[0])
const isFish       = computed(() => active.value === 'fish')
const gearList     = ref(GEAR_LIST)

const sceneRoutes  = ref([])
const scenePois    = ref([])

async function loadScene(id) {
  try {
    const [routes, pois] = await Promise.all([
      api.getSceneRoutes(id), api.getScenePois(id),
    ])
    sceneRoutes.value = routes
    scenePois.value   = pois
  } catch (_) {}
}

watch(active, loadScene)

onMounted(async () => {
  try {
    const sys = uni.getSystemInfoSync()
    statusBarHeight.value = sys.statusBarHeight || 44
    const tabH = (sys.safeAreaInsets?.bottom || 18) + 56
    tabBarHeight.value = tabH + 'px'
  } catch (_) {}

  try {
    scenes.value = await api.getScenes()
  } catch (_) {}
  loadScene(active.value)

  // 监听从首页传过来的场景切换事件
  uni.$on('switchScene', (sceneId) => {
    active.value = sceneId
  })
})

onUnmounted(() => {
  uni.$off('switchScene')
})

function setActive(id) {
  active.value = id
}

function goResult(routeId) {
  uni.navigateTo({ url: `/pages/result/result?routeId=${routeId}` })
}

function goPoi(id) {
  uni.navigateTo({ url: `/pages/poi/detail?id=${id}` })
}
</script>

<style lang="scss">
@import '../../uni.scss';

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
  color: #fff;
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

.gear-footer {
  margin-top: 20rpx;
  padding-top: 16rpx;
  border-top: 2rpx dashed $z-border;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.gear-footer-label {
  font-size: 22rpx;
  color: $z-muted;
}

.gear-golden {
  font-size: 22rpx;
  font-weight: 700;
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
  color: #fff;
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
  color: #fff;
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
  color: #fff;
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
