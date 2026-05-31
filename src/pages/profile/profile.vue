<template>
  <view class="cy-page">
    <scroll-view scroll-y class="cy-scroll" :style="{ paddingBottom: tabBarH }" :show-scrollbar="false">

      <!-- 用户头部卡 -->
      <view class="cy-user-card" :style="{ paddingTop: statusBarH + 'px' }">
        <view class="cy-user-main" @tap="onLogin">
          <view class="cy-avatar">
            <image v-if="profileAvatarSrc && !avatarBroken" :src="profileAvatarSrc" class="cy-avatar-img" mode="aspectFill" @error="onAvatarError" />
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
    <view v-if="showLoginSheet" class="cy-sheet-mask">
      <view class="cy-sheet">
        <view class="cy-sheet-handle" />
        <text class="cy-sheet-title">登录</text>
        <text class="cy-sheet-sub">使用默认头像和昵称快速登录，资料仅存本机</text>

        <button class="cy-save-btn" @tap="oneClickLogin">一键登录</button>

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
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { cacheAvatarFile, isRemoteAvatarFile } from '../../api/avatar.js'
import { consumePendingLoginRedirect, getProfileStats, getUserProfile, setUserProfile } from '../../api/storage.js'
import { setTabBarSelected } from '../../api/tabbar.js'
import CyIcon from '../../components/cy/cy-icon.vue'

const tabBarH    = ref('80px')
const statusBarH = ref(44)
const userProfile    = ref(null)
const showLoginSheet = ref(false)
const showOfflineSheet = ref(false)
const loginRedirect = ref('')
const avatarBroken = ref(false)
let avatarRepairing = false

const profileAvatarSrc = computed(() => {
  const avatar = userProfile.value?.avatar || ''
  return avatar && !isRemoteAvatarFile(avatar) ? avatar : ''
})

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
  loadUserProfile(true)
  refreshStats()
  uni.$on('cityChanged', refreshStats)
  uni.$on('profileLoginRequest', onProfileLoginRequest)
})

onShow(() => {
  setTabBarSelected(3)
  refreshStats()
  loadUserProfile(true)
  const redirect = consumePendingLoginRedirect()
  if (redirect && !userProfile.value) openLoginSheet(redirect)
})
onUnmounted(() => {
  uni.$off('cityChanged', refreshStats)
  uni.$off('profileLoginRequest', onProfileLoginRequest)
})

function openLoginSheet(redirect = '') {
  loginRedirect.value = redirect
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

function loadUserProfile(shouldRepair = false) {
  userProfile.value = getUserProfile()
  avatarBroken.value = false
  if (shouldRepair) repairRemoteUserAvatar()
}

async function repairRemoteUserAvatar() {
  const profile = userProfile.value
  const avatar = profile?.avatar || ''
  if (avatarRepairing || !isRemoteAvatarFile(avatar)) return avatar

  avatarRepairing = true
  let cachedAvatar = ''
  try {
    cachedAvatar = await cacheAvatarFile(avatar)
  } finally {
    avatarRepairing = false
  }

  if (userProfile.value?.avatar !== avatar) return userProfile.value?.avatar || ''
  if (!cachedAvatar || cachedAvatar === avatar) return avatar

  const nextProfile = { ...profile, avatar: cachedAvatar }
  setUserProfile(nextProfile)
  userProfile.value = nextProfile
  avatarBroken.value = false
  return cachedAvatar
}

// 一键登录：直接用系统默认头像 + 默认昵称（微信拿不到真实头像昵称，不再请求）
function oneClickLogin() {
  // 昵称仅本机显示，非账号标识；用时间戳后5位+1位随机，基本不会重
  const suffix = String(Date.now()).slice(-5) + Math.floor(Math.random() * 10)
  const profile = {
    name: '出游者' + suffix,
    avatar: '/static/images/avatar-default.svg',
    loginAt: Date.now(),
  }
  setUserProfile(profile)
  userProfile.value = profile
  avatarBroken.value = false
  afterLoginSuccess()
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

function goSettings() { uni.navigateTo({ url: '/pages/profile/settings' }) }
async function onAvatarError() {
  const avatar = userProfile.value?.avatar || ''
  const repaired = await repairRemoteUserAvatar()
  if (repaired && repaired !== avatar) return
  avatarBroken.value = true
}
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
