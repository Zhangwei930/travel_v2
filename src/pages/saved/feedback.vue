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
      <view v-if="loading" class="empty mono">加载中…</view>
      <view v-else-if="errored" class="empty mono">加载失败，请稍后重试</view>
      <view v-else-if="list.length === 0" class="empty mono">还没有反馈过，去攻略页点 👍 / 💬 试试</view>

      <view v-for="item in list" :key="item.id" class="card">
        <view class="card-meta">
          <text class="kind mono" :class="{ useful: item.useful }">
            {{ item.useful ? '👍 有用' : '💬 反馈' }}
          </text>
          <text class="date mono">{{ formatDate(item.created_at) }}</text>
        </view>
        <text v-if="item.target_label" class="target serif">{{ item.target_label }}</text>
        <text v-if="item.content" class="content">{{ item.content }}</text>
        <view v-if="item.status" class="status-row">
          <text class="status-chip" :class="'status-' + item.status">{{ statusLabel(item.status) }}</text>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../../api/mock.js'

const statusBarHeight = ref(44)
const list    = ref([])
const loading = ref(true)
const errored = ref(false)

onMounted(async () => {
  try { statusBarHeight.value = uni.getSystemInfoSync().statusBarHeight || 44 } catch (_) {}
  try {
    const res = await api.getFeedbackList()
    list.value = Array.isArray(res) ? res : (res?.items ?? [])
  } catch (_) {
    errored.value = true
  } finally {
    loading.value = false
  }
})

function goBack() { uni.navigateBack() }

function formatDate(ts) {
  if (!ts) return ''
  const d = new Date(typeof ts === 'number' ? ts : Date.parse(ts))
  if (Number.isNaN(d.getTime())) return ''
  return `${d.getMonth() + 1}/${d.getDate()}`
}

function statusLabel(s) {
  return { pending: '待处理', accepted: '已采纳', rejected: '已驳回' }[s] || s
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

.card { background: $z-card; border-radius: $radius-card; padding: 24rpx; margin-bottom: 16rpx; }
.card-meta { display: flex; justify-content: space-between; margin-bottom: 12rpx; }
.kind { font-family: $mono; font-size: $font-mono; color: $z-muted;
  &.useful { color: $z-accent; }
}
.date { font-family: $mono; font-size: $font-mono; color: $z-muted; }
.target { display: block; font-family: $serif; font-size: 28rpx; color: $z-text; margin-bottom: 8rpx; }
.content { display: block; font-size: $font-body; color: $z-text2; line-height: 1.5; margin-bottom: 12rpx; }
.status-row { display: flex; }
.status-chip { font-size: $font-xs; padding: 4rpx 14rpx; border-radius: $radius-tag; background: $z-bg; color: $z-muted;
  &.status-accepted { background: rgba(79, 209, 197, 0.15); color: $z-primary-l; }
  &.status-rejected { background: rgba(236, 75, 133, 0.12); color: $z-pink; }
}
</style>
