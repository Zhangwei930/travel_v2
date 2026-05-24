<template>
  <view class="launch-page" :style="{ paddingTop: statusBarHeight + 'px' }">
    <view class="launch-bg" />

    <view class="launch-skyline mono">{{ skylineMono }}</view>

    <view class="launch-mascot-wrap">
      <view class="launch-mascot">🤖</view>
      <view class="launch-mascot-shadow" />
    </view>

    <text class="launch-brand serif">出游助手</text>
    <text class="launch-slogan">定位 · 推荐 · 路线 · 一键导航</text>

    <view class="launch-loading-row">
      <view class="loading-dot dot-a" />
      <view class="loading-dot dot-b" />
      <view class="loading-dot dot-c" />
    </view>
    <text class="launch-status mono">{{ statusText }}</text>

    <view class="launch-features">
      <text class="feature-item">· 打开就推荐</text>
      <text class="feature-item">· 路线即用</text>
      <text class="feature-item">· 知识库越用越准</text>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { useCityStore } from '../../store/city.js'

const cityStore = useCityStore()
const statusBarHeight = ref(44)
const statusText = ref('BOOTING · 0.0')
const skylineMono = '▂▃▅█ ▆▂▅█▃ ▅█▂▆ ▃▅█▂'

try {
  const sys = uni.getSystemInfoSync()
  statusBarHeight.value = sys.statusBarHeight || 44
} catch (_) {}

function gotoHome() {
  uni.reLaunch({ url: '/pages/index/index' })
}

function gotoLocation() {
  uni.reLaunch({ url: '/pages/location/index' })
}

async function bootstrap() {
  await new Promise(r => setTimeout(r, 500))
  statusText.value = 'LOCATING · 1.0'

  // 已经缓存了坐标 — 直接进首页（首页内部也会刷新一次定位）
  if (cityStore.coords?.lat != null) {
    gotoHome()
    return
  }

  uni.getLocation({
    type: 'gcj02',
    success: (r) => {
      cityStore.setCoords(r.latitude, r.longitude)
      cityStore.locationDenied = false
      gotoHome()
    },
    fail: () => {
      cityStore.locationDenied = true
      gotoLocation()
    },
  })
}

onLoad(() => {
  bootstrap()
})
</script>

<style lang="scss">
@import '../../uni.scss';

.launch-page {
  min-height: 100vh;
  background: linear-gradient(180deg, $z-primary 0%, #1A6A65 60%, #0D4F4A 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 48rpx 60rpx;
  position: relative;
  overflow: hidden;
}

.launch-bg {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 50% 28%, rgba(255, 255, 255, 0.08) 0%, transparent 60%);
  pointer-events: none;
}

.launch-skyline {
  margin-top: 80rpx;
  color: rgba(255, 255, 255, 0.18);
  font-size: 28rpx;
  letter-spacing: 4rpx;
  text-align: center;
  line-height: 1;
}

.launch-mascot-wrap {
  margin-top: 120rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 1;
}

.launch-mascot {
  font-size: 140rpx;
  line-height: 1;
  filter: drop-shadow(0 8rpx 24rpx rgba(0, 0, 0, 0.25));
}

.launch-mascot-shadow {
  margin-top: 12rpx;
  width: 120rpx;
  height: 12rpx;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.25);
  filter: blur(6rpx);
}

.launch-brand {
  margin-top: 60rpx;
  color: $z-card;
  font-size: 60rpx;
  font-weight: 900;
  letter-spacing: 4rpx;
  z-index: 1;
}

.launch-slogan {
  margin-top: 16rpx;
  color: rgba(255, 255, 255, 0.78);
  font-size: 24rpx;
  letter-spacing: 1rpx;
  z-index: 1;
}

.launch-loading-row {
  margin-top: 80rpx;
  display: flex;
  gap: 14rpx;
  align-items: center;
  z-index: 1;
}

.loading-dot {
  width: 14rpx;
  height: 14rpx;
  border-radius: 7rpx;
  background: $z-card;
  opacity: 0.4;
  animation: dot-pulse 1.2s infinite ease-in-out;
}

.dot-b { animation-delay: 0.15s; }
.dot-c { animation-delay: 0.3s; }

@keyframes dot-pulse {
  0%, 80%, 100% { opacity: 0.4; transform: scale(0.9); }
  40% { opacity: 1; transform: scale(1.2); }
}

.launch-status {
  margin-top: 18rpx;
  color: rgba(255, 255, 255, 0.55);
  font-size: 20rpx;
  letter-spacing: 2rpx;
  z-index: 1;
}

.launch-features {
  margin-top: auto;
  padding-top: 60rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
  z-index: 1;
}

.feature-item {
  display: block;
  color: rgba(255, 255, 255, 0.6);
  font-size: 22rpx;
  letter-spacing: 1rpx;
}
</style>
