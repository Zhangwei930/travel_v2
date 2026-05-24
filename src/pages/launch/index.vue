<template>
  <view class="launch-page">
    <view class="launch-content">
      <view class="mascot-wrap">
        <view class="mascot-circle">
          <text class="mascot-emoji">🤖</text>
        </view>
        <view class="mascot-shadow" />
      </view>

      <view class="brand-wrap">
        <text class="brand-name">出游助手</text>
        <text class="brand-slogan">定位 · 推荐 · 路线 · 一键导航</text>
      </view>

      <view class="loading-wrap">
        <view class="loading-dots">
          <view class="dot" v-for="i in 3" :key="i" :class="'dot-' + i" />
        </view>
        <text class="status-text">{{ statusText }}</text>
      </view>
    </view>

    <view class="launch-footer" :style="{ paddingBottom: safeBottom }">
      <text class="footer-copy">© 2024 ZHOUMI TRAVEL</text>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useCityStore } from '../../store/city.js'

const cityStore = useCityStore()
const statusText = ref('INITIALIZING...')
const safeBottom = ref('40rpx')

onMounted(() => {
  try {
    const sys = uni.getSystemInfoSync()
    safeBottom.value = Math.max(sys.safeAreaInsets?.bottom || 20, 20) + 'px'
  } catch (_) {}
  bootstrap()
})

function gotoHome() {
  uni.reLaunch({ url: '/pages/index/index' })
}

async function bootstrap() {
  await new Promise(r => setTimeout(r, 600))
  statusText.value = 'LOCATING...'

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
    fail: (err) => {
      console.warn('launch getLocation fail:', err)
      cityStore.setDefaultLocation()
      gotoHome()
    },
  })
}
</script>

<style lang="scss">
@import '../../uni.scss';

.launch-page {
  min-height: 100vh;
  background: #fff;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.launch-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding-bottom: 100rpx;
}

.mascot-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 60rpx;
}

.mascot-circle {
  width: 180rpx;
  height: 180rpx;
  background: $u-bg-soft;
  border-radius: 90rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: $u-shadow;
}

.mascot-emoji {
  font-size: 80rpx;
}

.mascot-shadow {
  margin-top: 20rpx;
  width: 100rpx;
  height: 10rpx;
  background: rgba(0,0,0,0.05);
  border-radius: 50%;
  filter: blur(4rpx);
}

.brand-wrap {
  text-align: center;
  margin-bottom: 120rpx;
}

.brand-name {
  display: block;
  font-size: 52rpx;
  font-weight: 800;
  color: $u-text;
  letter-spacing: 4rpx;
  margin-bottom: 12rpx;
}

.brand-slogan {
  display: block;
  font-size: 24rpx;
  color: $u-text-mute;
  letter-spacing: 2rpx;
}

.loading-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16rpx;
}

.loading-dots {
  display: flex;
  gap: 12rpx;
}

.dot {
  width: 12rpx;
  height: 12rpx;
  border-radius: 6rpx;
  background: $z-primary;
  opacity: 0.3;
  animation: dotPulse 1.2s infinite ease-in-out;
}

.dot-2 { animation-delay: 0.2s; }
.dot-3 { animation-delay: 0.4s; }

@keyframes dotPulse {
  0%, 80%, 100% { transform: scale(0.8); opacity: 0.3; }
  40% { transform: scale(1.2); opacity: 1; }
}

.status-text {
  font-size: 18rpx;
  color: $u-text-mute;
  letter-spacing: 2rpx;
  font-family: $mono;}

.launch-footer {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  text-align: center;
  padding: 40rpx;
}

.footer-copy {
  font-size: 18rpx;
  color: $u-text-mute;
  letter-spacing: 2rpx;
  font-family: $mono;}
</style>
