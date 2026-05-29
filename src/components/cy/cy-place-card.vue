<template>
  <view class="cy-place-card" @tap="$emit('tap')">
    <view class="cy-place-thumb">
      <image :src="image" class="cy-place-img" mode="aspectFill" lazy-load @error="$emit('imgError')" />
    </view>
    <view class="cy-place-body">
      <view class="cy-place-row1">
        <text class="cy-place-name">{{ name }}</text>
        <text class="cy-place-dist">{{ distance }}</text>
      </view>
      <text v-if="desc" class="cy-place-desc">{{ desc }}</text>
      <view class="cy-place-row3">
        <view class="cy-place-tags">
          <view v-for="tag in (tags || []).slice(0, 3)" :key="tag" class="cy-ptag">{{ tag }}</view>
        </view>
        <view v-if="rating" class="cy-place-rating">
          <CyIcon name="star-yellow" :size="24" />
          <text class="cy-rating-num">{{ rating }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import CyIcon from './cy-icon.vue'

defineProps({
  name:     { type: String, default: '' },
  distance: { type: String, default: '' },
  desc:     { type: String, default: '' },
  image:    { type: String, default: '' },
  rating:   { type: [String, Number], default: '' },
  tags:     { type: Array, default: () => [] },
})
defineEmits(['tap', 'imgError'])
</script>

<style lang="scss">
@import '../../uni.scss';

.cy-place-card {
  background: #fff;
  border-radius: 28rpx;
  border: 1rpx solid $cy-border;
  padding: 24rpx;
  margin-bottom: 20rpx;
  display: flex;
  gap: 24rpx;
  box-shadow: 0 2rpx 6rpx rgba(0,0,0,0.03);
  cursor: pointer;
}

.cy-place-thumb {
  width: 180rpx;
  height: 180rpx;
  border-radius: 20rpx;
  overflow: hidden;
  flex-shrink: 0;
  background: $cy-green-ls;
}

.cy-place-img { width: 100%; height: 100%; }

.cy-place-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.cy-place-row1 {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 8rpx;
}

.cy-place-name {
  font-size: 32rpx;
  font-weight: 700;
  color: $cy-text;
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cy-place-dist {
  font-size: 26rpx;
  color: $cy-green;
  font-weight: 600;
  flex-shrink: 0;
}

.cy-place-desc {
  font-size: 26rpx;
  color: $cy-muted;
  line-height: 1.4;
  margin-top: 8rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cy-place-row3 {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: auto;
  padding-top: 16rpx;
}

.cy-place-tags {
  display: flex;
  gap: 8rpx;
  flex-wrap: wrap;
}

.cy-ptag {
  font-size: 22rpx;
  color: $cy-green;
  background: $cy-green-l;
  padding: 6rpx 16rpx;
  border-radius: 16rpx;
}

.cy-place-rating {
  display: flex;
  align-items: center;
  gap: 4rpx;
}

.cy-rating-num {
  font-size: 24rpx;
  color: $cy-text;
  font-weight: 600;
}
</style>
