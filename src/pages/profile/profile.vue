<template>
  <view class="cy-page">
    <scroll-view scroll-y class="cy-scroll" :style="{ paddingBottom: tabBarH }" :show-scrollbar="false">

      <!-- 用户头部卡 -->
      <view class="cy-user-card" :style="{ paddingTop: statusBarH + 'px' }">
        <view class="cy-user-main" @tap="onLogin">
          <view class="cy-avatar">
            <image v-if="userProfile?.avatar" :src="userProfile.avatar" class="cy-avatar-img" mode="aspectFill" />
            <CyIcon v-else name="user-fill-muted" :size="88" />
          </view>
          <view class="cy-user-info">
            <text class="cy-user-name">{{ userProfile?.name || '游客用户' }}</text>
            <text class="cy-user-hint">{{ userProfile ? '点击修改资料' : '点击登录/注册' }}</text>
          </view>
        </view>
      </view>

      <!-- 统计卡 -->
      <view class="cy-stats-card">
        <view class="cy-stat-item" v-for="s in stats" :key="s.label" @tap="s.onTap && s.onTap()">
          <text class="cy-stat-num">{{ s.num }}</text>
          <text class="cy-stat-label">{{ s.label }}</text>
        </view>
      </view>

      <!-- 常用功能 -->
      <view class="cy-func-card">
        <text class="cy-func-title">常用功能</text>
        <view class="cy-func-grid">
          <view
            v-for="item in funcItems"
            :key="item.label"
            class="cy-func-item"
            @tap="item.onTap && item.onTap()"
          >
            <view class="cy-func-icon-bg">
              <CyIcon :name="funcIconName(item.iconKey)" :size="52" />
            </view>
            <text class="cy-func-label">{{ item.label }}</text>
          </view>
        </view>
      </view>

      <view style="height: 32rpx;" />
    </scroll-view>

    <!-- 登录底栏 -->
    <view v-if="showLoginSheet" class="cy-sheet-mask" @tap.self="showLoginSheet = false">
      <view class="cy-sheet">
        <view class="cy-sheet-handle" />
        <text class="cy-sheet-title">微信授权登录</text>
        <text class="cy-sheet-sub">①点头像选微信头像 ②点昵称栏一键填入微信昵称 ③完成登录（仅存本机）</text>

        <!-- #ifdef MP-WEIXIN -->
        <!-- 昵称用 type=nickname，必须靠 form 提交才能稳定取到（input 事件时序会丢值）；昵称为空不阻断，默认"微信用户" -->
        <form class="cy-sheet-form" @submit="onSubmitProfile">
          <button class="cy-avatar-btn-lg" open-type="chooseAvatar" @chooseavatar="onChooseAvatar">
            <image class="cy-avatar-preview" :src="tempAvatar || '/static/images/avatar-default.svg'" mode="aspectFill" />
            <text class="cy-avatar-tip">{{ tempAvatar ? '点击更换头像' : '点击选择微信头像' }}</text>
          </button>
          <input class="cy-name-input" type="nickname" name="nickname" :value="tempName" placeholder="点这里一键填入微信昵称" placeholder-style="color:#9CA3AF" @input="onNameInput" @blur="onNameInput" />
          <button class="cy-save-btn" form-type="submit">完成登录</button>
        </form>
        <!-- #endif -->

        <!-- #ifdef H5 -->
        <image class="cy-avatar-preview" :src="tempAvatar || '/static/images/avatar-default.svg'" mode="aspectFill" />
        <input class="cy-name-input" :value="tempName" placeholder="输入昵称" placeholder-style="color:#9CA3AF" @input="e => tempName = e.detail.value" />
        <button class="cy-save-btn" :disabled="!tempName" @tap="saveProfile">确认授权</button>
        <!-- #endif -->

        <text class="cy-cancel-link" @tap="showLoginSheet = false">取消</text>
      </view>
    </view>

    <!-- 离线地图引导 -->
    <view v-if="showOfflineSheet" class="cy-sheet-mask" @tap.self="showOfflineSheet = false">
      <view class="cy-sheet">
        <view class="cy-sheet-handle" />
        <text class="cy-sheet-title">离线地图</text>
        <text class="cy-sheet-sub">本应用使用高德地图，可在高德 App 内下载离线地图包，断网环境下导航使用。</text>
        <view class="cy-offline-steps">
          <view class="cy-step-row"><text class="cy-step-num">1</text><text class="cy-step-text">打开高德地图 App</text></view>
          <view class="cy-step-row"><text class="cy-step-num">2</text><text class="cy-step-text">「我的」→「离线地图」</text></view>
          <view class="cy-step-row"><text class="cy-step-num">3</text><text class="cy-step-text">搜索城市，下载地图包</text></view>
        </view>
        <button class="cy-save-btn" @tap="showOfflineSheet = false">知道了</button>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { consumePendingLoginRedirect, getProfileStats, getUserProfile, setUserProfile } from '../../api/storage.js'
