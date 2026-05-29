<template>
  <view class="cy-page">
    <cy-nav-bar title="出游助手" right-icon="search" :show-back="false" />

    <view class="cy-loc-body">
      <!-- 雷达动画 -->
      <view class="cy-rings-wrap">
        <view class="cy-ring cy-ring-3" />
        <view class="cy-ring cy-ring-2" />
        <view class="cy-ring cy-ring-1" />
        <!-- 信号点 -->
        <view class="cy-signal-dot" style="top: 30rpx; left: 50rpx;" />
        <view class="cy-signal-dot" style="top: 60rpx; right: 40rpx;" />
        <view class="cy-signal-dot" style="bottom: 50rpx; left: 60rpx;" />
        <view class="cy-signal-dot" style="bottom: 40rpx; right: 50rpx;" />
        <view class="cy-pin-center">
          <CyIcon name="pin-white-center" :size="72" />
        </view>
      </view>

      <!-- 状态文字 -->
      <text class="cy-status-title">{{ pending ? '正在定位中...' : '定位服务未开启' }}</text>
      <text class="cy-status-sub">{{ pending ? '请允许获取位置权限' : '请在设置中开启位置权限' }}</text>

      <!-- 提示卡 -->
      <view class="cy-hint-card">
        <view class="cy-hint-header">
          <view class="cy-hint-icon">
            <CyIcon name="lightbulb-green" :size="36" />
          </view>
          <text class="cy-hint-title">定位提示</text>
        </view>
        <view class="cy-hint-items">
          <view class="cy-hint-item" v-for="t in tips" :key="t">
            <view class="cy-hint-dot" />
            <text class="cy-hint-text">{{ t }}</text>
          </view>
        </view>
      </view>

      <!-- 操作按钮 -->
      <view v-if="!pending && showActions" class="cy-actions" :style="{ paddingBottom: safeBottom }">
        <view class="cy-btn-primary" @tap="retry">重新尝试定位</view>
        <view class="cy-btn-secondary" @tap="useDefault">使用默认城市进入</view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useCityStore } from '../../store/city.js'
import { api } from '../../api/index.js'
import CyNavBar from '../../components/cy/cy-nav-bar.vue'
import CyIcon from '../../components/cy/cy-icon.vue'

const cityStore = useCityStore()
const pending = ref(true)
const showActions = ref(false)
const safeBottom = ref('40rpx')

const tips = [
  '开启定位权限后系统自动获取您的位置',
  '可获取更准确的附近出游推荐',
  '仅用于本地推荐，保护您的位置安全',
]

onMounted(() => {
  try { safeBottom.value = Math.max(uni.getSystemInfoSync().safeAreaInsets?.bottom || 20, 20) + 'px' } catch (_) {}
  doLocate()
})

function gotoHome() { uni.reLaunch({ url: '/pages/index/index' }) }

async function reverseCity(lat, lng) {
  try {
    const g = await api.geoCity(lat, lng)
    if (g?.city) cityStore.setFromLocation(g.city)
  } catch (_) {}
}

function doLocate() {
  pending.value = true
  showActions.value = false
  uni.getLocation({
    type: 'gcj02',
    success: async (r) => {
      cityStore.setCoords(r.latitude, r.longitude)
      cityStore.locationDenied = false
      await reverseCity(r.latitude, r.longitude)
      pending.value = false
      gotoHome()
    },
    fail: (err) => {
      pending.value = false
      showActions.value = true
      const msg = err?.errMsg || ''
      if (msg.includes('auth deny') || msg.includes('auth denied')) {
        uni.showModal({
          title: '定位权限未开启',
          content: '请前往设置开启位置权限，以获取附近出游推荐。',
          confirmText: '去设置',
          cancelText: '稍后',
          success: (res) => { if (res.confirm) uni.openSetting() },
        })
      }
    },
  })
}

function retry() { doLocate() }
function useDefault() { cityStore.setDefaultLocation(); gotoHome() }
</script>

<style lang="scss">
@import '../../uni.scss';

.cy-page {
  min-height: 100vh;
  background: #fff;
  font-family: "PingFang SC", "HarmonyOS Sans SC", "Noto Sans SC", -apple-system, system-ui, sans-serif;
}

.cy-loc-body {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60rpx 48rpx 0;
}

// ── 雷达 ───────────────────────────────────────────────────
.cy-rings-wrap {
  position: relative;
  width: 560rpx;
  height: 560rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 48rpx;
}

.cy-ring {
  position: absolute;
  border-radius: 50%;
  border: 2rpx dashed $cy-green-line;
  animation: cy-ring-pulse 2.4s infinite ease-out;
}

.cy-ring-1 { width: 160rpx; height: 160rpx; animation-delay: 0s; }
.cy-ring-2 { width: 320rpx; height: 320rpx; animation-delay: 0.6s; }
.cy-ring-3 { width: 480rpx; height: 480rpx; animation-delay: 1.2s; border-style: dashed; }

@keyframes cy-ring-pulse {
  0%   { opacity: 0.8; transform: scale(0.95); }
  60%  { opacity: 0.3; }
  100% { opacity: 0;   transform: scale(1.05); }
}

.cy-signal-dot {
  position: absolute;
  width: 18rpx;
  height: 18rpx;
  border-radius: 9rpx;
  background: $cy-green;
  opacity: 0.7;
  animation: cy-dot-blink 2s infinite ease-in-out;
}

@keyframes cy-dot-blink {
  0%, 100% { opacity: 0.3; } 50% { opacity: 0.9; }
}

.cy-pin-center {
  position: relative;
  z-index: 2;
  width: 100rpx;
  height: 100rpx;
  background: $cy-green-ls;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

// ── 状态文字 ───────────────────────────────────────────────
.cy-status-title {
  display: block;
  font-size: 56rpx;
  font-weight: 800;
  color: $cy-text;
  text-align: center;
  margin-bottom: 12rpx;
}

.cy-status-sub {
  display: block;
  font-size: 28rpx;
  color: $cy-muted;
  text-align: center;
  margin-bottom: 48rpx;
}

// ── 提示卡 ─────────────────────────────────────────────────
.cy-hint-card {
  width: 100%;
  background: $cy-green-ls;
  border-radius: 28rpx;
  padding: 28rpx 32rpx;
}

.cy-hint-header {
  display: flex;
  align-items: center;
  gap: 10rpx;
  margin-bottom: 20rpx;
}

.cy-hint-icon {
  width: 38rpx;
  height: 38rpx;
  border-radius: 19rpx;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
}
.cy-hint-title { font-size: 30rpx; font-weight: 800; color: $cy-green; }

.cy-hint-items { display: flex; flex-direction: column; gap: 14rpx; }
.cy-hint-item  { display: flex; align-items: center; gap: 14rpx; }
.cy-hint-dot   { width: 10rpx; height: 10rpx; border-radius: 5rpx; background: $cy-green; flex-shrink: 0; }
.cy-hint-text  { font-size: 26rpx; color: $cy-text-sub; }

// ── 操作按钮 ───────────────────────────────────────────────
.cy-actions {
  width: 100%;
  margin-top: 48rpx;
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.cy-btn-primary {
  height: 100rpx;
  border-radius: 50rpx;
  background: $cy-green;
  color: #fff;
  font-size: 32rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8rpx 20rpx rgba(26,136,112,0.25);
}

.cy-btn-secondary {
  height: 100rpx;
  border-radius: 50rpx;
  background: $cy-green-ls;
  color: $cy-text;
  font-size: 30rpx;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
