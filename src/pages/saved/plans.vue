<template>
  <view class="page">
    <view class="header" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="header-inner">
        <text class="back" @tap="goBack">←</text>
        <text class="title serif">我的攻略</text>
        <text class="count mono">{{ list.length }} 份</text>
      </view>
    </view>

    <scroll-view scroll-y class="list-scroll">
      <view v-if="list.length === 0" class="empty mono">还没有生成过方案，去首页试试吧</view>

      <view v-for="item in list" :key="item.no" class="card" @tap="viewPlan(item)">
        <view class="card-meta">
          <text class="no mono">{{ item.no }}</text>
          <text class="date mono">{{ formatDate(item.createdAt) }}</text>
        </view>
        <text class="plan-title serif">{{ item.title }}</text>
        <text class="summary">{{ item.summary }}</text>
        <view class="pills">
          <text class="pill">⏱ {{ item.totalTime }}</text>
          <text class="pill">💰 {{ item.totalBudget }}</text>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getPlanHistory } from '../../api/storage.js'

const statusBarHeight = ref(44)
const list = ref([])

onMounted(() => {
  try { statusBarHeight.value = uni.getSystemInfoSync().statusBarHeight || 44 } catch (_) {}
  list.value = getPlanHistory()
})

function goBack() { uni.navigateBack() }

function viewPlan(item) {
  uni.setStorageSync('lastPlan', item)
  uni.navigateTo({ url: '/pages/result/result' })
}

function formatDate(ts) {
  if (!ts) return ''
  const d = new Date(ts)
  return `${d.getMonth() + 1}/${d.getDate()}`
}
</script>

<style lang="scss" scoped>
@import '@/uni.scss';

.page { min-height: 100vh; background: $z-bg; }

.header {
  background: $z-card;
  border-bottom: 1rpx solid $z-border;
  padding-bottom: 24rpx;
  &-inner { display: flex; align-items: center; padding: 16rpx 32rpx 0; gap: 16rpx; }
}
.back { font-size: 36rpx; color: $z-accent; padding: 8rpx; }
.title { font-size: 36rpx; font-family: $serif; color: $z-text; flex: 1; }
.count { font-size: $font-mono; color: $z-muted; font-family: $mono; }

.list-scroll { height: calc(100vh - 120rpx); padding: 24rpx; box-sizing: border-box; }
.empty { color: $z-muted; font-family: $mono; font-size: $font-mono; text-align: center; margin-top: 80rpx; display: block; }

.card {
  background: $z-card;
  border-radius: $radius-card;
  padding: 28rpx;
  margin-bottom: 20rpx;
}
.card-meta { display: flex; justify-content: space-between; margin-bottom: 12rpx; }
.no { font-family: $mono; font-size: $font-mono; color: $z-accent; }
.date { font-family: $mono; font-size: $font-mono; color: $z-muted; }
.plan-title { display: block; font-family: $serif; font-size: 32rpx; color: $z-text; margin-bottom: 10rpx; }
.summary { display: block; font-size: $font-body; color: $z-text2; line-height: 1.5; margin-bottom: 16rpx; }
.pills { display: flex; gap: 12rpx; }
.pill { font-size: $font-xs; color: $z-muted; background: $z-bg; padding: 6rpx 16rpx; border-radius: $radius-tag; }
</style>
