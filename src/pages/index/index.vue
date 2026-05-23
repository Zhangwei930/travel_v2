<template>
  <view class="page">
    <!-- ══ HEADER 深墨青渐变 ══════════════════════════════════ -->
    <view class="header" :style="{ paddingTop: statusBarHeight + 'px' }">
      <!-- 顶行：城市 + 天气胶囊 -->
      <view class="header-top">
        <view class="city-btn" @tap="onCityTap">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none">
            <path d="M12 22s-8-7-8-13a8 8 0 1116 0c0 6-8 13-8 13z" stroke="#fff" stroke-width="2"/>
            <circle cx="12" cy="9" r="3" stroke="#fff" stroke-width="2"/>
          </svg>
          <text class="city-name">{{ city }}</text>
          <svg xmlns="http://www.w3.org/2000/svg" width="9" height="9" viewBox="0 0 9 9">
            <path d="M1 2.5l3.5 4 3.5-4" stroke="#fff" stroke-width="1.8" fill="none" stroke-linecap="round"/>
          </svg>
        </view>
        <view v-if="weather" class="weather-pill">
          <text class="weather-icon">{{ weather.icon }}</text>
          <text class="weather-text">{{ weather.temp }}° {{ weather.cond }}</text>
        </view>
      </view>

      <!-- ISSUE 标注 -->
      <text class="issue-label mono">ISSUE NO.05 · LOCAL FIELD GUIDE</text>

      <!-- 大标题 -->
      <text class="main-title serif">今天想去哪玩？</text>
      <text class="main-sub">{{ weather?.advice ?? '加载中…' }} · 已为你准备 {{ routes.length }} 条本地路线</text>
    </view>

    <!-- ══ AI 输入卡（悬浮在 header 下方，scroll-view 外）══════ -->
    <view class="ai-card-wrap">
      <view class="ai-card" @tap="goGenerate">
        <view class="ai-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 26 26" fill="none">
            <path d="M3 13l8 4 4 8 7-19-19 7z" fill="#fff"/>
          </svg>
        </view>
        <view class="ai-content">
          <text class="ai-title serif">告诉我你的想法 · AI 帮你规划</text>
          <text class="ai-hint">例如：周末想去钓鱼，自驾 2 小时内</text>
        </view>
        <view class="ai-btn">
          <text class="ai-btn-text">开始</text>
        </view>
      </view>
    </view>

    <!-- 滚动区域（Tab Bar 高度留白） -->
    <scroll-view
      scroll-y
      class="scroll-body"
      :style="{ paddingBottom: tabBarHeight }"
      :show-scrollbar="false"
    >
      <!-- ══ §01 按场景索引（9 宫格）═══════════════════════════ -->
      <view class="section">
        <z-section-header
          no="01"
          title="按场景索引"
          sub="9 类常见出游场景"
        />
        <view v-if="!scenes.length" class="list-empty mono">加载中…</view>
        <view class="scenes-grid">
          <view
            v-for="scene in scenes"
            :key="scene.id"
            class="scene-card"
            @tap="goScene(scene.id)"
          >
            <!-- 右上角编号 -->
            <text class="scene-no mono">{{ scene.no }}</text>
            <!-- 图标 -->
            <view
              class="scene-icon-bg"
              :style="{ background: scene.color + '18' }"
            >
              <text class="scene-icon-emoji">{{ scene.icon }}</text>
            </view>
            <!-- 文字 -->
            <view class="scene-info">
              <text class="scene-label serif">{{ scene.label }}</text>
              <text class="scene-desc">{{ scene.desc }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- ══ §02 附近现在适合去 ══════════════════════════════════ -->
      <view class="section">
        <z-section-header
          no="02"
          title="附近现在适合去"
          sub="基于定位 + 天气 + 时段"
          action="换一批"
          @action="refreshNearby"
        />
        <view v-if="!nearbyVisible.length" class="list-empty mono">定位中，加载附近地点…</view>
        <view class="poi-list">
          <view
            v-for="poi in nearbyVisible"
            :key="poi.id"
            class="poi-card"
            @tap="goPoi(poi.id)"
          >
            <!-- 缩略图 -->
            <view class="poi-img-wrap">
              <image :src="poi.img || poiFallbackImg(poi)" class="poi-img" mode="aspectFill" lazy-load @error="onImgError($event, poi)" />
              <view class="poi-dist-badge">
                <text>📍 {{ poi.dist }}</text>
              </view>
            </view>
            <!-- 内容 -->
            <view class="poi-content">
              <view class="poi-header-row">
                <view>
                  <text class="poi-no mono">{{ poi.no }}</text>
                  <text class="poi-name serif">{{ poi.name }}</text>
                </view>
                <text class="poi-time">🕐 {{ poi.time }}</text>
              </view>
              <text class="poi-cat">{{ poi.cat }}</text>
              <text class="poi-reason" :numberOfLines="1">💡 {{ poi.reason }}</text>
              <view class="poi-tags">
                <z-tag
                  v-for="tag in poi.tags.slice(0, 3)"
                  :key="tag"
                  :label="tag"
                  color="#0D4F4A"
                  :small="true"
                />
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- ══ §03 精选路线（横滑）════════════════════════════════ -->
      <view class="section">
        <z-section-header
          no="03"
          title="精选路线"
          sub="人工策划 · 已审核"
          action="全部"
        />
        <view v-if="!routes.length" class="list-empty mono">加载中…</view>
        <scroll-view scroll-x class="routes-scroll" :show-scrollbar="false">
          <view class="routes-row">
            <view
              v-for="route in routes"
              :key="route.id"
              class="route-card"
              @tap="goResult(route)"
            >
              <!-- 封面 -->
              <view class="route-cover">
                <image :src="route.img || `https://picsum.photos/seed/zr${route.id}/500/300`" class="route-img" mode="aspectFill" lazy-load @error="route.img = `https://picsum.photos/seed/zr${route.id}/500/300`" />
                <!-- R-01 编号 -->
                <view class="route-no-badge" :style="{ color: route.color }">
                  <text class="mono">{{ route.no }}</text>
                </view>
                <!-- 标题叠加 -->
                <view class="route-cover-title">
                  <text class="serif">{{ route.title }}</text>
                </view>
              </view>
              <!-- 卡片内容 -->
              <view class="route-body">
                <text class="route-summary" :numberOfLines="2">{{ route.summary }}</text>
                <view class="route-meta">
                  <text class="route-meta-text">🕐 {{ route.duration }} · 💰 {{ route.budget }} · 📍 {{ route.poi }}站</text>
                  <z-tag :label="route.tag" :color="route.color" :small="true" />
                </view>
              </view>
            </view>
          </view>
        </scroll-view>
      </view>

      <!-- ══ 越用越准横幅 ════════════════════════════════════════ -->
      <view class="tip-banner">
        <text class="tip-icon">🌱</text>
        <view class="tip-content">
          <text class="tip-title serif">越用越准</text>
          <text class="tip-sub">你的真实反馈让推荐更懂你</text>
        </view>
      </view>
    </scroll-view>

    <!-- ══ 底部 Tab Bar ════════════════════════════════════════ -->
    <z-tab-bar current="home" />
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '../../api/mock.js'
import { getCity, setCity, setCoords, setPendingScene } from '../../api/storage.js'
import ZSectionHeader from '../../components/ZSectionHeader.vue'
import ZTag from '../../components/ZTag.vue'
import ZTabBar from '../../components/ZTabBar.vue'

const statusBarHeight = ref(44)
const tabBarHeight = ref('80px')

const city    = ref(getCity())
const weather = ref(null)
const scenes  = ref([])
const nearby  = ref([])
const routes  = ref([])

// 每次显示 3 条，换一批轮换
const nearbyPage = ref(0)
const nearbyVisible = computed(() => {
  if (!nearby.value.length) return []
  const start = (nearbyPage.value * 3) % nearby.value.length
  return nearby.value.slice(start, start + 3).concat(
    nearby.value.slice(0, Math.max(0, start + 3 - nearby.value.length))
  ).slice(0, 3)
})

let cachedCoords = {}

async function loadData() {
  try {
    const [w, n, r] = await Promise.all([
      api.getWeather(city.value),
      api.getNearby(cachedCoords.latitude, cachedCoords.longitude),
      api.getRoutes(),
    ])
    weather.value = w
    nearby.value  = n
    routes.value  = r
  } catch (e) {
    uni.showToast({ title: '数据加载失败，请检查网络', icon: 'none' })
  }
}

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

  try {
    cachedCoords = await new Promise((resolve) => {
      uni.getLocation({ type: 'gcj02', success: resolve, fail: () => resolve({}) })
    })
  } catch (_) {}

  if (cachedCoords.latitude && cachedCoords.longitude) {
    setCoords(cachedCoords.latitude, cachedCoords.longitude)
    // 逆地理编码自动识别城市
    try {
      const res = await api.getLocationCity(cachedCoords.latitude, cachedCoords.longitude)
      if (res.city && res.city !== city.value) {
        city.value = res.city
        setCity(res.city)
      }
    } catch (_) {}
  }

  loadData()
})

