<template>
  <view class="cy-page">
    <cy-nav-bar title="我的攻略" />

    <scroll-view scroll-y class="cy-list-scroll">
      <view v-if="list.length === 0" class="cy-empty">还没有生成过方案，去出游 Tab 试试吧</view>

      <view v-if="list.length" class="cy-list-head">
        <text class="cy-count">共 {{ list.length }} 条</text>
        <text class="cy-clear" @tap="clearAll">清空</text>
      </view>

      <view v-for="item in list" :key="item.no" class="cy-card" @tap="viewPlan(item)">
        <view class="cy-card-meta">
          <text class="cy-no">{{ item.no }}</text>
          <view class="cy-meta-right">
            <text class="cy-date">{{ formatDate(item.createdAt) }}</text>
            <text class="cy-del-btn" @tap.stop="removeItem(item)">删除</text>
          </view>
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
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getPlanHistory, removePlanHistory, clearPlanHistory } from '../../api/storage.js'
import CyNavBar from '../../components/cy/cy-nav-bar.vue'

const list = ref([])

onShow(() => {
  list.value = getPlanHistory()
})

function removeItem(item) {
  uni.showModal({
    title: '删除攻略', content: `确定删除「${item.title}」？`, confirmColor: '#e25b4b',
    success: (r) => {
      if (!r.confirm) return
      removePlanHistory(item.no)
      list.value = getPlanHistory()
      uni.showToast({ title: '已删除', icon: 'none' })
    },
  })
}
function clearAll() {
  uni.showModal({
    title: '清空攻略', content: '确定清空全部攻略记录？', confirmColor: '#e25b4b',
    success: (r) => {
      if (!r.confirm) return
      clearPlanHistory()
      list.value = []
      uni.showToast({ title: '已清空', icon: 'none' })
    },
  })
}

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

.cy-list-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 8rpx 16rpx;
}
.cy-count { font-size: 24rpx; color: $cy-muted; }
.cy-clear { font-size: 26rpx; color: #e25b4b; font-weight: 600; }
.cy-meta-right { display: flex; align-items: center; gap: 18rpx; }
.cy-del-btn { font-size: 22rpx; color: #e25b4b; font-weight: 600; }

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
