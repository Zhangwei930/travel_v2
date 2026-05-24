<template>
  <view class="tab-bar" :style="{ paddingBottom: safeBottom }">
    <view
      v-for="item in items"
      :key="item.id"
      class="tab-item"
      :class="{ 'tab-center': item.center }"
      @tap="onTap(item)"
    >
      <!-- 中央凸起按钮 -->
      <view v-if="item.center" class="tab-center-btn">
        <svg-compass />
      </view>

      <!-- 普通 Tab 图标 -->
      <view v-else class="tab-icon">
        <component :is="item.icon" :active="current === item.path" />
      </view>

      <text class="tab-label" :class="{ active: current === item.path, 'center-label': item.center }">
        {{ item.label }}
      </text>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

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
  { id: 'home',      path: 'pages/index/index',      label: '首页', icon: 'IconHome' },
  { id: 'scenes',    path: 'pages/scenes/scenes',    label: '场景', icon: 'IconScenes' },
  { id: 'generate',  path: 'pages/generate/generate', label: '生成', center: true },
  { id: 'assistant', path: 'pages/assistant/chat',   label: '助手', icon: 'IconChat' },
  { id: 'profile',   path: 'pages/profile/profile',  label: '我的',  icon: 'IconUser' },
]

function onTap(item) {
  if (item.center) {
    uni.navigateTo({ url: '/pages/generate/generate' })
    return
  }
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

.tab-center-btn {
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
