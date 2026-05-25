<template>
  <view class="page">
    <scroll-view scroll-y class="scroll-body" :style="{ paddingBottom: tabBarHeight }" :show-scrollbar="false">

      <!-- 用户信息卡 -->
      <view class="user-card" :style="{ paddingTop: statusBarH + 'px' }">
        <view class="user-main" @tap="onLogin">
          <view class="avatar">
            <image v-if="userProfile?.avatar" :src="userProfile.avatar" class="avatar-img" mode="aspectFill"/>
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="8" r="4" fill="#9CA3AF"/>
              <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7" stroke="#9CA3AF" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </view>
          <view class="user-info">
            <text class="user-name">{{ userProfile?.name || '游客用户' }}</text>
            <text class="user-hint">{{ userProfile ? '点击修改资料' : '点击微信授权登录' }}</text>
          </view>
        </view>
        <view class="settings-btn" @tap.stop="goSettings">
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

    <!-- 登录底栏 -->
    <view v-if="showLoginSheet" class="sheet-mask" @tap.self="showLoginSheet = false">
      <view class="login-sheet">
        <view class="sheet-handle"/>
        <text class="sheet-title">微信授权登录</text>
        <text class="sheet-sub">授权后获取头像和昵称，仅存储在本设备</text>

        <!-- 头像 — 先显示预览，button 只负责触发选择 -->
        <!-- #ifdef MP-WEIXIN -->
        <image
          class="avatar-preview"
          :src="tempAvatar || '/static/images/avatar-default.svg'"
          mode="aspectFill"
        />
        <button
          class="avatar-picker-btn"
          open-type="chooseAvatar"
          @chooseavatar="onChooseAvatar"
        >{{ tempAvatar ? '更换头像' : '选择微信头像' }}</button>
        <input
          class="name-input"
          type="nickname"
          :value="tempName"
          placeholder="点击填写微信昵称"
          placeholder-style="color:#9CA3AF"
          @change="e => tempName = e.detail.value"
        />
        <!-- #endif -->

        <!-- H5 降级 -->
        <!-- #ifdef H5 -->
        <image
          class="avatar-preview"
          :src="tempAvatar || '/static/images/avatar-default.svg'"
          mode="aspectFill"
        />
        <input
          class="name-input"
          :value="tempName"
          placeholder="输入昵称"
          placeholder-style="color:#9CA3AF"
          @input="e => tempName = e.detail.value"
        />
        <!-- #endif -->

        <button class="save-btn" :disabled="!tempName" @tap="saveProfile">
          确认授权
        </button>
        <text class="cancel-link" @tap="showLoginSheet = false">取消</text>
      </view>
    </view>

    <!-- 离线地图引导 -->
    <view v-if="showOfflineSheet" class="sheet-mask" @tap.self="showOfflineSheet = false">
      <view class="login-sheet">
        <view class="sheet-handle"/>
        <text class="sheet-title">离线地图</text>
        <text class="sheet-sub">本应用使用高德地图，可在高德 App 内下载离线地图包，断网环境下导航使用。</text>
        <view class="offline-steps">
          <view class="step-row"><text class="step-num">1</text><text class="step-text">打开高德地图 App</text></view>
          <view class="step-row"><text class="step-num">2</text><text class="step-text">「我的」→「离线地图」</text></view>
          <view class="step-row"><text class="step-num">3</text><text class="step-text">搜索城市，下载地图包</text></view>
        </view>
        <button class="save-btn" @tap="showOfflineSheet = false">知道了</button>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import ZTabBar from '../../components/ZTabBar.vue'
import { getProfileStats, getUserProfile, setUserProfile, clearUserProfile } from '../../api/storage.js'

const tabBarHeight = ref('80px')
const statusBarH   = ref(44)

const userProfile    = ref(null)
const showLoginSheet = ref(false)
const showOfflineSheet = ref(false)
const tempAvatar     = ref('')
const tempName       = ref('')

const stats = ref([
  { num: '0', label: '收藏',  onTap: () => uni.navigateTo({ url: '/pages/saved/pois' }) },
  { num: '0', label: '足迹',  onTap: () => uni.navigateTo({ url: '/pages/saved/visited' }) },
  { num: '0', label: '路线',  onTap: () => uni.navigateTo({ url: '/pages/saved/plans' }) },
])

const funcItems = [
  { icon: '☆',  label: '我的收藏', bg: '#FFF3E0', onTap: () => uni.navigateTo({ url: '/pages/saved/pois' }) },
  { icon: '🕐', label: '浏览历史', bg: '#E3F2FD', onTap: () => uni.navigateTo({ url: '/pages/saved/visited' }) },
  { icon: '🗺️', label: '我的路线', bg: '#E8F5E9', onTap: () => uni.navigateTo({ url: '/pages/saved/plans' }) },
  { icon: '⬇️', label: '离线地图', bg: '#F3E5F5', onTap: () => { showOfflineSheet.value = true } },
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
    statusBarH.value  = sys.statusBarHeight || 44
    tabBarHeight.value = (sys.safeAreaInsets?.bottom || 18) + 56 + 'px'
  } catch (_) {}
  userProfile.value = getUserProfile()
  refreshStats()
  uni.$on('cityChanged', refreshStats)
})
onShow(() => { refreshStats(); userProfile.value = getUserProfile() })
onUnmounted(() => uni.$off('cityChanged', refreshStats))

