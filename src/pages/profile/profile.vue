<template>
  <view class="page">
    <u-nav-bar title="个人中心" />

    <scroll-view scroll-y class="scroll-body" :style="{ paddingBottom: tabBarHeight }" :show-scrollbar="false">
      <!-- 用户信息区 -->
      <view class="user-header">
        <view class="user-avatar">
          <text>🧭</text>
        </view>
        <view class="user-info">
          <text class="user-name">出游探索家</text>
          <text class="user-rank">EXPLORER · LV.2</text>
        </view>
      </view>

      <!-- 统计数据 -->
      <view class="stats-row">
        <view class="stat-box" v-for="s in stats" :key="s.label">
          <text class="stat-num">{{ s.num }}</text>
          <text class="stat-label">{{ s.label }}</text>
        </view>
      </view>

      <!-- 贡献横幅 -->
      <view class="contribution-card" @tap="onMenuContent(3)">
        <view class="contribution-content">
          <text class="contribution-title">🌱 我的反馈与贡献</text>
          <text class="contribution-sub">您已提交 {{ feedbackCount }} 条反馈</text>
        </view>
        <text class="contribution-arrow">›</text>
      </view>

      <!-- 菜单组 -->
      <view class="menu-group">
        <view class="menu-header">
          <text class="menu-header-title">我的出游</text>
        </view>
        <view class="menu-list">
          <view class="menu-item" v-for="(item, i) in menuContent" :key="item.title" @tap="onMenuContent(i)">
            <view class="menu-item-left">
              <view class="menu-item-icon">{{ item.icon }}</view>
              <text class="menu-item-title">{{ item.title }}</text>
            </view>
            <view class="menu-item-right">
              <text class="menu-item-sub">{{ item.sub }}</text>
              <text class="menu-item-arrow">›</text>
            </view>
          </view>
        </view>
      </view>

      <view class="menu-group">
        <view class="menu-header">
          <text class="menu-header-title">系统设置</text>
        </view>
        <view class="menu-list">
          <view class="menu-item" v-for="(item, i) in menuSettings" :key="item.title" @tap="onMenuSetting(i)">
            <view class="menu-item-left">
              <view class="menu-item-icon">{{ item.icon }}</view>
              <text class="menu-item-title">{{ item.title }}</text>
            </view>
            <view class="menu-item-right">
              <text class="menu-item-sub">{{ item.sub }}</text>
              <text class="menu-item-arrow">›</text>
            </view>
          </view>
        </view>
      </view>

      <view class="menu-group" v-if="isAdmin">
        <view class="menu-header">
          <text class="menu-header-title">管理后台</text>
        </view>
        <view class="menu-list">
          <view class="menu-item" @tap="goAdmin">
            <view class="menu-item-left">
              <view class="menu-item-icon">🛡️</view>
              <text class="menu-item-title">知识库审核</text>
            </view>
            <view class="menu-item-right">
              <text class="menu-item-arrow">›</text>
            </view>
          </view>
        </view>
      </view>

      <view class="version-info">
        <text>Version 1.0.0 · © 2024 ZHOUMI TRAVEL</text>
      </view>
    </scroll-view>

    <z-tab-bar current="profile" />
  </view>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import ZTabBar from '../../components/ZTabBar.vue'
import UNavBar from '../../components/UNavBar.vue'
import { getProfileStats } from '../../api/storage.js'
import { api } from '../../api/mock.js'
import { useCityStore } from '../../store/city.js'
import { storeToRefs } from 'pinia'

const cityStore = useCityStore()
const { current: currentCity } = storeToRefs(cityStore)

const tabBarHeight = ref('80px')
const feedbackCount = ref(0)
const isAdmin = ref(true)

const stats = ref([
  { num: '0', label: '我的收藏' },
  { num: '0', label: '我的足迹' },
  { num: '0', label: '生成方案' },
])

const menuContent = ref([
  { icon: '📋', title: '我的攻略',  sub: '0 份已生成' },
  { icon: '❤️', title: '我的收藏',  sub: '地点 · 路线' },
  { icon: '👣', title: '我的足迹',  sub: '0 个地点' },
  { icon: '💬', title: '我的反馈',  sub: '0 条已贡献' },
])

const menuSettings = ref([
  { icon: '📍', title: '当前城市',  sub: currentCity.value },
  { icon: '🔔', title: '通知管理',  sub: '已开启' },
  { icon: '🔒', title: '隐私授权',  sub: '' },
  { icon: 'ℹ️', title: '关于助手',  sub: '' },
])

async function refreshStats() {
  const s = getProfileStats()
  stats.value = [
    { num: String(s.saved),   label: '我的收藏' },
    { num: String(s.visited), label: '我的足迹' },
    { num: String(s.plans),   label: '生成方案' },
  ]
  menuContent.value[0].sub = `${s.plans} 份`
  menuContent.value[1].sub = `${s.saved} 个`
  menuContent.value[2].sub = `${s.visited} 个`

  try {
    const res = await api.getFeedbackList()
    const arr = Array.isArray(res) ? res : (res?.items ?? [])
    feedbackCount.value = arr.length
    menuContent.value[3].sub = `${feedbackCount.value} 条`
  } catch (_) {}
  
  menuSettings.value[0].sub = currentCity.value
}

