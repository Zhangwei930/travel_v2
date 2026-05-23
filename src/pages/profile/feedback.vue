<template>
  <view class="page">
    <view class="header" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="header-inner">
        <text class="back" @tap="goBack">←</text>
        <text class="title serif">我的反馈</text>
        <text class="count mono">{{ list.length }} 条</text>
      </view>
    </view>

    <scroll-view scroll-y class="list-scroll">
      <view v-if="list.length === 0" class="empty">
        <text class="empty-icon">💬</text>
        <text class="empty-text mono">还没有提交过反馈</text>
        <text class="empty-hint">在攻略结果页点「👍 有用」或「💬 反馈」即可记录</text>
      </view>

      <view v-for="(item, i) in list" :key="i" class="card">
        <view class="card-top">
          <view class="badge" :class="item.useful ? 'good' : 'neutral'">
            <text>{{ item.useful ? '👍 有用' : '💬 反馈' }}</text>
          </view>
          <text class="date mono">{{ formatDate(item.createdAt) }}</text>
        </view>
        <text class="target">{{ labelTarget(item) }}</text>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getFeedbacks } from '../../api/storage.js'

const statusBarHeight = ref(44)
const list = ref([])

onMounted(() => {
  try { statusBarHeight.value = uni.getSystemInfoSync().statusBarHeight || 44 } catch (_) {}
  list.value = getFeedbacks()
})

function goBack() { uni.navigateBack() }

function labelTarget(item) {
  if (item.target_type === 'plan' && item.target_id) return `攻略方案 · ${item.target_id}`
  if (item.target_type === 'qa') return 'AI 问答'
  return '出游攻略'
}

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
  margin-top: 100rpx;
  gap: 18rpx;
}
.empty-icon { font-size: 72rpx; }
.empty-text { color: $z-muted; font-family: $mono; font-size: $font-mono; }
.empty-hint { font-size: $font-sm; color: $z-muted; text-align: center; padding: 0 40rpx; line-height: 1.5; }

.card {
  background: $z-card;
  border-radius: $radius-card;
  padding: 28rpx;
  margin-bottom: 20rpx;
}

.card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14rpx;
}

.badge {
  display: inline-block;
  padding: 6rpx 18rpx;
  border-radius: $radius-pill;
  font-size: $font-sm;
  font-weight: 700;

  &.good    { background: rgba(34, 197, 94, 0.12); color: #16A34A; }
  &.neutral { background: rgba(13, 79, 74, 0.08);  color: #0D4F4A; }
}

.date   { font-family: $mono; font-size: $font-mono; color: $z-muted; }
.target { display: block; font-size: $font-body; color: $z-text2; line-height: 1.5; }
</style>