function onLogin() {
  tempAvatar.value = userProfile.value?.avatar || ''
  tempName.value   = userProfile.value?.name   || ''
  showLoginSheet.value = true
}

function onChooseAvatar(e) {
  tempAvatar.value = e.detail.avatarUrl
}

function saveProfile() {
  if (!tempName.value.trim()) return
  const profile = { name: tempName.value.trim(), avatar: tempAvatar.value, loginAt: Date.now() }
  setUserProfile(profile)
  userProfile.value = profile
  showLoginSheet.value = false
  uni.showToast({ title: '登录成功', icon: 'success' })
}

function goSettings() {
  uni.navigateTo({ url: '/pages/profile/settings' })
}
</script>

<style lang="scss">
@import '../../uni.scss';

.page { min-height: 100vh; background: $u-bg-soft; }
.scroll-body { position: relative; }

// ── 用户信息卡 ──────────────────────────────
.user-card {
  background: #fff;
  padding: 28rpx 32rpx 32rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20rpx;
}
.user-main { display: flex; align-items: center; gap: 24rpx; flex: 1; }
.avatar {
  width: 100rpx; height: 100rpx; border-radius: 50rpx;
  background: $u-bg-soft;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; overflow: hidden;
}
.avatar-img { width: 100%; height: 100%; border-radius: 50rpx; }
.user-info { display: flex; flex-direction: column; gap: 6rpx; }
.user-name  { font-size: 34rpx; font-weight: 700; color: $u-text; }
.user-hint  { font-size: 24rpx; color: $z-primary; }
.settings-btn { width: 56rpx; height: 56rpx; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }

// ── 统计 ────────────────────────────────────
.stats-row { background: #fff; margin-bottom: 20rpx; display: flex; border-bottom: 1rpx solid $u-line; }
.stat-item {
  flex: 1; display: flex; flex-direction: column; align-items: center; padding: 32rpx 0; position: relative;
  &::after { content: ''; position: absolute; right: 0; top: 28rpx; bottom: 28rpx; width: 1rpx; background: $u-line; }
  &:last-child::after { display: none; }
}
.stat-num   { font-size: 44rpx; font-weight: 800; color: $u-text; line-height: 1; margin-bottom: 6rpx; }
.stat-label { font-size: 22rpx; color: $u-text-mute; }

// ── 常用功能 ────────────────────────────────
.section-title-row { padding: 28rpx 32rpx 16rpx; }
.section-title { font-size: 28rpx; font-weight: 700; color: $u-text; }
.func-grid { background: #fff; margin: 0 0 20rpx; display: flex; flex-wrap: wrap; padding: 20rpx 16rpx; }
.func-item { width: 25%; display: flex; flex-direction: column; align-items: center; gap: 10rpx; padding: 24rpx 8rpx; box-sizing: border-box; }
.func-icon-bg { width: 100rpx; height: 100rpx; border-radius: 28rpx; display: flex; align-items: center; justify-content: center; }
.func-icon  { font-size: 44rpx; line-height: 1; }
.func-label { font-size: 22rpx; color: $u-text-sub; text-align: center; }

// ── 底部弹层 ─────────────────────────────────
.sheet-mask {
  position: fixed; inset: 0; background: rgba(0,0,0,.45); z-index: 999;
  display: flex; align-items: flex-end;
}
.login-sheet {
  width: 100%; background: #fff; border-radius: 32rpx 32rpx 0 0;
  padding: 20rpx 48rpx 60rpx; box-sizing: border-box;
  display: flex; flex-direction: column; align-items: center; gap: 24rpx;
}
.sheet-handle { width: 80rpx; height: 8rpx; border-radius: 4rpx; background: #E5E7EB; }
.sheet-title  { font-size: 36rpx; font-weight: 700; color: $u-text; }
.sheet-sub    { font-size: 24rpx; color: $u-text-mute; text-align: center; line-height: 1.6; }

.avatar-preview { width: 160rpx; height: 160rpx; border-radius: 80rpx; background: $u-bg-soft; }
.avatar-picker-btn {
  height: 72rpx; padding: 0 40rpx; margin: 0;
  background: $u-bg-soft; border: 1rpx solid $u-line;
  border-radius: 36rpx; font-size: 26rpx; color: $u-text-sub;
  display: flex; align-items: center; justify-content: center;
  line-height: normal; after: none;
}

.name-input {
  width: 100%; height: 96rpx; border: 1rpx solid $u-line;
  border-radius: 16rpx; padding: 0 28rpx; box-sizing: border-box;
  font-size: 30rpx; color: $u-text; background: $u-bg-soft;
}
.save-btn {
  width: 100%; height: 96rpx; border-radius: 48rpx;
  background: $z-primary; color: #fff; font-size: 32rpx; font-weight: 600;
  display: flex; align-items: center; justify-content: center;
  border: none; margin-top: 8rpx;
  &[disabled] { opacity: .45; }
}
.cancel-link { font-size: 26rpx; color: $u-text-mute; padding: 8rpx 0; }

// ── 离线地图步骤 ─────────────────────────────
.offline-steps { width: 100%; display: flex; flex-direction: column; gap: 20rpx; }
.step-row { display: flex; align-items: center; gap: 20rpx; }
.step-num  { width: 48rpx; height: 48rpx; border-radius: 24rpx; background: $z-primary; color: #fff; font-size: 26rpx; font-weight: 700; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.step-text { font-size: 28rpx; color: $u-text; }
</style>