import { setTabBarSelected } from '../../api/tabbar.js'
import CyIcon from '../../components/cy/cy-icon.vue'

const tabBarH    = ref('80px')
const statusBarH = ref(44)
const userProfile    = ref(null)
const showLoginSheet = ref(false)
const showOfflineSheet = ref(false)
const tempAvatar = ref('')
const tempName   = ref('')
const loginRedirect = ref('')

const stats = ref([
  { num: '0', label: '收藏',  onTap: () => uni.navigateTo({ url: '/pages/saved/pois' }) },
  { num: '0', label: '足迹',  onTap: () => uni.navigateTo({ url: '/pages/saved/visited' }) },
  { num: '0', label: '路线',  onTap: () => uni.navigateTo({ url: '/pages/saved/plans' }) },
])

const funcItems = [
  { iconKey: 'star',     label: '我的收藏', onTap: () => uni.navigateTo({ url: '/pages/saved/pois' }) },
  { iconKey: 'history',  label: '浏览历史', onTap: () => uni.navigateTo({ url: '/pages/saved/visited' }) },
  { iconKey: 'route',    label: '我的路线', onTap: () => uni.navigateTo({ url: '/pages/saved/plans' }) },
  { iconKey: 'offline',  label: '离线地图', onTap: () => { showOfflineSheet.value = true } },
  { iconKey: 'settings', label: '设置',    onTap: goSettings },
]

function refreshStats() {
  const s = getProfileStats()
  stats.value[0].num = String(s.saved)
  stats.value[1].num = String(s.visited)
  stats.value[2].num = String(s.plans)
}

onMounted(() => {
  try {
    const sys = uni.getWindowInfo()
    statusBarH.value = sys.statusBarHeight || 44
    tabBarH.value = ((sys.safeAreaInsets?.bottom || 18) + 56) + 'px'
  } catch (_) {}
  userProfile.value = getUserProfile()
  refreshStats()
  uni.$on('cityChanged', refreshStats)
  uni.$on('profileLoginRequest', onProfileLoginRequest)
})

onShow(() => {
  setTabBarSelected(3)
  refreshStats()
  userProfile.value = getUserProfile()
  const redirect = consumePendingLoginRedirect()
  if (redirect && !userProfile.value) openLoginSheet(redirect)
})
onUnmounted(() => {
  uni.$off('cityChanged', refreshStats)
  uni.$off('profileLoginRequest', onProfileLoginRequest)
})

function openLoginSheet(redirect = '') {
  loginRedirect.value = redirect
  tempAvatar.value = userProfile.value?.avatar || ''
  tempName.value   = userProfile.value?.name   || ''
  showLoginSheet.value = true
}

function onLogin() { openLoginSheet() }

