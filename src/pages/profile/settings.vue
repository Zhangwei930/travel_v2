<template>
  <view class="cy-page">
    <cy-nav-bar title="设置" />

    <scroll-view scroll-y class="cy-scroll-body">
      <!-- 定位与城市 -->
      <text class="cy-group-label">定位与城市</text>
      <view class="cy-group-card">
        <view class="cy-row">
          <text class="cy-row-label">当前城市</text>
          <text class="cy-row-value">{{ cityStore.current }}</text>
        </view>
        <view class="cy-divider" />
        <view class="cy-row" @tap="relocate">
          <text class="cy-row-label">重新定位</text>
          <text class="cy-row-arrow" :class="{ spinning: locating }">{{ locating ? '定位中…' : '›' }}</text>
        </view>
      </view>

      <!-- 缓存 -->
      <text class="cy-group-label">缓存管理</text>
      <view class="cy-group-card">
        <view class="cy-row" @tap="onClearCache">
          <text class="cy-row-label">清除缓存</text>
          <text class="cy-row-sub">{{ cacheSize }}</text>
        </view>
      </view>

      <!-- 关于 -->
      <text class="cy-group-label">关于</text>
      <view class="cy-group-card">
        <view class="cy-row">
          <text class="cy-row-label">版本</text>
          <text class="cy-row-value">v2.0.0</text>
        </view>
        <view class="cy-divider" />
        <view class="cy-row" @tap="showPrivacy">
          <text class="cy-row-label">隐私政策</text>
          <text class="cy-row-arrow">›</text>
        </view>
        <view class="cy-divider" />
        <view class="cy-row" @tap="uni.navigateTo({ url: '/pages/saved/feedback' })">
          <text class="cy-row-label">意见反馈</text>
          <text class="cy-row-arrow">›</text>
        </view>
      </view>

      <!-- 账号 -->
      <text v-if="userProfile" class="cy-group-label">账号</text>
      <view v-if="userProfile" class="cy-group-card">
        <view class="cy-row" @tap="onLogout">
          <text class="cy-row-label cy-danger">退出登录</text>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../../api/index.js'
import { useCityStore } from '../../store/city.js'
import { getUserProfile, clearUserProfile, clearTempCache } from '../../api/storage.js'
import CyNavBar from '../../components/cy/cy-nav-bar.vue'

const cityStore   = useCityStore()
const locating    = ref(false)
const cacheSize   = ref('已清理')
const userProfile = ref(null)

onMounted(() => {
  userProfile.value = getUserProfile()
  estimateCache()
})

function estimateCache() {
  try {
    const keys = ['zhoumi_home_feed', 'zhoumi_assistant_context']
    let bytes = 0
    keys.forEach(k => {
      const v = uni.getStorageSync(k)
      if (v) bytes += JSON.stringify(v).length
    })
    cacheSize.value = bytes > 0 ? `约 ${Math.ceil(bytes / 1024)} KB` : '已清理'
  } catch (_) { cacheSize.value = '' }
}

function relocate() {
  if (locating.value) return
  locating.value = true
  uni.getLocation({
    type: 'gcj02',
    success: async r => {
      cityStore.setCoords(r.latitude, r.longitude)
      // 回查城市名与地标，让「当前城市」立即刷新
      try {
        const g = await api.geoCity(r.latitude, r.longitude)
        if (g?.city) cityStore.setFromLocation(g.city)
        if (g?.landmark) {
          cityStore.landmark = g.landmark
          try { uni.setStorageSync('zhoumi_landmark', g.landmark) } catch (_) {}
        }
      } catch (_) {}
      uni.showToast({ title: '定位成功', icon: 'success' })
    },
    fail: () => uni.showToast({ title: '定位失败，请检查权限', icon: 'none' }),
    complete: () => { locating.value = false },
  })
}

function onClearCache() {
  uni.showModal({
    title: '清除缓存',
    content: '将清除首页推荐和助手缓存，不会删除收藏和历史记录',
    success: r => {
      if (!r.confirm) return
      clearTempCache()
      cacheSize.value = '已清理'
      uni.showToast({ title: '清除成功', icon: 'success' })
    },
  })
}

function onLogout() {
  uni.showModal({
    title: '退出登录',
    content: '退出后头像和昵称将恢复默认，收藏和历史记录仍保留',
    success: r => {
      if (!r.confirm) return
      clearUserProfile()
      userProfile.value = null
      uni.showToast({ title: '已退出', icon: 'success' })
      setTimeout(() => uni.navigateBack(), 800)
    },
  })
}

function showPrivacy() {
  uni.showModal({
    title: '隐私政策',
    content: '本应用仅将您的位置信息用于附近出游推荐，头像和昵称仅存储在本设备，不上传至服务器。',
    showCancel: false,
  })
}
</script>

<style lang="scss">
@import '../../uni.scss';

.cy-page {
  min-height: 100vh;
  background: $cy-bg;
  font-family: "PingFang SC", "HarmonyOS Sans SC", "Noto Sans SC", -apple-system, system-ui, sans-serif;
}

.cy-scroll-body { padding-bottom: 60rpx; }

.cy-group-label {
  display: block;
  font-size: 22rpx;
  color: $cy-muted;
  font-weight: 500;
  padding: 32rpx 32rpx 12rpx;
  letter-spacing: .05em;
}

.cy-group-card {
  background: #fff;
  margin: 0 0 8rpx;
  border-top: 1rpx solid $cy-border;
  border-bottom: 1rpx solid $cy-border;
}

.cy-divider { height: 1rpx; background: $cy-border; margin: 0 32rpx; }

.cy-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 32rpx;
  min-height: 96rpx;
  box-sizing: border-box;
}

.cy-row-label  { font-size: 30rpx; color: $cy-text; }
.cy-row-value  { font-size: 28rpx; color: $cy-muted; }
.cy-row-sub    { font-size: 26rpx; color: $cy-muted; }
.cy-row-arrow  { font-size: 36rpx; color: $cy-muted; }
.cy-danger     { color: #EF4444; }
</style>
