<template>
  <view class="page">
    <!-- Header 深墨青渐变 -->
    <view class="header" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="avatar-wrap">
        <view class="avatar">🧭</view>
      </view>
      <text class="explorer-mono mono">EXPLORER · LV.2</text>
      <text class="nickname serif">出游探索家</text>
      <text class="explore-sub">已探索 {{ exploredCount }} 个地方</text>
    </view>

    <scroll-view scroll-y class="scroll-body" :style="{ paddingBottom: tabBarHeight }" :show-scrollbar="false">
      <!-- 统计 3 列卡（悬浮 -32px） -->
      <view class="stats-card">
        <view class="stat-item" v-for="stat in stats" :key="stat.label">
          <text class="stat-num serif">{{ stat.num }}</text>
          <text class="stat-label">{{ stat.label }}</text>
        </view>
      </view>

      <!-- 知识贡献横幅 -->
      <view class="contribute-banner">
        <view class="contribute-left">
          <text class="contribute-title">🌱 已贡献 {{ feedbackCount }} 条反馈</text>
          <text class="contribute-sub">帮助系统更懂本地出游</text>
        </view>
        <view class="contribute-btn">查看 ›</view>
      </view>

      <!-- §M1 我的内容 -->
      <view class="section">
        <text class="menu-group-label mono">§ M1 · 我的内容</text>
        <view class="menu-card">
          <view class="menu-item" v-for="(item, i) in menuContent" :key="item.title">
            <text class="menu-no mono">{{ String(i + 1).padStart(2, '0') }}</text>
            <text class="menu-icon">{{ item.icon }}</text>
            <view class="menu-text">
              <text class="menu-title">{{ item.title }}</text>
              <text class="menu-sub">{{ item.sub }}</text>
            </view>
            <text class="menu-arrow">›</text>
          </view>
        </view>
      </view>

      <!-- §M2 设置 -->
      <view class="section">
        <text class="menu-group-label mono">§ M2 · 设置</text>
        <view class="menu-card">
          <view class="menu-item" v-for="(item, i) in menuSettings" :key="item.title">
            <text class="menu-no mono">{{ String(i + 1).padStart(2, '0') }}</text>
            <text class="menu-icon">{{ item.icon }}</text>
            <view class="menu-text">
              <text class="menu-title">{{ item.title }}</text>
              <text class="menu-sub">{{ item.sub }}</text>
            </view>
            <text class="menu-arrow">›</text>
          </view>
        </view>
      </view>

      <!-- §M3 管理 -->
      <view class="section">
        <text class="menu-group-label mono">§ M3 · 管理</text>
        <view class="menu-card">
          <view class="menu-item" @tap="goAdmin">
            <text class="menu-no mono">01</text>
            <text class="menu-icon">🛡️</text>
            <view class="menu-text">
              <text class="menu-title">知识库审核</text>
              <text class="menu-sub">待审核 · 通过 · 拒绝</text>
            </view>
            <text class="menu-arrow">›</text>
          </view>
        </view>
      </view>

      <!-- 底部署名 -->
      <view class="footer">
        <text class="footer-mono mono">地图 API · Dify · 本地 AI · WebSearch</text>
        <text class="footer-serif serif">※ 周密出游 · 让每一次出游都更稳 ※</text>
      </view>
    </scroll-view>

    <z-tab-bar current="profile" />
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ZTabBar from '../../components/ZTabBar.vue'
import { getProfileStats, getPlanHistory, getSavedPois } from '../../api/storage.js'

const statusBarHeight = ref(44)
const tabBarHeight    = ref('80px')

const stats = ref([
  { num: '0', label: '已生成方案' },
  { num: '0', label: '已收藏' },
  { num: '0', label: '足迹地点' },
])
const feedbackCount  = ref(0)
const exploredCount  = ref(0)

onMounted(() => {
  try {
    const sys = uni.getSystemInfoSync()
    statusBarHeight.value = sys.statusBarHeight || 44
    tabBarHeight.value = (sys.safeAreaInsets?.bottom || 18) + 56 + 'px'
  } catch (_) {}

  const s = getProfileStats()
  stats.value = [
    { num: String(s.plans),   label: '已生成方案' },
    { num: String(s.saved),   label: '已收藏' },
    { num: String(s.visited), label: '足迹地点' },
  ]
  exploredCount.value = s.visited
  feedbackCount.value = 0
  menuContent.value[0].sub = `${s.plans} 份已生成`
  menuContent.value[1].sub = s.saved > 0 ? `${s.saved} 个已收藏` : '地点 · 路线'
  menuContent.value[2].sub = `${s.visited} 个地点`
  menuContent.value[3].sub = `${feedbackCount.value} 条已贡献`
})

