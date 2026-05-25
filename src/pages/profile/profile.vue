<template>
  <view class="page">
    <scroll-view scroll-y class="scroll-body" :style="{ paddingBottom: tabBarHeight }" :show-scrollbar="false">
      <!-- 用户信息 -->
      <view class="user-card" :style="{ paddingTop: statusBarH + 'px' }">
        <view class="user-main" @tap="onLogin">
          <view class="avatar">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="8" r="4" fill="#9CA3AF"/>
              <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7" stroke="#9CA3AF" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </view>
          <view class="user-info">
            <text class="user-name">游客用户</text>
            <text class="user-hint">点击登录/注册</text>
          </view>
        </view>
        <view class="settings-btn" @tap="goSettings">
          <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#6B7280" stroke-width="1.8" stroke-linecap="round">
            <circle cx="12" cy="12" r="3"/>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
          </svg>
        </view>
      </view>

      <!-- 统计 -->
      <view class="stats-row">
        <view class="stat-item" v-for="s in stats" :key="s.label" @tap="s.onTap && s.onTap()">
          <text class="stat-num">{{ s.num }}</text>
          <text class="stat-label">{{ s.label }}</text>
        </view>
      </view>

      <!-- 常用功能 -->
      <view class="section-title-row">
        <text class="section-title">常用功能</text>
      </view>

      <view class="func-grid">
        <view
          v-for="item in funcItems"
          :key="item.label"
          class="func-item"
          @tap="item.onTap && item.onTap()"
        >
          <view class="func-icon-bg" :style="{ background: item.bg }">
            <text class="func-icon">{{ item.icon }}</text>
          </view>
          <text class="func-label">{{ item.label }}</text>
        </view>
      </view>
    </scroll-view>

    <z-tab-bar current="profile" />
  </view>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import ZTabBar from '../../components/ZTabBar.vue'
import { getProfileStats } from '../../api/storage.js'

const tabBarHeight = ref('80px')
const statusBarH = ref(44)

const stats = ref([
  { num: '0',  label: '收藏', onTap: () => uni.navigateTo({ url: '/pages/saved/pois' }) },
  { num: '0',  label: '足迹', onTap: () => uni.navigateTo({ url: '/pages/saved/visited' }) },
  { num: '0',  label: '路线', onTap: () => uni.navigateTo({ url: '/pages/saved/plans' }) },
])

const funcItems = [
  { icon: '☆', label: '我的收藏', bg: '#FFF3E0', onTap: () => uni.navigateTo({ url: '/pages/saved/pois' }) },
  { icon: '🕐', label: '浏览历史', bg: '#E3F2FD', onTap: () => uni.navigateTo({ url: '/pages/saved/visited' }) },
  { icon: '🗺️', label: '我的路线', bg: '#E8F5E9', onTap: () => uni.navigateTo({ url: '/pages/saved/plans' }) },
  { icon: '⬇️', label: '离线地图', bg: '#F3E5F5', onTap: onlineMapTip },
  { icon: '💬', label: '意见反馈', bg: '#E8F4F0', onTap: () => uni.navigateTo({ url: '/pages/saved/feedback' }) },
  { icon: '⚙️', label: '设置',     bg: '#F5F5F5', onTap: goSettings },
]

function refreshStats() {
  const s = getProfileStats()
  stats.value[0].num = String(s.saved)
  stats.value[1].num = String(s.visited)
  stats.value[2].num = String(s.plans)
}

onMounted(() => {
  try {
    const sys = uni.getSystemInfoSync()
    statusBarH.value = sys.statusBarHeight || 44
    tabBarHeight.value = (sys.safeAreaInsets?.bottom || 18) + 56 + 'px'
  } catch (_) {}
  refreshStats()
  uni.$on('cityChanged', refreshStats)
})

onShow(() => refreshStats())
onUnmounted(() => uni.$off('cityChanged', refreshStats))

function onLogin() {
  uni.showToast({ title: '登录功能开发中', icon: 'none' })
}

function goSettings() {
  uni.showModal({
    title: '周密出游',
    content: 'v1.0.0 · 智能本地出游规划系统',
    showCancel: false,
  })
}

function onlineMapTip() {
  uni.showToast({ title: '离线地图功能开发中', icon: 'none' })
}
</script>

<style lang="scss">
@import '../../uni.scss';

.page {
  min-height: 100vh;
  background: $u-bg-soft;
}

.scroll-body { position: relative; }

// ── 用户信息卡 ──────────────────────────────────────────────
.user-card {
  background: #FFFFFF;
  padding: 28rpx 32rpx 32rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20rpx;
}

.user-main {
  display: flex;
  align-items: center;
  gap: 24rpx;
  flex: 1;
}

.avatar {
  width: 100rpx;
  height: 100rpx;
  border-radius: 50rpx;
  background: $u-bg-soft;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 6rpx;
}

.user-name {
  font-size: 34rpx;
  font-weight: 700;
  color: $u-text;
}

.user-hint {
  font-size: 24rpx;
  color: $z-primary;
}

.settings-btn {
  width: 56rpx;
  height: 56rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

// ── 统计 ──────────────────────────────────────────────────
.stats-row {
  background: #FFFFFF;
  margin-bottom: 20rpx;
  display: flex;
  border-bottom: 1rpx solid $u-line;
}

.stat-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 32rpx 0;
  position: relative;

  &::after {
    content: '';
    position: absolute;
    right: 0;
    top: 28rpx;
    bottom: 28rpx;
    width: 1rpx;
    background: $u-line;
  }

  &:last-child::after { display: none; }
}

.stat-num {
  font-size: 44rpx;
  font-weight: 800;
  color: $u-text;
  line-height: 1;
  margin-bottom: 6rpx;
}

.stat-label {
  font-size: 22rpx;
  color: $u-text-mute;
}

// ── 常用功能 ────────────────────────────────────────────────
.section-title-row {
  padding: 28rpx 32rpx 16rpx;
}

.section-title {
  font-size: 28rpx;
  font-weight: 700;
  color: $u-text;
}

.func-grid {
  background: #FFFFFF;
  margin: 0 0 20rpx;
  display: flex;
  flex-wrap: wrap;
  padding: 20rpx 16rpx;
  gap: 0;
}

.func-item {
  width: 25%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10rpx;
  padding: 24rpx 8rpx;
  box-sizing: border-box;
}

.func-icon-bg {
  width: 100rpx;
  height: 100rpx;
  border-radius: 28rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.func-icon {
  font-size: 44rpx;
  line-height: 1;
}

.func-label {
  font-size: 22rpx;
  color: $u-text-sub;
  text-align: center;
}
</style>
