<template>
  <view class="page">
    <u-nav-bar title="按场所索引" />

    <text class="page-subtitle">选择您感兴趣的类型</text>

    <scroll-view
      scroll-y
      class="scroll-body"
      :style="{ paddingBottom: tabBarHeight }"
      :show-scrollbar="false"
    >
      <view v-if="!scenes.length" class="hint">场景加载中…</view>
      <view class="scenes-grid">
        <view
          v-for="s in scenes"
          :key="s.id"
          class="scene-card"
          :class="tintClass(s.id)"
          @tap="goScene(s)"
        >
          <view class="scene-icon-wrap">
            <text class="scene-icon" :style="{ color: iconColor(s.id) }">{{ iconChar(s.id) }}</text>
          </view>
          <text class="scene-label">{{ s.label }}</text>
          <text class="scene-desc">{{ s.desc }}</text>
        </view>
      </view>
    </scroll-view>

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
import UNavBar from '../../components/UNavBar.vue'

const cityStore = useCityStore()
const tabBarHeight = ref('80px')
const scenes = ref([])

const TINTS = {
  family: 'tint-mint',
  couple: 'tint-pink',
  rainy:  'tint-blue',
  budget: 'tint-peach',
  fish:   'tint-leaf',
  photo:  'tint-rose',
  night:  'tint-lilac',
  walk:   'tint-mint',
  old:    'tint-sun',
}

const ICON_COLORS = {
  family: '#2D9D6E',
  couple: '#E83E8C',
  rainy:  '#4F6FE0',
  budget: '#E07A2D',
  fish:   '#3E8C3A',
  photo:  '#D63384',
  night:  '#7C3AED',
  walk:   '#2D9D6E',
  old:    '#D97706',
}

// 用 emoji 太花，统一用更"教科书"的简笔 unicode 字符给图标位置；
// 真正小程序里建议替换成 SVG icon set
const ICONS = {
  family: '👨‍👩‍👧',
  couple: '💖',
  rainy:  '☂️',
  budget: '🪙',
  fish:   '🎣',
  photo:  '📸',
  night:  '🌙',
  walk:   '📍',
  old:    '🧓',
}

function tintClass(id) { return TINTS[id] || 'tint-mint' }
function iconColor(id) { return ICON_COLORS[id] || '#1A7A73' }
function iconChar(id)  { return ICONS[id] || '•' }

function navigateToResult(sceneId) {
  if (!sceneId) return
  uni.navigateTo({ url: `/pages/scenes/result?scene=${encodeURIComponent(sceneId)}` })
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
    const tabH = (sys.safeAreaInsets?.bottom || 18) + 56
    tabBarHeight.value = tabH + 'px'
  } catch (_) {}

  try {
    scenes.value = await api.getScenes()
  } catch (_) {
    uni.showToast({ title: '场景加载失败', icon: 'none' })
  }

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

.page {
  min-height: 100vh;
  background: $u-bg;
}

.page-subtitle {
  display: block;
  text-align: center;
  font-size: 22rpx;
  color: $u-text-mute;
  padding: 6rpx 0 18rpx;
}

.scroll-body {
  position: relative;
}

.hint {
  text-align: center;
  color: $u-text-mute;
  font-size: 24rpx;
  padding: 40rpx 0;
}

// ── 2×N 场景网格 ───────────────────────────────────────────
.scenes-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16rpx;
  padding: 0 24rpx 32rpx;
}

.scene-card {
  border-radius: 22rpx;
  padding: 28rpx 24rpx 26rpx;
  min-height: 200rpx;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 14rpx;
  cursor: pointer;

  &.tint-mint  { background: $u-tint-mint; }
  &.tint-pink  { background: $u-tint-pink; }
  &.tint-blue  { background: $u-tint-blue; }
  &.tint-peach { background: $u-tint-peach; }
  &.tint-lilac { background: $u-tint-lilac; }
  &.tint-rose  { background: $u-tint-rose; }
  &.tint-leaf  { background: $u-tint-leaf; }
  &.tint-sun   { background: $u-tint-sun; }
}

.scene-icon-wrap {
  width: 80rpx;
  height: 80rpx;
  border-radius: 40rpx;
  background: rgba(255, 255, 255, 0.65);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8rpx;
}

.scene-icon {
  font-size: 42rpx;
  line-height: 1;
}

.scene-label {
  display: block;
  font-size: 30rpx;
  font-weight: 800;
  color: $u-text;
  line-height: 1.15;
}

.scene-desc {
  display: block;
  font-size: 22rpx;
  color: $u-text-sub;
  line-height: 1.3;
}
</style>