const menuContent = ref([
  { icon: '📋', title: '我的攻略',  sub: '0 份已生成' },
  { icon: '❤️', title: '我的收藏',  sub: '地点 · 路线' },
  { icon: '👣', title: '我的足迹',  sub: '0 个地点' },
  { icon: '💬', title: '我的反馈',  sub: '0 条已贡献' },
])

const menuSettings = [
  { icon: '📍', title: '位置与城市',  sub: '乌鲁木齐' },
  { icon: '🔔', title: '通知设置',    sub: '' },
  { icon: '🔒', title: '隐私与授权',  sub: '' },
  { icon: 'ℹ️', title: '关于周密出游', sub: 'v1.0.0' },
]

function goAdmin() {
  uni.navigateTo({ url: '/pages/admin/admin' })
}
</script>

<style lang="scss">
@import '../../uni.scss';

.page {
  min-height: 100vh;
  background: $z-bg;
}

.header {
  background: linear-gradient(180deg, $z-primary 0%, $z-primary-d 100%);
  padding: 0 32rpx 64rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-bottom: 64rpx;
}

.avatar-wrap {
  margin-top: 20rpx;
  margin-bottom: 16rpx;
}

.avatar {
  width: 124rpx;
  height: 124rpx;
  border-radius: 62rpx;
  background: linear-gradient(135deg, #FF6B35 0%, #FF9558 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 54rpx;
  border: 4rpx solid rgba(255, 255, 255, 0.3);
}

.explorer-mono {
  display: block;
  font-size: 20rpx;
  color: rgba(255, 255, 255, 0.65);
  letter-spacing: 3rpx;
  margin-bottom: 8rpx;
}

.nickname {
  display: block;
  color: #fff;
  font-size: 32rpx;
  font-weight: 900;
  margin-bottom: 8rpx;
}

.explore-sub {
  display: block;
  color: rgba(255, 255, 255, 0.65);
  font-size: 24rpx;
}

// 统计卡悬浮
.stats-card {
  margin: -40rpx 32rpx 0;
  background: $z-card;
  border-radius: $radius-card;
  box-shadow: 0 4rpx 20rpx rgba(13, 79, 74, 0.1);
  display: flex;
  padding: 28rpx;
  position: relative;
  z-index: 2;
}

.stat-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6rpx;

  &:not(:last-child) {
    border-right: 1rpx solid $z-line;
  }
}

.stat-num {
  font-size: 44rpx;
  font-weight: 900;
  color: $z-text;
}

.stat-label {
  font-size: 22rpx;
  color: $z-muted;
}

// 知识贡献
.contribute-banner {
  margin: 24rpx 32rpx 0;
  background: linear-gradient(135deg, rgba(244, 185, 66, 0.13), rgba(244, 185, 66, 0.05));
  border: 1rpx solid rgba(244, 185, 66, 0.3);
  border-radius: $radius-card;
  padding: 24rpx 28rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.contribute-title {
  display: block;
  font-size: 26rpx;
  font-weight: 700;
  color: $z-text;
  margin-bottom: 6rpx;
}

.contribute-sub {
  display: block;
  font-size: 22rpx;
  color: $z-muted;
}

.contribute-btn {
  font-size: 24rpx;
  color: #0D4F4A;
  font-weight: 600;
}

// 菜单
.section {
  padding: 28rpx 32rpx 0;
}

.menu-group-label {
  display: block;
  font-size: 20rpx;
  color: $z-muted;
  letter-spacing: 2rpx;
  margin-bottom: 14rpx;
}

.menu-card {
  background: $z-card;
  border-radius: $radius-card;
  overflow: hidden;
  box-shadow: 0 2rpx 10rpx rgba(13, 79, 74, 0.05);
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 20rpx;
  padding: 28rpx 28rpx;
  border-bottom: 1rpx solid $z-line;
  cursor: pointer;

  &:last-child {
    border-bottom: none;
  }
}

.menu-no {
  font-size: 20rpx;
  color: $z-muted;
  font-weight: 700;
  letter-spacing: 1rpx;
  width: 40rpx;
}

.menu-icon {
  font-size: 36rpx;
  width: 44rpx;
  text-align: center;
}

.menu-text {
  flex: 1;
}

.menu-title {
  display: block;
  font-size: 28rpx;
  color: $z-text;
  font-weight: 600;
  margin-bottom: 4rpx;
}

.menu-sub {
  display: block;
  font-size: 22rpx;
  color: $z-muted;
}

.menu-arrow {
  font-size: 30rpx;
  color: $z-muted;
}

// 底部署名
.footer {
  margin: 40rpx 32rpx 16rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10rpx;
}

.footer-mono {
  display: block;
  font-size: 19rpx;
  color: $z-muted;
  letter-spacing: 1.5rpx;
}

.footer-serif {
  display: block;
  font-size: 22rpx;
  color: $z-muted;
  font-weight: 600;
}
</style>
