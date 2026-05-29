<template>
  <view class="cy-entry-card" @tap="$emit('tap')">
    <view class="cy-ec-icon">
      <CyIcon :name="`entry-${iconType}`" :size="72" />
    </view>
    <text class="cy-ec-title">{{ title }}</text>
    <text class="cy-ec-sub">{{ desc }}</text>
  </view>
</template>

<script setup>
import CyIcon from './cy-icon.vue'

defineProps({
  iconType: { type: String, default: '' },
  title:    { type: String, default: '' },
  desc:     { type: String, default: '' },
})
defineEmits(['tap'])
</script>

<style lang="scss">
@import '../../uni.scss';

.cy-entry-card {
  background: #fff;
  border-radius: 24rpx;
  padding: 28rpx 16rpx 24rpx;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10rpx;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.05);
  cursor: pointer;
  width: 100%;
}

.cy-ec-icon {
  width: 72rpx;
  height: 72rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cy-ec-title {
  display: block;
  font-size: 26rpx;
  font-weight: 700;
  color: $cy-text;
  line-height: 1.3;
  text-align: center;
}

.cy-ec-sub {
  display: block;
  font-size: 21rpx;
  color: $cy-muted;
  text-align: center;
  line-height: 1.3;
}
</style>
