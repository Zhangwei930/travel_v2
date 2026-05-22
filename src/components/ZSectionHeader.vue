<!-- §N 索引风章节标题 -->
<template>
  <view class="sec-header">
    <view class="sec-left">
      <text class="sec-no mono">§ {{ no }}</text>
      <view>
        <text class="sec-title serif">{{ title }}</text>
        <text v-if="sub" class="sec-sub">{{ sub }}</text>
      </view>
    </view>
    <text v-if="action" class="sec-action" @tap="$emit('action')">{{ action }} ›</text>
  </view>
</template>

<script setup>
defineProps({
  no:     { type: String, required: true },
  title:  { type: String, required: true },
  sub:    { type: String, default: '' },
  action: { type: String, default: '' },
})
defineEmits(['action'])
</script>

<style lang="scss">
@import '../uni.scss';

.sec-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-bottom: 22rpx;
}

.sec-left {
  display: flex;
  align-items: baseline;
  gap: 16rpx;
}

.sec-no {
  font-size: $font-mono;
  color: $z-muted;
  font-weight: 700;
  letter-spacing: 1rpx;
}

.sec-title {
  display: block;
  font-size: 30rpx;
  font-weight: 800;
  color: $z-text;
  line-height: 1.2;
}

.sec-sub {
  display: block;
  font-size: $font-mono;
  color: $z-muted;
  margin-top: 4rpx;
}

.sec-action {
  font-size: 23rpx;
  color: #0D4F4A;
  font-weight: 600;
}
</style>
