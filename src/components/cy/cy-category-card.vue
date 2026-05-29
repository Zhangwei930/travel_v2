<template>
  <view class="cy-cat-card" :style="{ background: bg }" @tap="$emit('tap')">
    <view class="cy-cat-icon">
      <CyIcon v-if="iconType" :name="`cat-${iconType}`" :size="76" />
    </view>
    <text class="cy-cat-title">{{ title }}</text>
    <text class="cy-cat-desc">{{ desc }}</text>
  </view>
</template>

<script setup>
import CyIcon from './cy-icon.vue'

defineProps({
  icon:     { type: String, default: '' },
  iconType: { type: String, default: '' },
  title:    { type: String, default: '' },
  desc:     { type: String, default: '' },
  bg:       { type: String, default: '#DCEDE0' },
})
defineEmits(['tap'])
</script>

<style lang="scss">
@import '../../uni.scss';

.cy-cat-card {
  border-radius: 24rpx;
  padding: 32rpx 20rpx 28rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10rpx;
  cursor: pointer;
}

.cy-cat-icon {
  width: 96rpx;
  height: 96rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 2rpx;
}

.cy-cat-title {
  font-size: 28rpx;
  font-weight: 700;
  color: $cy-text;
  text-align: center;
}

.cy-cat-desc {
  font-size: 22rpx;
  color: $cy-muted;
  text-align: center;
  line-height: 1.4;
}
</style>