// 按场景 seed 生成稳定的占位图（picsum.photos 按 id 固定图）
function poiFallbackImg(poi) {
  return `https://picsum.photos/seed/poi${poi.id}/400/300`
}

function onImgError(e, poi) {
  // 图片加载失败时换占位图，避免空白
  poi.img = `https://picsum.photos/seed/poi${poi.id}/400/300`
}

function refreshNearby() {
  if (!nearby.value.length) return
  nearbyPage.value = (nearbyPage.value + 1) % Math.ceil(nearby.value.length / 3)
}

const CITY_LIST = ['乌鲁木齐', '喀什', '伊宁', '库尔勒', '阿克苏', '北京', '上海', '成都', '西安', '深圳']

function onCityTap() {
  uni.showActionSheet({
    itemList: CITY_LIST,
    success: (res) => {
      const selected = CITY_LIST[res.tapIndex]
      if (selected === city.value) return
      city.value = selected
      setCity(selected)
      weather.value = null
      nearby.value  = []
      routes.value  = []
      loadData()
    },
  })
}

function goGenerate() {
  uni.navigateTo({ url: '/pages/generate/generate' })
}

function goScene(sceneId) {
  setPendingScene(sceneId)
  uni.switchTab({ url: '/pages/scenes/scenes' })
}

