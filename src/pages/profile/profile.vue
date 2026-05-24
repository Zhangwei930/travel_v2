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
          <view class="menu-item" v-for="(item, i) in menuContent" :key="item.title" @tap="onMenuContent(i)">
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
          <view class="menu-item" v-for="(item, i) in menuSettings" :key="item.title" @tap="onMenuSetting(i)">
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
import { ref, onMounted, onUnmounted } from 'vue'
import ZTabBar from '../../components/ZTabBar.vue'
import { getProfileStats } from '../../api/storage.js'
import { api } from '../../api/mock.js'
import { useCityStore } from '../../store/city.js'
import { storeToRefs } from 'pinia'

const cityStore = useCityStore()
const { current: currentCity } = storeToRefs(cityStore)

const statusBarHeight = ref(44)
const tabBarHeight    = ref('80px')

const stats = ref([
  { num: '0', label: '已生成方案' },
  { num: '0', label: '已收藏' },
  { num: '0', label: '足迹地点' },
])
const feedbackCount  = ref(0)
const exploredCount  = ref(0)

async function refreshStats() {
  const s = getProfileStats()
  stats.value = [
    { num: String(s.plans),   label: '已生成方案' },
    { num: String(s.saved),   label: '已收藏' },
    { num: String(s.visited), label: '足迹地点' },
  ]
  exploredCount.value = s.visited
  menuContent.value[0].sub = `${s.plans} 份已生成`
  menuContent.value[1].sub = s.saved > 0 ? `${s.saved} 个已收藏` : '地点 · 路线'
  menuContent.value[2].sub = `${s.visited} 个地点`

  // 反馈数走真实 API；失败时显示占位但不打断页面
  try {
    const res = await api.getFeedbackList()
    const arr = Array.isArray(res) ? res : (res?.items ?? [])
    feedbackCount.value = arr.length
  } catch (_) {
    feedbackCount.value = 0
  }
  menuContent.value[3].sub = `${feedbackCount.value} 条已贡献`
  menuSettings.value[0].sub = currentCity.value
}

onMounted(async () => {
  try {
    const sys = uni.getSystemInfoSync()
    statusBarHeight.value = sys.statusBarHeight || 44
    tabBarHeight.value = (sys.safeAreaInsets?.bottom || 18) + 56 + 'px'
  } catch (_) {}
  await refreshStats()
  uni.$on('cityChanged', refreshStats)
})

onUnmounted(() => {
  uni.$off('cityChanged', refreshStats)
})

const menuContent = ref([
  { icon: '📋', title: '我的攻略',  sub: '0 份已生成' },
  { icon: '❤️', title: '我的收藏',  sub: '地点 · 路线' },
  { icon: '👣', title: '我的足迹',  sub: '0 个地点' },
  { icon: '💬', title: '我的反馈',  sub: '0 条已贡献' },
])

const menuSettings = ref([
  { icon: '📍', title: '位置与城市',  sub: currentCity.value },
  { icon: '🔔', title: '通知设置',    sub: '' },
  { icon: '🔒', title: '隐私与授权',  sub: '' },
  { icon: 'ℹ️', title: '关于周密出游', sub: 'v1.0.0' },
])

function goAdmin() { uni.navigateTo({ url: '/pages/admin/admin' }) }

function onMenuContent(i) {
  if (i === 0) uni.navigateTo({ url: '/pages/saved/plans' })
  else if (i === 1) uni.navigateTo({ url: '/pages/saved/pois' })
  else if (i === 2) uni.navigateTo({ url: '/pages/saved/visited' })
  else if (i === 3) uni.navigateTo({ url: '/pages/saved/feedback' })
}

function onMenuSetting(i) {
  if (i === 0) {
    // 位置与城市 — 当前定位驱动，不可手动切换；显示提示
    uni.showToast({ title: `当前定位：${currentCity.value}\n回「出游」Tab 点城市可刷新`, icon: 'none', duration: 2500 })
  } else if (i === 1) {
    // 通知设置 — 跳到微信设置页（小程序），H5 兜底提示
    // #ifdef MP-WEIXIN
    uni.openSetting({ success: (r) => {
      const ok = r.authSetting?.['scope.userLocation']
      uni.showToast({ title: ok ? '已开启定位授权' : '设置已打开', icon: 'none' })
    }, fail: () => uni.showToast({ title: '请到「微信 → 设置 → 通知」开启', icon: 'none' }) })
    // #endif
    // #ifndef MP-WEIXIN
    uni.showToast({ title: '请到系统设置开启通知权限', icon: 'none' })
    // #endif
  } else if (i === 2) {
    // 隐私与授权 — 显示授权信息（位置/通知）
    uni.showActionSheet({
      itemList: ['查看当前授权状态', '清除本地数据', '隐私协议'],
      success: ({ tapIndex }) => {
        if (tapIndex === 0) {
          uni.getSetting({ success: (r) => {
            const a = r.authSetting || {}
            const lines = [
              `定位：${a['scope.userLocation'] ? '已允许' : '未授权'}`,
            ]
            uni.showModal({ title: '当前授权', content: lines.join('\n'), showCancel: false })
          }})
        } else if (tapIndex === 1) {
          uni.showModal({
            title: '清除本地数据',
            content: '将清除你的收藏、足迹、攻略历史。该操作不可撤销。',
            success: ({ confirm }) => {
              if (confirm) {
                try { uni.clearStorageSync() } catch (e) { console.warn('clearStorage failed', e) }
                uni.showToast({ title: '已清除', icon: 'success' })
                setTimeout(() => refreshStats(), 400)
              }
            },
          })
        } else if (tapIndex === 2) {
          uni.showModal({
            title: '隐私协议',
            content: '本应用收集你的定位用于推荐附近出游地点，不会上传到第三方。完整协议详见运营方公示。',
            showCancel: false,
          })
        }
      },
    })
  } else if (i === 3) {
    // 关于
    uni.showModal({
      title: '关于周密出游',
      content: '版本 v1.0.0\n智能本地出游规划系统\n地图：高德 API\nAI：Dify Workflow\n反馈邮箱：support@magies.top',
      showCancel: false,
    })
  }
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
  background: linear-gradient(135deg, $z-accent 0%, $z-accent-l 100%);
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
  color: $z-card;
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
  color: $z-primary;
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
