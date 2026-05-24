<template>
  <view class="page">
    <view class="header" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="header-inner">
        <text class="back" @tap="goBack">←</text>
        <view class="title-wrap">
          <text class="kicker mono">§ FEEDBACK · KNOWLEDGE</text>
          <text class="title serif">我的反馈与贡献</text>
        </view>
        <text class="count mono">{{ list.length }} 条</text>
      </view>
    </view>

    <view class="kb-loop">
      <text class="kb-loop-title serif">反馈如何进入知识库</text>
      <view class="step-row">
        <view class="step">
          <text class="step-no mono">01</text>
          <text class="step-label">你提交</text>
        </view>
        <text class="step-arrow">→</text>
        <view class="step">
          <text class="step-no mono">02</text>
          <text class="step-label">人工审核</text>
        </view>
        <text class="step-arrow">→</text>
        <view class="step">
          <text class="step-no mono">03</text>
          <text class="step-label">入库 / 驳回</text>
        </view>
        <text class="step-arrow">→</text>
        <view class="step">
          <text class="step-no mono">04</text>
          <text class="step-label">推荐更准</text>
        </view>
      </view>
    </view>

    <scroll-view scroll-y class="list-scroll">
      <view v-if="loading" class="empty mono">加载中…</view>
      <view v-else-if="errored" class="empty mono">加载失败，请稍后重试</view>
      <view v-else-if="list.length === 0" class="empty-card">
        <text class="empty-title serif">还没有反馈过</text>
        <text class="empty-sub">在地点详情或攻略页点 👍 / 💬，反馈会进入知识库审核队列。</text>
      </view>

      <view v-for="item in list" :key="item.id" class="card">
        <view class="card-meta">
          <text class="kind mono" :class="{ useful: item.useful }">
            {{ item.useful ? '👍 有用' : '💬 反馈' }}
          </text>
          <text class="date mono">{{ formatDate(item.created_at) }}</text>
        </view>
        <text v-if="item.target_label" class="target serif">{{ item.target_label }}</text>
        <text v-if="item.content" class="content">{{ item.content }}</text>

        <view class="card-status">
          <view
            v-for="phase in phases(item.status)"
            :key="phase.id"
            class="phase"
            :class="{ active: phase.active, current: phase.current }"
          >
            <text class="phase-dot" />
            <text class="phase-label mono">{{ phase.label }}</text>
          </view>
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

// 4 步进度：提交 → 审核中 → 入库/驳回 → 已生效
function phases(status) {
  const map = {
    pending:  { stage: 1, terminal: false },
    reviewing:{ stage: 2, terminal: false },
    accepted: { stage: 3, terminal: true, label: '已入库' },
    rejected: { stage: 3, terminal: true, label: '已驳回', failed: true },
    applied:  { stage: 4, terminal: true, label: '已生效' },
  }
  const meta = map[status] || map.pending
  return [
    { id: 1, label: '已提交',  active: meta.stage >= 1, current: meta.stage === 1 },
    { id: 2, label: '审核中',  active: meta.stage >= 2, current: meta.stage === 2 },
    { id: 3, label: meta.failed ? '已驳回' : '已入库', active: meta.stage >= 3, current: meta.stage === 3 && !meta.terminal },
    { id: 4, label: '已生效',  active: meta.stage >= 4, current: meta.stage === 4 },
  ]
}
</script>

<style lang="scss" scoped>
@import '@/uni.scss';

.page { min-height: 100vh; background: $z-bg; }

.header {
  background: $z-card;
  border-bottom: 1rpx solid $z-border;
  padding-bottom: 20rpx;
  &-inner { display: flex; align-items: center; padding: 16rpx 32rpx 0; gap: 16rpx; }
}
.back { font-size: 36rpx; color: $z-primary; padding: 8rpx; }
.title-wrap { flex: 1; min-width: 0; }
.kicker { display: block; font-size: 18rpx; color: $z-muted; letter-spacing: 2rpx; margin-bottom: 2rpx; }
.title { display: block; font-size: 34rpx; font-family: $serif; color: $z-text; font-weight: 900; }
.count { font-size: $font-mono; color: $z-muted; font-family: $mono; }

// ── KB loop banner ──────────────────────────────────────────
.kb-loop {
  margin: 22rpx 28rpx 0;
  background: $z-card;
  border-radius: 18rpx;
  padding: 22rpx 22rpx 20rpx;
  box-shadow: 0 2rpx 10rpx rgba(13, 79, 74, 0.05);
}

.kb-loop-title {
  display: block;
  font-size: 24rpx;
  color: $z-text;
  font-weight: 800;
  margin-bottom: 16rpx;
}

.step-row {
  display: flex;
  align-items: center;
  gap: 6rpx;
  overflow: hidden;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6rpx;
  flex: 1;
  min-width: 0;
}

.step-no {
  font-size: 18rpx;
  color: $z-primary;
  font-weight: 800;
  letter-spacing: 1rpx;
}

.step-label {
  font-size: 19rpx;
  color: $z-text2;
  text-align: center;
}

.step-arrow {
  color: $z-muted;
  font-size: 20rpx;
  flex-shrink: 0;
}

// ── List ────────────────────────────────────────────────────
.list-scroll { padding: 22rpx 28rpx 32rpx; box-sizing: border-box; }
.empty { color: $z-muted; font-family: $mono; font-size: $font-mono; text-align: center; margin-top: 60rpx; display: block; }

.empty-card {
  margin-top: 24rpx;
  background: $z-card;
  border-radius: 18rpx;
  padding: 32rpx 28rpx;
  text-align: center;
  box-shadow: 0 2rpx 10rpx rgba(13, 79, 74, 0.05);
}

.empty-title {
  display: block;
  font-size: 28rpx;
  font-weight: 900;
  color: $z-text;
  margin-bottom: 10rpx;
}

.empty-sub {
  display: block;
  font-size: 22rpx;
  color: $z-muted;
  line-height: 1.5;
}

.card { background: $z-card; border-radius: 18rpx; padding: 22rpx; margin-bottom: 14rpx; box-shadow: 0 2rpx 10rpx rgba(13, 79, 74, 0.05); }
.card-meta { display: flex; justify-content: space-between; margin-bottom: 10rpx; }
.kind { font-family: $mono; font-size: $font-mono; color: $z-muted;
  &.useful { color: $z-primary; }
}
.date { font-family: $mono; font-size: $font-mono; color: $z-muted; }
.target { display: block; font-family: $serif; font-size: 26rpx; color: $z-text; font-weight: 800; margin-bottom: 6rpx; }
.content { display: block; font-size: 22rpx; color: $z-text2; line-height: 1.55; margin-bottom: 14rpx; }

// ── 4-step progress on each card ────────────────────────────
.card-status {
  display: flex;
  align-items: center;
  gap: 0;
  padding-top: 4rpx;
  border-top: 1rpx dashed $z-border;
  margin-top: 4rpx;
  padding: 12rpx 0 0;
}

.phase {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4rpx;
  opacity: 0.4;

  &.active { opacity: 1; }
}

.phase-dot {
  width: 14rpx;
  height: 14rpx;
  border-radius: 7rpx;
  background: $z-muted;

  .phase.active & { background: $z-primary; }
  .phase.current & { background: $z-accent; box-shadow: 0 0 0 4rpx rgba(255, 107, 53, 0.18); }
}

.phase-label {
  font-size: 18rpx;
  color: $z-muted;

  .phase.active & { color: $z-text2; }
}
</style>