function onProfileLoginRequest(payload = {}) {
  if (userProfile.value) {
    if (payload.redirect) uni.navigateTo({ url: payload.redirect })
    return
  }
  openLoginSheet(payload.redirect || '')
}

function onChooseAvatar(e) {
  const tempUrl = e.detail.avatarUrl
  if (!tempUrl) {
    // chooseAvatar 可能因微信下载头像时网络被重置(ECONNRESET)而拿不到，提示重试
    uni.showToast({ title: '头像获取失败，请重试', icon: 'none' })
    return
  }
  // #ifdef MP-WEIXIN
  // 持久化头像临时文件(重启会失效)；用新版 FileSystemManager.saveFile 替代已废弃的 wx.saveFile
  try {
    wx.getFileSystemManager().saveFile({
      tempFilePath: tempUrl,
      success: (res) => { tempAvatar.value = res.savedFilePath },
      fail: () => { tempAvatar.value = tempUrl },
    })
  } catch (_) {
    tempAvatar.value = tempUrl
  }
  // #endif
  // #ifndef MP-WEIXIN
  tempAvatar.value = tempUrl
  // #endif
}

// #ifdef MP-WEIXIN
// 用 form 提交可靠取到微信昵称（type=nickname）。昵称为空不阻断登录，默认"微信用户"，可在"修改资料"再改。
function onSubmitProfile(e) {
  const name = (((e.detail.value && e.detail.value.nickname) || tempName.value || '').trim()) || '微信用户'
  const profile = { name, avatar: tempAvatar.value, loginAt: Date.now() }
  setUserProfile(profile)
  userProfile.value = profile
  afterLoginSuccess()
}
// #endif

function onNameInput(e) {
  tempName.value = e?.detail?.value || ''
}

function afterLoginSuccess() {
  const redirect = loginRedirect.value
  loginRedirect.value = ''
  showLoginSheet.value = false
  uni.showToast({ title: '登录成功', icon: 'success' })
  if (redirect) {
    setTimeout(() => uni.navigateTo({ url: redirect }), 300)
  }
}

function funcIconName(key) {
  const map = {
    star: 'star-line-green',
    history: 'history-green',
    route: 'route-green',
    offline: 'download-green',
    feedback: 'feedback-green',
    settings: 'gear-green',
  }
  return map[key] || 'star-line-green'
}

function saveProfile() {
  if (!tempName.value.trim()) return
  const profile = { name: tempName.value.trim(), avatar: tempAvatar.value, loginAt: Date.now() }
  setUserProfile(profile)
  userProfile.value = profile
  afterLoginSuccess()
}

function goSettings() { uni.navigateTo({ url: '/pages/profile/settings' }) }
</script>

<style lang="scss">
@import '../../uni.scss';

.cy-page {
  min-height: 100vh;
  background: $cy-bg;
  font-family: "PingFang SC", "HarmonyOS Sans SC", "Noto Sans SC", -apple-system, system-ui, sans-serif;
}

