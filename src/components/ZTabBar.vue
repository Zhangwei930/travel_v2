<!-- 底部 4-Tab 导航 -->
<template>
  <view class="ztab-bar" :style="{ paddingBottom: safeBottom }">
    <view
      v-for="item in items"
      :key="item.id"
      class="ztab-item"
      :class="{ 'is-center': item.center }"
      @tap="onTap(item)"
    >
      <view class="ztab-icon">
        <CyIcon :name="iconName(item)" :size="48" />
      </view>

      <text
        class="ztab-label"
        :style="{
          color: item.center ? '#9AA3A8' : (isActive(item) ? '#1A8870' : '#9AA3A8'),
          fontWeight: isActive(item) ? '700' : '500',
        }"
      >{{ item.label }}</text>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import CyIcon from './cy/cy-icon.vue'

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
  { id: 'home',      path: '/pages/index/index',       label: '出游', tab: true },
  { id: 'scenes',    path: '/pages/scenes/scenes',     label: '发现', tab: true },
  { id: 'assistant', path: '/pages/assistant/chat',    label: '咨询', tab: true },
  { id: 'profile',   path: '/pages/profile/profile',   label: '我的',  tab: true },
]

function isActive(item) {
  return props.current === item.id
}

function iconName(item) {
  const suffix = isActive(item) ? 'active' : 'muted'
  const base = item.id === 'assistant' ? 'chat' : item.id
  return `${base}-${suffix}`
}

function onTap(item) {
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
  border-top: 1rpx solid $cy-border;
  display: flex;
  align-items: flex-end;
  padding-top: 16rpx;
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
  padding-bottom: 6rpx;
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
  width: 48rpx;
  height: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ztab-label {
  font-size: 24rpx;
  line-height: 1;
}
</style>
