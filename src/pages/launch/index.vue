<template>
  <view class="launch-page">
    <!-- 主内容 -->
    <view class="launch-body">
      <!-- 标题区 -->
      <view class="title-area">
        <text class="main-title">出游助手</text>
        <text class="sub-title">发现身边好去处</text>
      </view>

      <!-- 插画区 -->
      <view class="illustration-area">
        <svg class="illus-svg" viewBox="0 0 340 260" xmlns="http://www.w3.org/2000/svg">
          <!-- 天空 -->
          <rect x="0" y="0" width="340" height="260" fill="#F0FAF7" rx="24"/>
          <!-- 远山 -->
          <ellipse cx="170" cy="200" rx="200" ry="60" fill="#C8EAE0"/>
          <!-- 大树 左 -->
          <ellipse cx="70" cy="155" rx="38" ry="42" fill="#2A8278"/>
          <rect x="62" y="185" width="16" height="40" fill="#1A6056" rx="4"/>
          <!-- 大树 右 -->
          <ellipse cx="265" cy="150" rx="42" ry="46" fill="#1A7A73"/>
          <rect x="257" y="182" width="16" height="44" fill="#156058" rx="4"/>
          <!-- 小树 中左 -->
          <ellipse cx="120" cy="170" rx="24" ry="28" fill="#4FD1C5"/>
          <rect x="113" y="192" width="12" height="28" fill="#2A8278" rx="3"/>
          <!-- 小树 中右 -->
          <ellipse cx="218" cy="168" rx="22" ry="26" fill="#38B2AC"/>
          <rect x="211" y="188" width="12" height="26" fill="#2A8278" rx="3"/>
          <!-- 小路 -->
          <path d="M150 260 Q170 200 190 260" fill="#D4EDE8"/>
          <path d="M145 260 Q170 195 195 260" fill="none" stroke="#B2D8D0" stroke-width="1" stroke-dasharray="6,4"/>
          <!-- 草地 -->
          <ellipse cx="170" cy="230" rx="130" ry="32" fill="#4FD1C5" opacity="0.35"/>
          <!-- 装饰点 -->
          <circle cx="95" cy="210" r="5" fill="#38B2AC" opacity="0.5"/>
          <circle cx="240" cy="215" r="4" fill="#2A8278" opacity="0.4"/>
          <circle cx="170" cy="100" r="6" fill="#B2EBF4" opacity="0.7"/>
          <circle cx="130" cy="80" r="4" fill="#C8EAE0" opacity="0.8"/>
          <circle cx="210" cy="75" r="5" fill="#B2EBF4" opacity="0.6"/>
          <!-- 路径圆点 -->
          <circle cx="160" cy="230" r="4" fill="#0D4F4A" opacity="0.3"/>
          <circle cx="170" cy="215" r="4" fill="#0D4F4A" opacity="0.3"/>
          <circle cx="180" cy="228" r="4" fill="#0D4F4A" opacity="0.3"/>
        </svg>

        <!-- 机器人遮挡在插画下方 -->
        <view class="mascot-wrap">
          <view class="mascot-glow" />
          <view class="mascot-body">
            <view class="mascot-head">
              <view class="mascot-eye left" />
              <view class="mascot-eye right" />
            </view>
            <view class="mascot-torso">
              <view class="mascot-dot" />
              <view class="mascot-dot" />
              <view class="mascot-dot" />
            </view>
            <view class="mascot-antenna" />
          </view>
        </view>
      </view>

      <!-- 加载文字 -->
      <view class="loading-row">
        <text class="loading-text">{{ statusText }}</text>
        <view class="loading-dots">
          <view class="ldot ldot-1" />
          <view class="ldot ldot-2" />
          <view class="ldot ldot-3" />
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useCityStore } from '../../store/city.js'

const cityStore = useCityStore()
const statusText = ref('正在为你准备附近好去处')

onMounted(() => bootstrap())

function gotoHome() {
  uni.reLaunch({ url: '/pages/index/index' })
}

function gotoLocation() {
  uni.reLaunch({ url: '/pages/location/index' })
}

async function bootstrap() {
  await new Promise(r => setTimeout(r, 400))

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
      // 跳转定位页，不静默回落成都
      gotoLocation()
    },
  })
}
</script>

<style lang="scss">
@import '../../uni.scss';

.launch-page {
  min-height: 100vh;
  background: #FFFFFF;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.launch-body {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 100rpx;
}

// ── 标题 ─────────────────────────────────────────────────────
.title-area {
  text-align: center;
  margin-bottom: 48rpx;
}

.main-title {
  display: block;
  font-size: 64rpx;
  font-weight: 900;
  color: $u-text;
  letter-spacing: 4rpx;
  margin-bottom: 12rpx;
}

.sub-title {
  display: block;
  font-size: 28rpx;
  color: $u-text-mute;
}

// ── 插画区 ──────────────────────────────────────────────────
.illustration-area {
  position: relative;
  width: 680rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.illus-svg {
  width: 680rpx;
  height: 520rpx;
}

// ── 机器人 ──────────────────────────────────────────────────
.mascot-wrap {
  position: absolute;
  bottom: -40rpx;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.mascot-glow {
  position: absolute;
  bottom: -10rpx;
  width: 140rpx;
  height: 40rpx;
  background: rgba(13, 79, 74, 0.12);
  border-radius: 50%;
  filter: blur(8rpx);
}

.mascot-body {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4rpx;
}

.mascot-antenna {
  width: 8rpx;
  height: 28rpx;
  background: $z-primary;
  border-radius: 4rpx;
  position: absolute;
  top: -30rpx;

  &::after {
    content: '';
    display: block;
    width: 16rpx;
    height: 16rpx;
    background: $z-primary;
    border-radius: 50%;
    position: absolute;
    top: -12rpx;
    left: -4rpx;
  }
}

.mascot-head {
  width: 100rpx;
  height: 90rpx;
  background: $z-primary;
  border-radius: 24rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 18rpx;
}

.mascot-eye {
  width: 22rpx;
  height: 22rpx;
  background: #FFFFFF;
  border-radius: 50%;

  &::after {
    content: '';
    display: block;
    width: 10rpx;
    height: 10rpx;
    background: $z-primary;
    border-radius: 50%;
    margin: 6rpx auto;
  }
}

.mascot-torso {
  width: 100rpx;
  height: 72rpx;
  background: $z-primary-m;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
}

.mascot-dot {
  width: 14rpx;
  height: 14rpx;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 50%;
}

// ── 加载文字 ────────────────────────────────────────────────
.loading-row {
  margin-top: 80rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 18rpx;
}

.loading-text {
  font-size: 26rpx;
  color: $u-text-sub;
}

.loading-dots {
  display: flex;
  gap: 12rpx;
}

.ldot {
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
  background: $z-primary;
  opacity: 0.25;
  animation: dotPulse 1.4s infinite ease-in-out;
}
.ldot-2 { animation-delay: 0.2s; }
.ldot-3 { animation-delay: 0.4s; }

@keyframes dotPulse {
  0%, 80%, 100% { transform: scale(0.8); opacity: 0.25; }
  40%           { transform: scale(1.2); opacity: 1; }
}
</style>
