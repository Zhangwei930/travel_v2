<template>
  <view class="cy-page">
    <cy-nav-bar title="我的攻略" />

    <scroll-view scroll-y class="cy-list-scroll">
      <view v-if="list.length === 0" class="cy-empty">还没有生成过方案，去出游 Tab 试试吧</view>

      <view v-for="item in list" :key="item.no" class="cy-card" @tap="viewPlan(item)">
        <view class="cy-card-meta">
          <text class="cy-no">{{ item.no }}</text>
          <text class="cy-date">{{ formatDate(item.createdAt) }}</text>
        </view>
        <text class="cy-plan-title">{{ item.title }}</text>
        <text class="cy-summary">{{ item.summary }}</text>
        <view class="cy-pills">
          <text class="cy-pill">用时 {{ item.totalTime }}</text>
          <text class="cy-pill">预算 {{ item.totalBudget }}</text>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getPlanHistory } from '../../api/storage.js'
import CyNavBar from '../../components/cy/cy-nav-bar.vue'

const list = ref([])

onMounted(() => {
  list.value = getPlanHistory()
})

function viewPlan(item) {
  uni.setStorageSync('lastPlan', item)
  uni.navigateTo({ url: `/pages/result/result?no=${encodeURIComponent(item.no)}` })
}

function formatDate(ts) {
  if (!ts) return ''
  const d = new Date(ts)
  return `${d.getMonth() + 1}/${d.getDate()}`
}
</script>

<style lang="scss">
@import '../../uni.scss';

.cy-page {
  min-height: 100vh;
  background: $cy-bg;
  font-family: "PingFang SC", "HarmonyOS Sans SC", "Noto Sans SC", -apple-system, system-ui, sans-serif;
}

.cy-list-scroll { padding: 24rpx; box-sizing: border-box; }

.cy-empty {
  display: block;
  color: $cy-muted;
  font-size: 26rpx;
  text-align: center;
  margin-top: 80rpx;
}

.cy-card {
  background: $cy-card;
  border-radius: 24rpx;
  padding: 28rpx;
  margin-bottom: 20rpx;
  box-shadow: $cy-shadow;
}

.cy-card-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12rpx;
}

.cy-no   { font-size: 20rpx; color: $cy-green; font-weight: 700; letter-spacing: 1rpx; }
.cy-date { font-size: 20rpx; color: $cy-muted; }

.cy-plan-title {
  display: block;
  font-size: 32rpx;
  font-weight: 800;
  color: $cy-text;
  margin-bottom: 10rpx;
}

.cy-summary {
  display: block;
  font-size: 26rpx;
  color: $cy-text-sub;
  line-height: 1.5;
  margin-bottom: 16rpx;
}

.cy-pills { display: flex; gap: 12rpx; }

.cy-pill {
  font-size: 22rpx;
  color: $cy-muted;
  background: $cy-bg;
  padding: 6rpx 16rpx;
  border-radius: 9999rpx;
}
</style>