// ── 用户头部卡 ─────────────────────────────────────────────
.cy-user-card {
  background: $cy-green-l;
  border-radius: 32rpx;
  margin: 16rpx 28rpx 24rpx;
  padding: 36rpx 36rpx 40rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.cy-user-main { display: flex; align-items: center; gap: 24rpx; flex: 1; }

.cy-avatar {
  width: 130rpx;
  height: 130rpx;
  border-radius: 65rpx;
  background: rgba(255,255,255,0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  overflow: hidden;
  border: 4rpx solid rgba(255,255,255,0.8);
}

.cy-avatar-img { width: 100%; height: 100%; }

.cy-user-info { display: flex; flex-direction: column; gap: 6rpx; }

.cy-user-name { font-size: 36rpx; font-weight: 800; color: $cy-text; }
.cy-user-hint { font-size: 26rpx; color: $cy-green; font-weight: 500; }


// ── 统计卡 ─────────────────────────────────────────────────
.cy-stats-card {
  background: #fff;
  border-radius: 32rpx;
  margin: 0 28rpx 24rpx;
  display: flex;
  overflow: hidden;
  box-shadow: $cy-shadow;
}

.cy-stat-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 32rpx 0;
  position: relative;
  cursor: pointer;

  &::after {
    content: '';
    position: absolute;
    right: 0;
    top: 28rpx;
    bottom: 28rpx;
    width: 1rpx;
    background: $cy-border;
  }

  &:last-child::after { display: none; }
}

.cy-stat-num   { font-size: 44rpx; font-weight: 800; color: $cy-text; line-height: 1; margin-bottom: 6rpx; }
.cy-stat-label { font-size: 22rpx; color: $cy-muted; }

// ── 常用功能 ───────────────────────────────────────────────
.cy-func-card {
  background: #fff;
  border-radius: 32rpx;
  margin: 0 28rpx;
  padding: 36rpx 36rpx 44rpx;
  box-shadow: $cy-shadow;
}

.cy-func-title {
  display: block;
  font-size: 30rpx;
  font-weight: 800;
  color: $cy-text;
  margin-bottom: 20rpx;
}

.cy-func-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12rpx;
}

.cy-func-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10rpx;
  padding: 16rpx 0;
  cursor: pointer;
}

.cy-func-icon-bg {
  width: 108rpx;
  height: 108rpx;
  border-radius: 54rpx;
  background: $cy-green-ls;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 0;            // 消除 image 基线间隙，避免图标偏上

  .cy-icon { display: block; }
}

.cy-func-label { font-size: 24rpx; color: $cy-text; text-align: center; }

// ── 底部弹层 ───────────────────────────────────────────────
.cy-sheet-mask {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.45);
  z-index: 999;
  display: flex;
  align-items: flex-end;
}

.cy-sheet {
  width: 100%;
  background: #fff;
  border-radius: 32rpx 32rpx 0 0;
  padding: 20rpx 48rpx 60rpx;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24rpx;
}

.cy-sheet-handle { width: 80rpx; height: 8rpx; border-radius: 4rpx; background: #E5E7EB; }
.cy-sheet-title  { font-size: 36rpx; font-weight: 700; color: $cy-text; }
.cy-sheet-sub    { font-size: 24rpx; color: $cy-muted; text-align: center; line-height: 1.6; }

.cy-sheet-form {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24rpx;
}

.cy-avatar-preview { width: 160rpx; height: 160rpx; border-radius: 80rpx; background: $cy-green-ls; }

.cy-avatar-btn-lg {
  background: transparent; border: none; padding: 0; margin: 0; line-height: 1;
  display: flex; flex-direction: column; align-items: center; gap: 12rpx;
  &::after { border: none; }
}

.cy-avatar-tip { font-size: 24rpx; color: $cy-green; }

.cy-name-input {
  width: 100%; height: 96rpx;
  border: 1rpx solid $cy-border;
  border-radius: 16rpx; padding: 0 28rpx;
  box-sizing: border-box; font-size: 30rpx; color: $cy-text;
  background: $cy-green-ls;
}

.cy-save-btn {
  width: 100%; height: 96rpx; border-radius: 48rpx;
  background: $cy-green; color: #fff; font-size: 32rpx; font-weight: 600;
  display: flex; align-items: center; justify-content: center;
  border: none; margin-top: 8rpx;
  &[disabled] { opacity: 0.45; }
}

.cy-cancel-link { font-size: 26rpx; color: $cy-muted; padding: 8rpx 0; }

.cy-offline-steps { width: 100%; display: flex; flex-direction: column; gap: 20rpx; }
.cy-step-row  { display: flex; align-items: center; gap: 20rpx; }
.cy-step-num  { width: 48rpx; height: 48rpx; border-radius: 24rpx; background: $cy-green; color: #fff; font-size: 26rpx; font-weight: 700; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.cy-step-text { font-size: 28rpx; color: $cy-text; }
</style>
