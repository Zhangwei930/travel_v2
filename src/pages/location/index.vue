<template>
  <view class="loc-page" :style="{ paddingTop: statusBarHeight + 'px' }">
    <view class="loc-header">
      <text class="loc-kicker mono">§ LOCATION · REQUIRED</text>
      <text class="loc-title serif">{{ pending ? '定位中…' : '正在定位中' }}</text>
      <text class="loc-sub">需要您的位置权限，才能推荐附近真实可去的地点，结合天气和时段给出合理路线。</text>
    </view>

    <view class="loc-card">
      <view class="loc-pin-wrap">
        <view class="loc-pin">
          <svg xmlns="http://www.w3.org/2000/svg" width="56" height="56" viewBox="0 0 24 24" fill="none">
            <path d="M12 22s-8-7-8-13a8 8 0 1116 0c0 6-8 13-8 13z" stroke="#0D4F4A" stroke-width="2"/>
            <circle cx="12" cy="9" r="3" stroke="#0D4F4A" stroke-width="2"/>
          </svg>
        </view>
        <view v-if="pending" class="loc-pin-pulse" />
      </view>

      <view class="loc-detail">
        <text class="loc-detail-title serif">权限用途</text>
        <view class="loc-detail-list">
          <text class="loc-detail-item">· 推荐附近 3~5 公里内的目的地</text>
          <text class="loc-detail-item">· 按当前天气、时段调整推荐</text>
          <text class="loc-detail-item">· 生成可一键导航的可执行路线</text>
          <text class="loc-detail-item">· 位置数据只在本机使用，不会上传明文</text>
        </view>
      </view>
    </view>

    <view class="loc-actions">
      <view class="primary-btn" :class="{ disabled: pending }" @tap="retry">{{ pending ? '正在定位…' : '重新定位' }}</view>
      <view class="secondary-btn" @tap="useDefault">使用默认城市继续</view>
    </view>

    <text class="loc-hint mono">默认城市：{{ cityStore.current }} · 之后可在出游 Tab 点城市重新定位</text>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { useCityStore } from '../../store/city.js'
import { api } from '../../api/mock.js'

const cityStore = useCityStore()
const statusBarHeight = ref(44)
const pending = ref(false)

try {
  const sys = uni.getSystemInfoSync()
  statusBarHeight.value = sys.statusBarHeight || 44
} catch (_) {}

function gotoHome() {
  uni.reLaunch({ url: '/pages/index/index' })
}

async function reverseAndSetCity(lat, lng) {
  try {
    const g = await api.geoCity(lat, lng)
    if (g?.city) cityStore.setFromLocation(g.city)
  } catch (_) {}
}

function retry() {
  if (pending.value) return
  pending.value = true
  uni.getLocation({
    type: 'gcj02',
    success: async (r) => {
      cityStore.setCoords(r.latitude, r.longitude)
      cityStore.locationDenied = false
      await reverseAndSetCity(r.latitude, r.longitude)
      pending.value = false
      gotoHome()
    },
    fail: () => {
      pending.value = false
      uni.showToast({ title: '仍未获取到位置权限', icon: 'none' })
    },
  })
}

function useDefault() {
  cityStore.locationDenied = true
  gotoHome()
}
</script>

<style lang="scss">
@import '../../uni.scss';

.loc-page {
  min-height: 100vh;
  background: $z-bg;
  display: flex;
  flex-direction: column;
  padding: 32rpx 32rpx 60rpx;
}

.loc-header {
  margin-top: 16rpx;
  margin-bottom: 36rpx;
}

.loc-kicker {
  display: block;
  font-size: 20rpx;
  color: $z-muted;
  letter-spacing: 3rpx;
  margin-bottom: 12rpx;
}

.loc-title {
  display: block;
  font-size: 46rpx;
  font-weight: 900;
  color: $z-text;
  margin-bottom: 10rpx;
}

.loc-sub {
  display: block;
  font-size: 24rpx;
  color: $z-muted;
  line-height: 1.55;
  max-width: 600rpx;
}

.loc-card {
  background: $z-card;
  border-radius: 26rpx;
  padding: 36rpx 32rpx;
  box-shadow: 0 8rpx 28rpx rgba(13, 79, 74, 0.08);
  margin-bottom: 36rpx;
}

.loc-pin-wrap {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 140rpx;
  margin-bottom: 28rpx;
}

.loc-pin {
  width: 120rpx;
  height: 120rpx;
  border-radius: 60rpx;
  background: rgba(13, 79, 74, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
}

.loc-pin-pulse {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 120rpx;
  height: 120rpx;
  border-radius: 60rpx;
  background: rgba(13, 79, 74, 0.18);
  animation: pin-ripple 1.4s infinite ease-out;
}

@keyframes pin-ripple {
  0%   { transform: translate(-50%, -50%) scale(1);   opacity: 0.5; }
  100% { transform: translate(-50%, -50%) scale(1.8); opacity: 0; }
}

.loc-detail-title {
  display: block;
  font-size: 26rpx;
  font-weight: 800;
  color: $z-text;
  margin-bottom: 14rpx;
}

.loc-detail-list {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.loc-detail-item {
  display: block;
  font-size: 23rpx;
  color: $z-text2;
  line-height: 1.5;
}

.loc-actions {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
  margin-bottom: 24rpx;
}

.primary-btn,
.secondary-btn {
  height: 88rpx;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
  font-weight: 800;
}

.primary-btn {
  color: $z-card;
  background: $z-primary;

  &.disabled { opacity: 0.6; }
}

.secondary-btn {
  color: $z-primary;
  background: rgba(13, 79, 74, 0.08);
}

.loc-hint {
  display: block;
  text-align: center;
  font-size: 20rpx;
  color: $z-muted;
  letter-spacing: 1rpx;
}
</style>