function goPoi(id) {
  uni.navigateTo({ url: `/pages/poi/detail?id=${id}` })
}

const TAG_SCENE = { '亲子': 'family', '情侣': 'couple', '雨天': 'rainy', '低预算': 'budget', '钓鱼': 'fish', '拍照': 'photo', '夜游': 'night', 'Citywalk': 'walk', '适老': 'old' }

async function goResult(route) {
  uni.showLoading({ title: '生成中…', mask: true })
  try {
    const plan = await api.generateTrip({
      city: city.value, scene: TAG_SCENE[route.tag] || '', preferences: [route.tag],
    })
    uni.setStorageSync('lastPlan', plan)
    uni.hideLoading()
    uni.navigateTo({ url: '/pages/result/result?generated=1' })
  } catch (_) {
    uni.hideLoading()
    uni.switchTab({ url: '/pages/generate/generate' })
  }
}
</script>

<style lang="scss">
@import '../../uni.scss';

.page {
  min-height: 100vh;
  background: $z-bg;
  display: flex;
  flex-direction: column;
}

.list-empty {
  color: $z-muted;
  font-family: $mono;
  font-size: $font-mono;
  padding: 20rpx 0;
  display: block;
}

// ── Header ──────────────────────────────────────────────────
.header {
  background: linear-gradient(180deg, $z-primary 0%, $z-primary 70%, $z-bg 100%);
  padding: 0 32rpx 48rpx;
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 28rpx;
  padding-top: 16rpx;
}

