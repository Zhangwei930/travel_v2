<template>
  <view class="page">
    <!-- ══ HEADER ══════════════════════════════════════════════ -->
    <view class="header" :style="{ paddingTop: statusBarHeight + 'px' }">
      <text class="header-mono mono">§ SCENES · INDEX</text>
      <text class="header-title serif">按场所索引</text>
      <text class="header-sub">选一个场景，系统按定位 + 天气推荐路线与地点</text>
    </view>

    <!-- ══ 滚动内容区：3×3 场景网格 ═════════════════════════════ -->
    <scroll-view
      scroll-y
      class="scroll-body"
      :style="{ paddingBottom: tabBarHeight }"
      :show-scrollbar="false"
    >
      <view v-if="!scenes.length" class="list-empty mono">场景列表加载中…</view>
      <view class="scenes-grid">
        <view
          v-for="s in scenes"
          :key="s.id"
          class="scene-card"
          @tap="goScene(s)"
        >
          <text class="scene-no mono">NO.{{ s.no }}</text>
          <view class="scene-icon-bg" :style="{ background: s.color + '22' }">
            <text class="scene-icon">{{ s.icon }}</text>
          </view>
          <text class="scene-label serif">{{ s.label }}</text>
          <text class="scene-desc">{{ s.desc }}</text>
        </view>
      </view>

      <view class="hint-card">
        <text class="hint-title serif">如何选场景？</text>
        <text class="hint-text">每个场景对应一套筛选规则（适合人群、天气、时段、避坑提醒）。系统会基于当前定位推荐 2~3 条已策划的路线和附近 POI。</text>
      </view>
    </scroll-view>

    <!-- ══ 底部 Tab Bar ════════════════════════════════════════ -->
    <z-tab-bar current="scenes" />
  </view>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { api } from '../../api/mock.js'
import { useCityStore } from '../../store/city.js'
import { consumePendingScene } from '../../api/storage.js'
import ZTabBar from '../../components/ZTabBar.vue'

const cityStore = useCityStore()

const statusBarHeight = ref(44)
const tabBarHeight    = ref('80px')
const scenes          = ref([])

function navigateToResult(sceneId) {
  if (!sceneId) return
  uni.navigateTo({
    url: `/pages/scenes/result?scene=${encodeURIComponent(sceneId)}`,
  })
}

function goScene(s) {
  navigateToResult(s.id)
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

  try {
    scenes.value = await api.getScenes()
  } catch (_) {
    uni.showToast({ title: '场景列表加载失败', icon: 'none' })
  }

  // 从首页带入的预选场景，直接打开结果子页
  const pendingScene = consumePendingScene()
  if (pendingScene) navigateToResult(pendingScene)

  uni.$on('switchScene', navigateToResult)
  uni.$on('homeLocationContext', applyHomeLocationContext)
})

onShow(() => {
  const pendingScene = consumePendingScene()
  if (pendingScene) navigateToResult(pendingScene)
})

onUnmounted(() => {
  uni.$off('switchScene', navigateToResult)
  uni.$off('homeLocationContext', applyHomeLocationContext)
})
</script>

<style lang="scss">
@import '../../uni.scss';

.list-empty {
  color: $z-muted;
  font-family: $mono;
  font-size: $font-mono;
  padding: 28rpx 32rpx;
  display: block;
}

.page {
  min-height: 100vh;
  background: $z-bg;
}

.header {
  background: $z-card;
  padding: 0 32rpx 28rpx;
}

.header-mono {
  display: block;
  font-size: 20rpx;
  color: $z-muted;
  letter-spacing: 3rpx;
  padding-top: 16rpx;
  margin-bottom: 8rpx;
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
}

.scroll-body {
  position: relative;
}

// ── 3×3 场景网格 ───────────────────────────────────────────────
.scenes-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18rpx;
  padding: 24rpx 28rpx 8rpx;
}

.scene-card {
  background: $z-card;
  border-radius: 22rpx;
  padding: 22rpx 18rpx 20rpx;
  display: flex;
  flex-direction: column;
  gap: 12rpx;
  cursor: pointer;
  box-shadow: 0 2rpx 10rpx rgba(13, 79, 74, 0.06);
  position: relative;
  min-height: 230rpx;
}

.scene-no {
  position: absolute;
  top: 14rpx;
  right: 18rpx;
  font-size: 18rpx;
  color: $z-muted;
  letter-spacing: 1rpx;
}

.scene-icon-bg {
  width: 72rpx;
  height: 72rpx;
  border-radius: 18rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 8rpx;
}

.scene-icon {
  font-size: 36rpx;
  line-height: 1;
}

.scene-label {
  display: block;
  font-size: 26rpx;
  font-weight: 800;
  color: $z-text;
  line-height: 1.2;
  margin-top: auto;
}

.scene-desc {
  display: block;
  font-size: 20rpx;
  color: $z-muted;
  line-height: 1.3;
}

// ── 底部说明卡 ────────────────────────────────────────────────
.hint-card {
  margin: 28rpx 28rpx 0;
  background: $z-card;
  border-radius: 18rpx;
  padding: 22rpx 26rpx;
  box-shadow: 0 2rpx 10rpx rgba(13, 79, 74, 0.04);
}

.hint-title {
  display: block;
  font-size: 26rpx;
  font-weight: 800;
  color: $z-text;
  margin-bottom: 8rpx;
}

.hint-text {
  display: block;
  font-size: 22rpx;
  color: $z-muted;
  line-height: 1.55;
}
</style>
