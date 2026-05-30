<template>
  <view class="cy-navbar">
    <view class="cy-navbar-pad" :style="{ height: statusBarH + 'px' }" />
    <view class="cy-navbar-row">
      <view class="cy-navbar-left">
        <view v-if="showBack" class="cy-icon-btn" @tap="onBack">
          <CyIcon name="back-dark" :size="44" />
        </view>
      </view>
      <view class="cy-navbar-center">
        <text class="cy-navbar-title">{{ title }}</text>
        <text v-if="subtitle" class="cy-navbar-sub">{{ subtitle }}</text>
      </view>
      <view class="cy-navbar-right">
        <view v-if="rightIcon === 'search'" class="cy-icon-btn" @tap="$emit('right')">
          <CyIcon name="search-dark" :size="40" />
        </view>
        <view v-else-if="rightIcon === 'share'" class="cy-icon-btn" @tap="$emit('right')">
          <CyIcon name="share-dark" :size="40" />
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import CyIcon from './cy-icon.vue'

defineProps({
  title:     { type: String, default: '' },
  subtitle:  { type: String, default: '' },
  showBack:  { type: Boolean, default: true },
  rightIcon: { type: String, default: '' },
})
defineEmits(['right'])

const statusBarH = ref(44)

onMounted(() => {
  try {
    const sys = uni.getWindowInfo()
    statusBarH.value = sys.statusBarHeight || 44
  } catch (_) {}
})

function onBack() {
  const stack = getCurrentPages()
  if (stack.length > 1) uni.navigateBack()
  else uni.switchTab({ url: '/pages/index/index' })
}
</script>

<style lang="scss">
@import '../../uni.scss';

.cy-navbar {
  background: #fff;
  border-bottom: 1rpx solid $cy-border;
  flex-shrink: 0;
}

.cy-navbar-row {
  height: 88rpx;
  display: flex;
  align-items: center;
  padding: 0 16rpx;
  position: relative;
}

.cy-navbar-left,
.cy-navbar-right {
  width: 72rpx;
  display: flex;
  align-items: center;
  z-index: 1;
}

.cy-navbar-right { justify-content: flex-end; }

.cy-navbar-center {
  position: absolute;
  left: 0;
  right: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  pointer-events: none;
}

.cy-navbar-title {
  font-size: 34rpx;
  font-weight: 800;
  color: $cy-text;
  line-height: 1.2;
}

.cy-navbar-sub {
  font-size: 22rpx;
  color: $cy-muted;
  margin-top: 2rpx;
}

.cy-icon-btn {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
