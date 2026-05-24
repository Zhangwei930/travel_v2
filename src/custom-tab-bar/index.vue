<template>
  <view class="tab-bar" :style="{ paddingBottom: safeBottom }">
    <view
      v-for="item in items"
      :key="item.id"
      class="tab-item"
      :class="{ 'tab-center': item.center }"
      @tap="onTap(item)"
    >
      <view class="tab-icon">
        <svg v-if="item.id === 'home'" xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none">
          <path d="M3 9.5L12 3l9 6.5V20a1 1 0 01-1 1H5a1 1 0 01-1-1V9.5z"
            :stroke="isActive(item) ? '#0D4F4A' : '#8B9594'" stroke-width="2"
            :fill="isActive(item) ? '#0D4F4A22' : 'none'"/>
          <path d="M9 21V13h6v8" :stroke="isActive(item) ? '#0D4F4A' : '#8B9594'" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <svg v-else-if="item.id === 'scenes'" xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none">
          <rect x="3" y="3" width="7" height="7" rx="1" :stroke="isActive(item) ? '#0D4F4A' : '#8B9594'" stroke-width="2" :fill="isActive(item) ? '#0D4F4A22' : 'none'"/>
          <rect x="14" y="3" width="7" height="7" rx="1" :stroke="isActive(item) ? '#0D4F4A' : '#8B9594'" stroke-width="2"/>
          <rect x="3" y="14" width="7" height="7" rx="1" :stroke="isActive(item) ? '#0D4F4A' : '#8B9594'" stroke-width="2"/>
          <rect x="14" y="14" width="7" height="7" rx="1" :stroke="isActive(item) ? '#0D4F4A' : '#8B9594'" stroke-width="2" :fill="isActive(item) ? '#0D4F4A22' : 'none'"/>
        </svg>
        <svg v-else-if="item.id === 'assistant'" xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none">
          <path d="M21 12a8 8 0 01-12.5 6.6L3 20l1.4-5.5A8 8 0 1121 12z"
            :stroke="isActive(item) ? '#0D4F4A' : '#8B9594'" stroke-width="2"
            :fill="isActive(item) ? '#0D4F4A22' : 'none'" stroke-linejoin="round"/>
          <circle cx="8.5" cy="12" r="1.2" :fill="isActive(item) ? '#0D4F4A' : '#8B9594'"/>
          <circle cx="12" cy="12" r="1.2" :fill="isActive(item) ? '#0D4F4A' : '#8B9594'"/>
          <circle cx="15.5" cy="12" r="1.2" :fill="isActive(item) ? '#0D4F4A' : '#8B9594'"/>
        </svg>
        <svg v-else-if="item.id === 'profile'" xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none">
          <circle cx="12" cy="8" r="4" :stroke="isActive(item) ? '#0D4F4A' : '#8B9594'" stroke-width="2" :fill="isActive(item) ? '#0D4F4A22' : 'none'"/>
          <path d="M4 21c0-4.4 3.6-8 8-8s8 3.6 8 8" :stroke="isActive(item) ? '#0D4F4A' : '#8B9594'" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </view>

      <text class="tab-label" :class="{ active: isActive(item), 'center-label': item.center }">
        {{ item.label }}
      </text>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
  current: { type: String, default: 'pages/index/index' },
})

const safeBottom = ref('0px')

onMounted(() => {
  const sysInfo = uni.getSystemInfoSync()
  const bottom = sysInfo.safeAreaInsets?.bottom || 0
  safeBottom.value = bottom + 'px'
})

const items = [
  { id: 'home',      path: 'pages/index/index',      label: '出游' },
  { id: 'scenes',    path: 'pages/scenes/scenes',    label: '发现' },
  { id: 'assistant', path: 'pages/assistant/chat',   label: '咨询' },
  { id: 'profile',   path: 'pages/profile/profile',  label: '我的' },
]

function isActive(item) {
  return props.current === item.id || props.current === item.path
}

function onTap(item) {
  uni.switchTab({ url: '/' + item.path })
}
</script>

<style lang="scss">
@import '../uni.scss';

.tab-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(20px);
  border-top: 1rpx solid $z-border;
  display: flex;
  align-items: flex-end;
  padding-top: 12rpx;
  z-index: 999;
}

.tab-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6rpx;
  padding-bottom: 8rpx;
  cursor: pointer;

  &.tab-center {
    padding-bottom: 0;
    gap: 6rpx;
  }
}

.tab-icon {
  width: 44rpx;
  height: 44rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tab-label {
  font-size: 20rpx;
  font-weight: 500;
  color: $z-muted;
  line-height: 1;

  &.active {
    color: $z-primary;
    font-weight: 700;
  }

  &.center-label {
    color: $z-muted;
  }
}
</style>
