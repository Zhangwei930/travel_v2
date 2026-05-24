<template>
  <view class="page">
    <u-nav-bar title="定位服务" />

    <view class="loc-content">
      <view class="loc-icon-wrap">
        <view class="loc-icon-bg">
          <text class="loc-icon">📍</text>
        </view>
        <view v-if="pending" class="loc-ripple" />
      </view>

      <view class="text-wrap">
        <text class="loc-title">{{ pending ? '正在定位中...' : '定位服务未开启' }}</text>
        <text class="loc-sub">允许位置权限后，系统将为您：</text>
      </view>

      <view class="usage-list">
        <view class="usage-item" v-for="(item, i) in usage" :key="i">
          <view class="usage-dot" />
          <text class="usage-text">{{ item }}</text>
        </view>
      </view>
    </view>

    <view class="action-wrap" :style="{ paddingBottom: safeBottom }">
      <view class="btn primary" :class="{ disabled: pending }" @tap="retry">
        <text>{{ pending ? '定位中...' : '重新尝试定位' }}</text>
      </view>
      <view class="btn secondary" @tap="useDefault">
        <text>使用默认城市进入</text>
      </view>
      <text class="action-hint">也可先进入默认城市，稍后在「出游」Tab 重新定位</text>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useCityStore } from '../../store/city.js'
import { api } from '../../api/mock.js'
import UNavBar from '../../components/UNavBar.vue'

const cityStore = useCityStore()
const pending = ref(false)
const safeBottom = ref('40rpx')

const usage = [
  '推荐附近 3-5 公里内的优质目的地',
  '按当前天气与时段智能调整推荐权重',
  '规划可一键导航的即兴出游路线',
  '位置数据仅用于本地计算，保障隐私'
]

onMounted(() => {
  try {
    const sys = uni.getSystemInfoSync()
    safeBottom.value = Math.max(sys.safeAreaInsets?.bottom || 20, 20) + 'px'
  } catch (_) {}
})

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
    fail: (err) => {
      pending.value = false
      const errMsg = err?.errMsg || ''
      if (errMsg.includes('auth deny') || errMsg.includes('auth denied')) {
        uni.showModal({
          title: '定位权限未开启',
          content: '我们需要您的位置信息来推荐出游地点。请前往设置开启。',
          confirmText: '去设置',
          success: (res) => {
            if (res.confirm) {
              uni.openSetting()
            }
          }
        })
      } else {
        uni.showToast({ title: '定位失败: ' + errMsg, icon: 'none', duration: 3000 })
      }
    },
  })
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
  background: #fff;
  display: flex;
  flex-direction: column;
}

.loc-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 0 60rpx;
}

.loc-icon-wrap {
  position: relative;
  width: 200rpx;
  height: 200rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 60rpx;
}

.loc-icon-bg {
  width: 140rpx;
  height: 140rpx;
  background: $u-bg-soft;
  border-radius: 70rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
  box-shadow: $u-shadow;
}

.loc-icon { font-size: 64rpx; }

.loc-ripple {
  position: absolute;
  width: 140rpx;
  height: 140rpx;
  background: $u-tint-mint;
  border-radius: 70rpx;
  animation: ripple 1.5s infinite ease-out;
}

@keyframes ripple {
  0% { transform: scale(1); opacity: 0.6; }
  100% { transform: scale(2.2); opacity: 0; }
}

.text-wrap {
  text-align: center;
  margin-bottom: 48rpx;
}

.loc-title {
  display: block;
  font-size: 40rpx;
  font-weight: 800;
  color: $u-text;
  margin-bottom: 12rpx;
}

.loc-sub {
  display: block;
  font-size: 26rpx;
  color: $u-text-mute;
}

.usage-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.usage-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.usage-dot {
  width: 10rpx;
  height: 10rpx;
  background: $z-primary;
  border-radius: 5rpx;
}

.usage-text {
  font-size: 26rpx;
  color: $u-text-sub;
}

.action-wrap {
  padding: 40rpx 48rpx;
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.btn {
  height: 96rpx;
  border-radius: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30rpx;
  font-weight: 800;

  &.primary {
    background: $z-primary;
    color: #fff;
    box-shadow: 0 8rpx 20rpx rgba(13, 79, 74, 0.2);
    &.disabled { opacity: 0.5; }
  }

  &.secondary {
    background: $u-bg-soft;
    color: $u-text;
  }
}

.action-hint {
  text-align: center;
  font-size: 20rpx;
  color: $u-text-mute;
  margin-top: 10rpx;
}
</style>
