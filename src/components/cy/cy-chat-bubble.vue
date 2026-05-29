<template>
  <view class="cy-bubble-wrap" :class="{ 'cy-bubble-right': role === 'user' }">
    <view v-if="role === 'bot'" class="cy-bubble-avatar">
      <cy-robot-mascot :size="72" />
    </view>
    <view class="cy-bubble" :class="role === 'user' ? 'cy-bubble--user' : 'cy-bubble--bot'">
      <slot />
    </view>
    <view v-if="role === 'user'" class="cy-bubble-user-avatar">
      <image v-if="avatar" :src="avatar" class="cy-user-avatar-img" mode="aspectFill" />
      <view v-else class="cy-user-avatar-placeholder">
        <CyIcon name="user-muted" :size="44" />
      </view>
    </view>
  </view>
</template>

<script setup>
import CyRobotMascot from './cy-robot-mascot.vue'
import CyIcon from './cy-icon.vue'

defineProps({
  role:   { type: String, default: 'bot' }, // bot | user
  avatar: { type: String, default: '' },
})
</script>

<style lang="scss">
@import '../../uni.scss';

.cy-bubble-wrap {
  display: flex;
  align-items: flex-end;
  gap: 12rpx;
  padding: 0 28rpx;
  margin-bottom: 20rpx;

  &.cy-bubble-right {
    flex-direction: row-reverse;
  }
}

.cy-bubble-avatar {
  width: 72rpx;
  height: 72rpx;
  flex-shrink: 0;
}

.cy-bubble {
  max-width: 72%;
  border-radius: 24rpx;
  padding: 20rpx 24rpx;
  font-size: 28rpx;
  line-height: 1.6;

  &--bot {
    background: #F3F4F6;
    color: $cy-text;
    border-bottom-left-radius: 6rpx;
  }

  &--user {
    background: $cy-green-l;
    color: $cy-green-d;
    border-bottom-right-radius: 6rpx;
  }
}

.cy-bubble-user-avatar {
  width: 72rpx;
  height: 72rpx;
  border-radius: 9999rpx;
  overflow: hidden;
  flex-shrink: 0;
  background: #F3F4F6;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cy-user-avatar-img { width: 100%; height: 100%; }

.cy-user-avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
