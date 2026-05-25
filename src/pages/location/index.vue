<template>
  <view class="page">
    <u-nav-bar title="出游助手" right-icon="search" />

    <view class="loc-body">
      <!-- 同心圆动画 + 定位图标 -->
      <view class="rings-wrap">
        <view class="ring ring-3" />
        <view class="ring ring-2" />
        <view class="ring ring-1" />
        <view class="pin-center">
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none">
            <path d="M12 22s-8-7-8-13a8 8 0 1116 0c0 6-8 13-8 13z" fill="#0D4F4A"/>
            <circle cx="12" cy="9" r="3" fill="#FFFFFF"/>
          </svg>
        </view>
      </view>

      <!-- 状态文字 -->
      <view class="status-area">
        <text class="status-title">{{ pending ? '正在定位中...' : '定位服务未开启' }}</text>
        <text class="status-sub">{{ pending ? '请允许获取位置权限' : '请在设置中开启位置权限' }}</text>
      </view>

      <!-- 定位提示卡 -->
      <view class="hint-card">
        <view class="hint-header">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none">
            <path d="M12 22s-8-7-8-13a8 8 0 1116 0c0 6-8 13-8 13z" fill="#0D4F4A"/>
            <circle cx="12" cy="9" r="3" fill="#FFFFFF"/>
          </svg>
          <text class="hint-title">定位提示</text>
        </view>
        <view class="hint-items">
          <view class="hint-item" v-for="t in tips" :key="t">
            <view class="hint-dot" />
            <text class="hint-text">{{ t }}</text>
          </view>
        </view>
      </view>

      <!-- 操作按钮（非首次状态才显示） -->
      <view v-if="!pending && showActions" class="actions" :style="{ paddingBottom: safeBottom }">
        <view class="btn-primary" @tap="retry">重新尝试定位</view>
        <view class="btn-secondary" @tap="useDefault">使用默认城市进入</view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useCityStore } from '../../store/city.js'
import { api } from '../../api/mock.js'
import UNavBar from '../../components/UNavBar.vue'

const cityStore = useCityStore()
const pending = ref(true)
const showActions = ref(false)
const safeBottom = ref('40rpx')

const tips = [
  '开启定位权限',
  '可获取更准确的出游推荐',
  '保护您的位置信息安全',
]

onMounted(() => {
  try {
    const sys = uni.getSystemInfoSync()
    safeBottom.value = Math.max(sys.safeAreaInsets?.bottom || 20, 20) + 'px'
  } catch (_) {}
  doLocate()
})

function gotoHome() {
  uni.reLaunch({ url: '/pages/index/index' })
}

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

function retry() {
  doLocate()
}

function useDefault() {
  cityStore.setDefaultLocation()
  gotoHome()
}
</script>

<style lang="scss">
@import '../../uni.scss';

.page {
  min-height: 100vh;
  background: #FFFFFF;
  display: flex;
  flex-direction: column;
}

.loc-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60rpx 48rpx 0;
}

// ── 同心圆 ───────────────────────────────────────────────────
.rings-wrap {
  position: relative;
  width: 280rpx;
  height: 280rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 48rpx;
}

.ring {
  position: absolute;
  border-radius: 50%;
  border: 2rpx solid rgba(13, 79, 74, 0.15);
  animation: ringPulse 2.4s infinite ease-out;
}
.ring-1 { width: 100rpx; height: 100rpx; animation-delay: 0s; }
.ring-2 { width: 180rpx; height: 180rpx; animation-delay: 0.6s; }
.ring-3 { width: 260rpx; height: 260rpx; animation-delay: 1.2s; }

@keyframes ringPulse {
  0%   { opacity: 0.8; transform: scale(0.92); }
  60%  { opacity: 0.3; }
  100% { opacity: 0;   transform: scale(1.05); }
}

.pin-center {
  position: relative;
  z-index: 2;
  width: 72rpx;
  height: 72rpx;
  background: rgba(13, 79, 74, 0.08);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

// ── 状态文字 ─────────────────────────────────────────────────
.status-area {
  text-align: center;
  margin-bottom: 48rpx;
}

.status-title {
  display: block;
  font-size: 40rpx;
  font-weight: 800;
  color: $u-text;
  margin-bottom: 12rpx;
}

.status-sub {
  display: block;
  font-size: 26rpx;
  color: $u-text-mute;
}

// ── 提示卡 ──────────────────────────────────────────────────
.hint-card {
  width: 100%;
  background: #E8F4F0;
  border-radius: 20rpx;
  padding: 28rpx 32rpx;
}

.hint-header {
  display: flex;
  align-items: center;
  gap: 10rpx;
  margin-bottom: 20rpx;
}

.hint-title {
  font-size: 28rpx;
  font-weight: 700;
  color: $z-primary;
}

.hint-items {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}

.hint-item {
  display: flex;
  align-items: center;
  gap: 14rpx;
}

.hint-dot {
  width: 8rpx;
  height: 8rpx;
  border-radius: 50%;
  background: $z-primary;
  flex-shrink: 0;
}

.hint-text {
  font-size: 26rpx;
  color: $u-text-sub;
}

// ── 操作按钮 ─────────────────────────────────────────────────
.actions {
  width: 100%;
  margin-top: 48rpx;
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.btn-primary {
  height: 96rpx;
  border-radius: 48rpx;
  background: $z-primary;
  color: #FFFFFF;
  font-size: 30rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8rpx 20rpx rgba(13, 79, 74, 0.2);
}

.btn-secondary {
  height: 96rpx;
  border-radius: 48rpx;
  background: $u-bg-soft;
  color: $u-text;
  font-size: 30rpx;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