onMounted(async () => {
  try {
    const sys = uni.getSystemInfoSync()
    tabBarHeight.value = (sys.safeAreaInsets?.bottom || 18) + 56 + 'px'
  } catch (_) {}
  await refreshStats()
  uni.$on('cityChanged', refreshStats)
})

onUnmounted(() => { uni.$off('cityChanged', refreshStats) })

function goAdmin() { uni.navigateTo({ url: '/pages/admin/admin' }) }

function onMenuContent(i) {
  const urls = ['/pages/saved/plans', '/pages/saved/pois', '/pages/saved/visited', '/pages/saved/feedback']
  if (urls[i]) uni.navigateTo({ url: urls[i] })
}

function onMenuSetting(i) {
  if (i === 0) {
    uni.showToast({ title: `当前定位：${currentCity.value}\n可在「出游」Tab点击左上角手动切换`, icon: 'none' })
  } else if (i === 1) {
    // #ifdef MP-WEIXIN
    uni.openSetting()
    // #endif
  } else if (i === 2) {
    uni.showModal({ title: '隐私说明', content: '我们严格保护您的位置数据，仅用于本地出游推荐。', showCancel: false })
  } else if (i === 3) {
    uni.showModal({ title: '周密出游', content: 'v1.0.0\n智能本地出游规划系统\n基于 AI + 地图数据构建', showCancel: false })
  }
}
</script>

<style lang="scss">
@import '../../uni.scss';

.page {
  min-height: 100vh;
  background: $u-bg;
}

.scroll-body {
  position: relative;
}

// ── 用户信息 ────────────────────────────────────────────────
.user-header {
  padding: 40rpx 32rpx;
  display: flex;
  align-items: center;
  gap: 32rpx;
}

.user-avatar {
  width: 120rpx;
  height: 120rpx;
  background: $u-bg-soft;
  border-radius: 60rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 64rpx;
  box-shadow: $u-shadow;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}

.user-name {
  font-size: 36rpx;
  font-weight: 800;
  color: $u-text;
}

.user-rank {
  font-size: 18rpx;
  color: $u-text-mute;
  letter-spacing: 2rpx;
  font-family: $mono;
}

// ── 统计 ──────────────────────────────────────────────────
.stats-row {
  display: flex;
  padding: 0 32rpx 32rpx;
  gap: 20rpx;
}

.stat-box {
  flex: 1;
  background: $u-bg;
  border-radius: 24rpx;
  padding: 24rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4rpx;
  box-shadow: $u-shadow;
}

.stat-num {
  font-size: 40rpx;
  font-weight: 800;
  color: $u-text;
}

.stat-label {
  font-size: 20rpx;
  color: $u-text-mute;
}

// ── 贡献卡 ────────────────────────────────────────────────
.contribution-card {
  margin: 0 32rpx 40rpx;
  background: $u-tint-mint;
  border-radius: 24rpx;
  padding: 32rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.contribution-title {
  display: block;
  font-size: 28rpx;
  font-weight: 700;
  color: $z-primary;
  margin-bottom: 4rpx;
}

.contribution-sub {
  display: block;
  font-size: 22rpx;
  color: $z-primary-l;
}

.contribution-arrow {
  font-size: 40rpx;
  color: $z-primary;
  opacity: 0.5;
}

// ── 菜单 ──────────────────────────────────────────────────
.menu-group {
  margin-bottom: 40rpx;
  padding: 0 32rpx;
}

.menu-header {
  margin-bottom: 16rpx;
  padding-left: 8rpx;
}

.menu-header-title {
  font-size: 24rpx;
  font-weight: 800;
  color: $u-text-mute;
  letter-spacing: 1rpx;
}

.menu-list {
  background: $u-bg;
  border-radius: 24rpx;
  box-shadow: $u-shadow;
  overflow: hidden;
}

.menu-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 32rpx;
  border-bottom: 1rpx solid $u-line;
  
  &:last-child { border-bottom: none; }
}

.menu-item-left {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.menu-item-icon {
  font-size: 32rpx;
  width: 44rpx;
  text-align: center;
}

.menu-item-title {
  font-size: 28rpx;
  color: $u-text;
  font-weight: 600;
}

.menu-item-right {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.menu-item-sub {
  font-size: 24rpx;
  color: $u-text-mute;
}

.menu-item-arrow {
  font-size: 32rpx;
  color: $u-text-mute;
}

.version-info {
  text-align: center;
  padding: 40rpx 0 20rpx;
  font-size: 20rpx;
  color: $u-text-mute;
  letter-spacing: 1rpx;
}
</style>
