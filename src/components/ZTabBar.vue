<!-- 底部 5-Tab 导航（中央凸起 AI 生成按钮） -->
<template>
  <view class="ztab-bar" :style="{ paddingBottom: safeBottom }">
    <view
      v-for="item in items"
      :key="item.id"
      class="ztab-item"
      :class="{ 'is-center': item.center }"
      @tap="onTap(item)"
    >
      <!-- 中央凸起按钮 -->
      <view v-if="item.center" class="center-btn">
        <view class="compass-svg">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 26 26" fill="none">
            <path d="M3 13l8 4 4 8 7-19-19 7z" fill="#fff"/>
          </svg>
        </view>
      </view>

      <!-- 普通 Tab -->
      <template v-else>
        <view class="ztab-icon">
          <!-- home -->
          <svg v-if="item.id === 'home'" xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none">
            <path d="M3 9.5L12 3l9 6.5V20a1 1 0 01-1 1H5a1 1 0 01-1-1V9.5z"
              :stroke="isActive(item) ? '#0D4F4A' : '#8B9594'" stroke-width="2"
              :fill="isActive(item) ? '#0D4F4A22' : 'none'"/>
            <path d="M9 21V13h6v8" :stroke="isActive(item) ? '#0D4F4A' : '#8B9594'" stroke-width="2" stroke-linecap="round"/>
          </svg>
          <!-- scenes -->
          <svg v-else-if="item.id === 'scenes'" xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none">
            <rect x="3" y="3" width="7" height="7" rx="1" :stroke="isActive(item) ? '#0D4F4A' : '#8B9594'" stroke-width="2" :fill="isActive(item) ? '#0D4F4A22' : 'none'"/>
            <rect x="14" y="3" width="7" height="7" rx="1" :stroke="isActive(item) ? '#0D4F4A' : '#8B9594'" stroke-width="2"/>
            <rect x="3" y="14" width="7" height="7" rx="1" :stroke="isActive(item) ? '#0D4F4A' : '#8B9594'" stroke-width="2"/>
            <rect x="14" y="14" width="7" height="7" rx="1" :stroke="isActive(item) ? '#0D4F4A' : '#8B9594'" stroke-width="2" :fill="isActive(item) ? '#0D4F4A22' : 'none'"/>
          </svg>
          <!-- assistant -->
          <svg v-else-if="item.id === 'assistant'" xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none">
            <path d="M21 12a8 8 0 01-12.5 6.6L3 20l1.4-5.5A8 8 0 1121 12z"
              :stroke="isActive(item) ? '#0D4F4A' : '#8B9594'" stroke-width="2"
              :fill="isActive(item) ? '#0D4F4A22' : 'none'" stroke-linejoin="round"/>
            <circle cx="8.5" cy="12" r="1.2" :fill="isActive(item) ? '#0D4F4A' : '#8B9594'"/>
            <circle cx="12" cy="12" r="1.2" :fill="isActive(item) ? '#0D4F4A' : '#8B9594'"/>
            <circle cx="15.5" cy="12" r="1.2" :fill="isActive(item) ? '#0D4F4A' : '#8B9594'"/>
          </svg>
          <!-- profile -->
          <svg v-else-if="item.id === 'profile'" xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="8" r="4" :stroke="isActive(item) ? '#0D4F4A' : '#8B9594'" stroke-width="2" :fill="isActive(item) ? '#0D4F4A22' : 'none'"/>
            <path d="M4 21c0-4.4 3.6-8 8-8s8 3.6 8 8" :stroke="isActive(item) ? '#0D4F4A' : '#8B9594'" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </view>
      </template>

      <text
        class="ztab-label"
        :style="{
          color: item.center ? '#8B9594' : (isActive(item) ? '#0D4F4A' : '#8B9594'),
          fontWeight: isActive(item) ? '700' : '500',
        }"
      >{{ item.label }}</text>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
  current: { type: String, default: 'home' },
})

const safeBottom = ref('18px')

onMounted(() => {
  try {
    const sys = uni.getSystemInfoSync()
    const b = sys.safeAreaInsets?.bottom || 0
    safeBottom.value = Math.max(b, 18) + 'px'
  } catch (_) {}
})

const items = [
  { id: 'home',      path: '/pages/index/index',       label: '首页', tab: true },
  { id: 'scenes',    path: '/pages/scenes/scenes',     label: '场景', tab: true },
  { id: 'generate',  path: '/pages/generate/generate', label: '生成', center: true },
  { id: 'assistant', path: '/pages/assistant/chat',    label: '助手', tab: true },
  { id: 'profile',   path: '/pages/profile/profile',   label: '我的',  tab: true },
]

function isActive(item) {
  return props.current === item.id
}

function onTap(item) {
  if (item.center) {
    uni.navigateTo({ url: item.path })
    return
  }
  uni.switchTab({ url: item.path })
}
</script>

<style lang="scss">
@import '../uni.scss';

.ztab-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(255, 255, 255, 0.98);
  border-top: 1rpx solid $z-border;
  display: flex;
  align-items: flex-end;
  padding-top: 12rpx;
  z-index: 999;
  // backdrop-filter 在低端小程序机型降级
  backdrop-filter: blur(20px);
}

.ztab-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6rpx;
  padding-bottom: 8rpx;
  cursor: pointer;

  &.is-center {
    padding-bottom: 6rpx;
    gap: 8rpx;
  }
}

.center-btn {
  width: 104rpx;
  height: 104rpx;
  border-radius: 52rpx;
  background: linear-gradient(135deg, $z-accent 0%, $z-accent-l 100%);
  box-shadow: 0 12rpx 36rpx rgba(255, 107, 53, 0.55);
  margin-top: -28rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.compass-svg {
  display: flex;
  align-items: center;
  justify-content: center;
}

.ztab-icon {
  width: 44rpx;
  height: 44rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ztab-label {
  font-size: 20rpx;
  line-height: 1;
}
</style>
