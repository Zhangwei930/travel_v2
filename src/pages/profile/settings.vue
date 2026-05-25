<template>
  <view class="page">
    <!-- 导航栏 -->
    <view class="nav-bar" :style="{ paddingTop: statusBarH + 'px' }">
      <view class="nav-back" @tap="goBack">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#111" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="15 18 9 12 15 6"/>
        </svg>
      </view>
      <text class="nav-title">设置</text>
      <view style="width:44px"/>
    </view>

    <scroll-view scroll-y class="scroll-body">
      <!-- 定位与城市 -->
      <view class="group-label">定位与城市</view>
      <view class="group-card">
        <view class="row">
          <text class="row-label">当前城市</text>
          <text class="row-value">{{ cityStore.current }}</text>
        </view>
        <view class="divider"/>
        <view class="row" @tap="relocate">
          <text class="row-label">重新定位</text>
          <text class="row-arrow" :class="{ spinning: locating }">{{ locating ? '定位中…' : '›' }}</text>
        </view>
      </view>

      <!-- 缓存 -->
      <view class="group-label">缓存管理</view>
      <view class="group-card">
        <view class="row" @tap="onClearCache">
          <text class="row-label">清除缓存</text>
          <text class="row-sub">{{ cacheSize }}</text>
        </view>
      </view>

      <!-- 关于 -->
      <view class="group-label">关于</view>
      <view class="group-card">
        <view class="row">
          <text class="row-label">版本</text>
          <text class="row-value">v1.0.0</text>
        </view>
        <view class="divider"/>
        <view class="row" @tap="showPrivacy">
          <text class="row-label">隐私政策</text>
          <text class="row-arrow">›</text>
        </view>
        <view class="divider"/>
        <view class="row" @tap="uni.navigateTo({ url: '/pages/saved/feedback' })">
          <text class="row-label">意见反馈</text>
          <text class="row-arrow">›</text>
        </view>
      </view>

      <!-- 账号 -->
      <view v-if="userProfile" class="group-label">账号</view>
      <view v-if="userProfile" class="group-card">
        <view class="row logout-row" @tap="onLogout">
          <text class="row-label danger">退出登录</text>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useCityStore } from '../../store/city.js'
import { getUserProfile, clearUserProfile, clearTempCache } from '../../api/storage.js'

const cityStore   = useCityStore()
const statusBarH  = ref(44)
const locating    = ref(false)
const cacheSize   = ref('已清理')
const userProfile = ref(null)

onMounted(() => {
  try { statusBarH.value = uni.getSystemInfoSync().statusBarHeight || 44 } catch (_) {}
  userProfile.value = getUserProfile()
  estimateCache()
})

function estimateCache() {
  // 粗估：读两个缓存 key 的 JSON 长度
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
    success: r => {
      cityStore.setCoords(r.latitude, r.longitude)
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

function goBack() { uni.navigateBack() }

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

.page { min-height: 100vh; background: $u-bg-soft; }

.nav-bar {
  background: #fff; display: flex; align-items: center; justify-content: space-between;
  padding-left: 16px; padding-right: 16px; padding-bottom: 12px; border-bottom: 1rpx solid $u-line;
}
.nav-back { width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; }
.nav-title { font-size: 32rpx; font-weight: 700; color: $u-text; }

.scroll-body { padding-bottom: 60rpx; }

.group-label {
  font-size: 22rpx; color: $u-text-mute; font-weight: 500;
  padding: 32rpx 32rpx 12rpx; text-transform: uppercase; letter-spacing: .05em;
}
.group-card {
  background: #fff; margin: 0 0 8rpx;
  border-top: 1rpx solid $u-line; border-bottom: 1rpx solid $u-line;
}
.divider { height: 1rpx; background: $u-line; margin: 0 32rpx; }

.row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 32rpx 32rpx; min-height: 96rpx; box-sizing: border-box;
}
.row-label  { font-size: 30rpx; color: $u-text; }
.row-value  { font-size: 28rpx; color: $u-text-mute; }
.row-sub    { font-size: 26rpx; color: $u-text-mute; }
.row-arrow  { font-size: 36rpx; color: $u-text-mute; transition: opacity .2s; }
.danger     { color: #EF4444; }
</style>