.city-btn {
  display: flex;
  align-items: center;
  gap: 10rpx;
  cursor: pointer;
}

.city-name {
  color: #fff;
  font-size: 28rpx;
  font-weight: 700;
}

.weather-pill {
  display: flex;
  align-items: center;
  gap: 10rpx;
  background: rgba(255, 255, 255, 0.15);
  border-radius: $radius-pill;
  padding: 8rpx 20rpx;
}

.weather-icon { font-size: 26rpx; }

.weather-text {
  color: #fff;
  font-size: 24rpx;
  font-weight: 600;
}

.issue-label {
  display: block;
  font-size: 20rpx;
  color: rgba(255, 255, 255, 0.55);
  letter-spacing: 3rpx;
  margin-bottom: 10rpx;
}

.main-title {
  display: block;
  color: #fff;
  font-size: 48rpx;
  font-weight: 900;
  letter-spacing: 2rpx;
  margin-bottom: 10rpx;
}

.main-sub {
  display: block;
  color: rgba(255, 255, 255, 0.65);
  font-size: 24rpx;
}

// ── AI 卡（header 外，flex 流中）────────────────────────────
.ai-card-wrap {
  margin: -36rpx 28rpx 8rpx;
  position: relative;
  z-index: 3;
  flex-shrink: 0;
}

// ── 滚动区 ──────────────────────────────────────────────────
.scroll-body {
  flex: 1;
}

.ai-card {
  background: $z-card;
  border-radius: 28rpx;
  padding: 24rpx 28rpx;
  box-shadow: 0 16rpx 48rpx rgba(13, 79, 74, 0.12);
  display: flex;
  align-items: center;
  gap: 20rpx;
  cursor: pointer;
}

.ai-icon {
  width: 68rpx;
  height: 68rpx;
  border-radius: 34rpx;
  background: linear-gradient(135deg, #FF6B35 0%, #FF9558 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.ai-content {
  flex: 1;
  min-width: 0;
}

.ai-title {
  display: block;
  font-size: 27rpx;
  font-weight: 700;
  color: $z-text;
  margin-bottom: 4rpx;
}

.ai-hint {
  display: block;
  font-size: 21rpx;
  color: $z-muted;
}

.ai-btn {
  background: $z-primary;
  border-radius: 18rpx;
  padding: 10rpx 18rpx;
  flex-shrink: 0;
}

.ai-btn-text {
  color: #fff;
  font-size: 23rpx;
  font-weight: 700;
}

// ── 通用 Section 间距 ────────────────────────────────────────
.section {
  padding: 36rpx 32rpx 0;
}

// ── §01 场景宫格 ─────────────────────────────────────────────
.scenes-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16rpx;
}

.scene-card {
  background: $z-card;
  border-radius: 22rpx;
  padding: 24rpx 18rpx;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 14rpx;
  cursor: pointer;
  box-shadow: 0 2rpx 8rpx rgba(13, 79, 74, 0.05);
  position: relative;
}

.scene-no {
  position: absolute;
  top: 14rpx;
  right: 18rpx;
  font-size: 18rpx;
  color: $z-muted;
  letter-spacing: 1rpx;
  font-weight: 700;
}

