<template>
  <view class="cy-robot" :style="{ width: size + 'rpx', height: size + 'rpx' }">
    <image class="cy-robot-img" src="/static/images/ui/robot-full.png" mode="aspectFit" />
  </view>
</template>

<script setup>
defineProps({
  size: { type: Number, default: 80 },
})
</script>

<style lang="scss">
.cy-robot {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.cy-robot-img {
  width: 100%;
  height: 100%;
}
</style>
