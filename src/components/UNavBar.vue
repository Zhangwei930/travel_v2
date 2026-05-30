<!-- iOS 风顶部导航：左返回 / 中标题 / 右图标。所有内部页统一用它，保证位置/高度一致 -->
<template>
  <view class="u-navbar" :class="{ 'is-flat': flat }">
    <view class="u-navbar-pad" :style="{ height: statusBarHeight + 'px' }" />
    <view class="u-navbar-row">
      <view class="u-navbar-left">
        <view v-if="showBack" class="u-icon-btn" @tap="onBack">
          <CyIcon name="back-dark" :size="44" />
        </view>
      </view>
      <view class="u-navbar-title">
        <text class="u-navbar-title-text">{{ title }}</text>
      </view>
      <view class="u-navbar-right">
        <view v-if="rightIcon === 'search'" class="u-icon-btn" @tap="onRight">
          <CyIcon name="search-dark" :size="40" />
        </view>
        <view v-else-if="rightIcon === 'share'" class="u-icon-btn" @tap="onRight">
          <CyIcon name="share-dark" :size="40" />
        </view>
        <view v-else-if="rightIcon === 'more'" class="u-icon-btn" @tap="onRight">
          <CyIcon name="more-dark" :size="40" />
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import CyIcon from './cy/cy-icon.vue'

defineProps({
  title: { type: String, default: '' },
  showBack: { type: Boolean, default: true },
  rightIcon: { type: String, default: '' }, // search | share | more | ''
  flat: { type: Boolean, default: false },   // true = 透明无 border
})
const emit = defineEmits(['right'])

const statusBarHeight = ref(44)

onMounted(() => {
  try {
    const sys = uni.getWindowInfo()
    statusBarHeight.value = sys.statusBarHeight || 44
  } catch (_) {}
})

function onBack() {
  const stack = getCurrentPages()
  if (stack.length > 1) uni.navigateBack()
  else uni.switchTab({ url: '/pages/index/index' })
}

function onRight() {
  emit('right')
}
</script>

<style lang="scss">
@import '../uni.scss';

.u-navbar {
  background: #fff;
  border-bottom: 1rpx solid rgba(0, 0, 0, 0.04);

  &.is-flat {
    background: transparent;
    border-bottom: none;
  }
}

.u-navbar-row {
  height: 88rpx;
  position: relative;
  display: flex;
  align-items: center;
  padding: 0 16rpx;
}

.u-navbar-left,
.u-navbar-right {
  width: 80rpx;
  display: flex;
  align-items: center;
}

.u-navbar-right { justify-content: flex-end; }

.u-navbar-title {
  position: absolute;
  left: 0;
  right: 0;
  text-align: center;
  pointer-events: none;
}

.u-navbar-title-text {
  font-size: 32rpx;
  font-weight: 700;
  color: $z-text;
  letter-spacing: 0.5rpx;
}

.u-icon-btn {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 32rpx;
}
</style>
