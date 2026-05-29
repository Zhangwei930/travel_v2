<template>
  <view class="cy-chip" :class="'cy-chip--' + type" @tap="$emit('tap')">
    <slot />
  </view>
</template>

<script setup>
defineProps({
  type: { type: String, default: 'green' }, // green | blue | pink | plain | active
})
defineEmits(['tap'])
</script>

<style lang="scss">
@import '../../uni.scss';

.cy-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 6rpx 20rpx;
  border-radius: 9999rpx;
  font-size: 22rpx;
  font-weight: 500;
  white-space: nowrap;

  &--green {
    background: $cy-green-l;
    color: $cy-green-d;
  }
  &--blue {
    background: $cy-tag-blue-bg;
    color: $cy-tag-blue;
  }
  &--pink {
    background: $cy-tag-pink-bg;
    color: $cy-tag-pink;
  }
  &--plain {
    background: #F3F4F6;
    color: $cy-text-sub;
  }
  &--active {
    background: $cy-green;
    color: #fff;
  }
}
</style>
