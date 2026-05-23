<template>
  <view class="page">
    <view class="header" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="header-inner">
        <text class="back" @tap="goBack">←</text>
        <text class="title serif">我的足迹</text>
        <text class="count mono">{{ list.length }} 个地点</text>
      </view>
    </view>

    <scroll-view scroll-y class="list-scroll">
      <view v-if="list.length === 0" class="empty">
        <text class="empty-icon">👣</text>
        <text class="empty-text mono">还没有足迹，去探索地点详情页吧</text>
      </view>

      <!-- 时间线列表 -->
      <view class="timeline">
        <view v-for="(item, i) in list" :key="item.id" class="row" @tap="viewPoi(item.id)">
          <!-- 左：时间线 -->
          <view class="row-left">
            <view class="dot" />
            <view v-if="i < list.length - 1" class="line" />
          </view>

          <!-- 右：卡片 -->
          <view class="card">
            <image v-if="item.img" :src="item.img" class="thumb" mode="aspectFill" lazy-load />
            <view class="info">
              <text class="name serif">{{ item.name }}</text>
              <text class="cat">{{ item.cat }}</text>
              <text class="date mono">{{ formatDate(item.visitedAt) }}</text>
            </view>
            <text class="arrow">›</text>
          </view>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getVisited } from '../../api/storage.js'

const statusBarHeight = ref(44)
const list = ref([])

onMounted(() => {
  try { statusBarHeight.value = uni.getSystemInfoSync().statusBarHeight || 44 } catch (_) {}
  list.value = getVisited()
})

function goBack() { uni.navigateBack() }
function viewPoi(id) { uni.navigateTo({ url: `/pages/poi/detail?id=${id}` }) }

function formatDate(ts) {
  if (!ts) return ''
  const d = new Date(ts)
  const now = new Date()
  const diff = now - d
  if (diff < 60000)  return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)} 小时前`
  if (diff < 86400000 * 7) return `${Math.floor(diff / 86400000)} 天前`
  return `${d.getMonth() + 1}/${d.getDate()}`
}
</script>

<style lang="scss" scoped>
@import '../../uni.scss';

.page { min-height: 100vh; background: $z-bg; }

.header {
  background: $z-card;
  border-bottom: 1rpx solid $z-border;
  padding-bottom: 24rpx;
  &-inner { display: flex; align-items: center; padding: 16rpx 32rpx 0; gap: 16rpx; }
}
.back  { font-size: 36rpx; color: $z-accent; padding: 8rpx; }
.title { font-size: 36rpx; font-family: $serif; color: $z-text; flex: 1; }
.count { font-size: $font-mono; color: $z-muted; font-family: $mono; }

.list-scroll { height: calc(100vh - 120rpx); padding: 32rpx 32rpx 40rpx; box-sizing: border-box; }

.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 120rpx;
  gap: 20rpx;
}
.empty-icon { font-size: 72rpx; }
.empty-text { color: $z-muted; font-family: $mono; font-size: $font-mono; text-align: center; }

.timeline { display: flex; flex-direction: column; }

.row {
  display: flex;
  gap: 20rpx;
  margin-bottom: 0;
}

.row-left {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 24rpx;
  flex-shrink: 0;
  padding-top: 28rpx;
}

.dot {
  width: 16rpx;
  height: 16rpx;
  border-radius: 8rpx;
  background: $z-accent;
  flex-shrink: 0;
}

.line {
  flex: 1;
  width: 2rpx;
  background: $z-line;
  margin: 8rpx 0;
  min-height: 24rpx;
}

.card {
  flex: 1;
  display: flex;
  align-items: center;
  background: $z-card;
  border-radius: $radius-card;
  padding: 20rpx;
  margin-bottom: 20rpx;
  gap: 20rpx;
}

.thumb {
  width: 100rpx;
  height: 100rpx;
  border-radius: $radius-small;
  flex-shrink: 0;
}

.info { flex: 1; }
.name { display: block; font-family: $serif; font-size: 28rpx; color: $z-text; margin-bottom: 6rpx; }
.cat  { display: block; font-size: $font-sm; color: $z-muted; margin-bottom: 6rpx; }
.date { display: block; font-family: $mono; font-size: $font-mono; color: $z-muted; }
.arrow { font-size: 32rpx; color: $z-muted; }
</style>
