<template>
  <view class="cy-route-card" @tap="$emit('tap')">
    <view class="cy-route-info">
      <text class="cy-route-title">{{ title }}</text>
      <text class="cy-route-sub">{{ sub }}</text>
    </view>
    <!-- 路线节点可视化：纯 view 元素，兼容小程序（不用 SVG data URI） -->
    <view class="cy-route-path-wrap">
      <view class="cy-route-track" />
      <view
        v-for="(node, i) in nodes"
        :key="i"
        class="cy-route-node"
        :style="{ left: node.left + '%', bottom: node.bottom + 'rpx', background: NODE_COLORS[i % NODE_COLORS.length] }"
      />
    </view>
  </view>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title:    { type: String, default: '' },
  sub:      { type: String, default: '' },
  stops:    { type: Number, default: 2 },
  image:    { type: String, default: '' },
  distance: { type: String, default: '' },
})
defineEmits(['tap', 'imgError'])

const NODE_COLORS = ['#E8876A', '#F5C84A', '#5CBDB0', '#3B7A6E', '#F0A060', '#7FC8C0']

// 节点位置：left(%) + bottom(rpx)，容器高 88rpx
// 对应原 SVG viewBox 0 0 320 90 的坐标换算
const NODE_DATA = {
  1: [{ left: 50,    bottom: 40 }],
  2: [{ left: 9,     bottom: 18 }, { left: 91, bottom: 52 }],
  3: [{ left: 9,     bottom: 14 }, { left: 50, bottom: 62 }, { left: 91, bottom: 24 }],
  4: [{ left: 9,     bottom: 18 }, { left: 37, bottom: 62 }, { left: 63, bottom: 14 }, { left: 91, bottom: 54 }],
  5: [{ left: 9,     bottom: 14 }, { left: 31, bottom: 62 }, { left: 54, bottom: 14 }, { left: 77, bottom: 62 }, { left: 91, bottom: 28 }],
}

const nodes = computed(() => {
  const count = Math.min(Math.max(props.stops || 2, 1), 5)
  return NODE_DATA[count]
})
</script>

<style lang="scss">
@import '../../uni.scss';

.cy-route-card {
  width: 100%;
  height: 180rpx;
  border-radius: 28rpx;
  position: relative;
  overflow: hidden;
  background: $cy-green-ls;
  border: 1rpx solid $cy-border;
  cursor: pointer;
}

.cy-route-info {
  position: relative;
  padding: 22rpx 24rpx 0;
  z-index: 1;
}

.cy-route-title {
  display: block;
  font-size: 30rpx;
  font-weight: 800;
  color: $cy-text;
}

.cy-route-sub {
  display: block;
  font-size: 22rpx;
  color: $cy-text-sub;
  margin-top: 6rpx;
}

.cy-route-path-wrap {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 88rpx;
}

// 水平中轴线
.cy-route-track {
  position: absolute;
  left: 9%;
  right: 9%;
  top: 50%;
  height: 4rpx;
  background: #C8DDD8;
  border-radius: 2rpx;
}

// 每个节点圆点
.cy-route-node {
  position: absolute;
  width: 24rpx;
  height: 24rpx;
  border-radius: 50%;
  margin-left: -12rpx;
  margin-bottom: -12rpx;
}
</style>