.scene-icon-bg {
  width: 68rpx;
  height: 68rpx;
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.scene-icon-emoji {
  font-size: 36rpx;
}

.scene-info {
  width: 100%;
}

.scene-label {
  display: block;
  font-size: 25rpx;
  font-weight: 700;
  color: $z-text;
  line-height: 1.2;
  margin-bottom: 4rpx;
}

.scene-desc {
  display: block;
  font-size: 19rpx;
  color: $z-muted;
}

// ── §02 POI 卡片 ─────────────────────────────────────────────
.poi-list {
  display: flex;
  flex-direction: column;
  gap: 18rpx;
}

.poi-card {
  background: $z-card;
  border-radius: 26rpx;
  padding: 22rpx;
  box-shadow: 0 2rpx 12rpx rgba(13, 79, 74, 0.06);
  display: flex;
  gap: 22rpx;
  cursor: pointer;
}

.poi-img-wrap {
  width: 160rpx;
  height: 160rpx;
  border-radius: 20rpx;
  overflow: hidden;
  flex-shrink: 0;
  position: relative;
}

.poi-img {
  width: 100%;
  height: 100%;
}

.poi-dist-badge {
  position: absolute;
  bottom: 8rpx;
  left: 8rpx;
  background: rgba(0, 0, 0, 0.55);
  color: #fff;
  font-size: 18rpx;
  padding: 3rpx 10rpx;
  border-radius: $radius-pill;
}

.poi-content {
  flex: 1;
  min-width: 0;
}

.poi-header-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12rpx;
  margin-bottom: 6rpx;
}

.poi-no {
  display: block;
  font-size: 19rpx;
  color: $z-muted;
  letter-spacing: 1rpx;
  margin-bottom: 4rpx;
}

.poi-name {
  display: block;
  font-size: 29rpx;
  font-weight: 800;
  color: $z-text;
  line-height: 1.2;
}

.poi-time {
  font-size: 20rpx;
  color: $z-muted;
  white-space: nowrap;
  margin-top: 4rpx;
}

.poi-cat {
  display: block;
  font-size: 21rpx;
  color: $z-muted;
  margin-bottom: 10rpx;
}

.poi-reason {
  display: block;
  font-size: 23rpx;
  color: $z-text2;
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 12rpx;
}

.poi-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8rpx;
}

// ── §03 路线横滑 ─────────────────────────────────────────────
.routes-scroll {
  width: 100%;
}

.routes-row {
  display: flex;
  gap: 20rpx;
  padding-bottom: 8rpx;
  white-space: nowrap;
}

.route-card {
  min-width: 440rpx;
  flex-shrink: 0;
  background: $z-card;
  border-radius: 26rpx;
  overflow: hidden;
  box-shadow: 0 2rpx 12rpx rgba(13, 79, 74, 0.06);
  cursor: pointer;
  display: inline-block;
  white-space: normal;
}

.route-cover {
  height: 200rpx;
  position: relative;
  overflow: hidden;
}

.route-img {
  width: 100%;
  height: 100%;
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
}

.route-cover-title {
  position: absolute;
  bottom: 16rpx;
  left: 22rpx;
  color: #fff;
  font-size: 28rpx;
  font-weight: 800;
  text-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.5);
}

.route-body {
  padding: 18rpx 22rpx;
}

.route-summary {
  display: block;
  font-size: 22rpx;
  color: $z-muted;
  line-height: 1.5;
  margin-bottom: 12rpx;
  // 2 行截断（H5/WXML 均支持）
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.route-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.route-meta-text {
  font-size: 20rpx;
  color: $z-muted;
}

// ── 越用越准横幅 ─────────────────────────────────────────────
.tip-banner {
  margin: 28rpx 32rpx 0;
  background: linear-gradient(135deg, rgba(244, 185, 66, 0.13) 0%, rgba(255, 107, 53, 0.07) 100%);
  border: 1rpx solid rgba(244, 185, 66, 0.27);
  border-radius: 26rpx;
  padding: 24rpx 28rpx;
  display: flex;
  align-items: center;
  gap: 22rpx;
}

.tip-icon {
  font-size: 44rpx;
}

.tip-content {
  flex: 1;
}

.tip-title {
  display: block;
  font-size: 26rpx;
  font-weight: 800;
  color: $z-text;
  margin-bottom: 4rpx;
}

.tip-sub {
  display: block;
  font-size: 22rpx;
  color: $z-muted;
}
</style>
