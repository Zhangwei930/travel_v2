<!-- 场景色胶囊标签 -->
<template>
  <text
    class="z-tag"
    :style="{
      color: color || '#0D4F4A',
      background: (color || '#0D4F4A') + '20',
      fontSize: small ? '20rpx' : '22rpx',
      padding: small ? '4rpx 14rpx' : '6rpx 16rpx',
    }"
  >{{ label }}</text>
</template>

<script setup>
defineProps({
  label: { type: String, required: true },
  color: { type: String, default: '' },
  small: { type: Boolean, default: false },
})
</script>

<style lang="scss">
.z-tag {
  display: inline-flex;
  align-items: center;
  border-radius: 12rpx;
  font-weight: 600;
  white-space: nowrap;
  line-height: 1.4;
}
</style>
