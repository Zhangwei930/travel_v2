<template>
  <view class="page">
    <view class="header" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="header-inner">
        <view class="back-btn" @tap="goBack">
          <svg xmlns="http://www.w3.org/2000/svg" width="9" height="16" viewBox="0 0 9 16">
            <path d="M7.5 1.5L2 8l5.5 6.5" stroke="#FF6B35" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
          </svg>
          <text class="back-text">返回</text>
        </view>
        <text class="title serif">我的攻略</text>
        <text class="count mono">{{ list.length }} 份</text>
      </view>
    </view>

    <scroll-view scroll-y class="list-scroll">
      <view v-if="list.length === 0" class="empty mono">还没有生成过方案，去首页试试吧</view>

      <view v-for="item in list" :key="item.no" class="card">
        <view class="card-top" @tap="viewPlan(item)">
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
        <view class="card-footer">
          <view class="del-btn" @tap="deletePlan(item.no)">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none">
              <path d="M3 6h18M8 6V4h8v2M19 6l-1 14H6L5 6" stroke="#C0392B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <text class="del-text">删除</text>
          </view>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getPlanHistory, removePlanHistory } from '../../api/storage.js'

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

function deletePlan(no) {
  uni.showModal({
    title: '删除攻略',
    content: '确定删除该方案吗？',
    confirmColor: '#C0392B',
    success: (res) => {
      if (res.confirm) {
        removePlanHistory(no)
        list.value = getPlanHistory()
      }
    },
  })
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

.back-btn {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 8rpx 4rpx;
}
.back-text { font-size: 28rpx; color: $z-accent; }

.title { font-size: 36rpx; font-family: $serif; color: $z-text; flex: 1; }
.count { font-size: $font-mono; color: $z-muted; font-family: $mono; }

.list-scroll { height: calc(100vh - 120rpx); padding: 24rpx; box-sizing: border-box; }
.empty { color: $z-muted; font-family: $mono; font-size: $font-mono; text-align: center; margin-top: 80rpx; display: block; }

.card {
  background: $z-card;
  border-radius: $radius-card;
  margin-bottom: 20rpx;
  overflow: hidden;
}
.card-top { padding: 28rpx 28rpx 16rpx; }
.card-footer {
  border-top: 1rpx solid $z-border;
  padding: 16rpx 28rpx;
  display: flex;
  justify-content: flex-end;
}

.card-meta { display: flex; justify-content: space-between; margin-bottom: 12rpx; }
.no { font-family: $mono; font-size: $font-mono; color: $z-accent; }
.date { font-family: $mono; font-size: $font-mono; color: $z-muted; }
.plan-title { display: block; font-family: $serif; font-size: 32rpx; color: $z-text; margin-bottom: 10rpx; }
.summary { display: block; font-size: $font-body; color: $z-text2; line-height: 1.5; margin-bottom: 16rpx; }
.pills { display: flex; gap: 12rpx; }
.pill { font-size: $font-xs; color: $z-muted; background: $z-bg; padding: 6rpx 16rpx; border-radius: $radius-tag; }

.del-btn {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 6rpx 12rpx;
}
.del-text { font-size: 24rpx; color: #C0392B; }
</style>
