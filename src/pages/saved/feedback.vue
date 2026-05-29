<template>
  <view class="cy-page">
    <cy-nav-bar title="我的反馈" />

    <!-- KB 流程卡 -->
    <view class="cy-kb-banner">
      <text class="cy-kb-title">反馈如何进入知识库</text>
      <view class="cy-step-row">
        <view class="cy-step">
          <text class="cy-step-no">01</text>
          <text class="cy-step-label">你提交</text>
        </view>
        <text class="cy-step-arrow">→</text>
        <view class="cy-step">
          <text class="cy-step-no">02</text>
          <text class="cy-step-label">人工审核</text>
        </view>
        <text class="cy-step-arrow">→</text>
        <view class="cy-step">
          <text class="cy-step-no">03</text>
          <text class="cy-step-label">入库/驳回</text>
        </view>
        <text class="cy-step-arrow">→</text>
        <view class="cy-step">
          <text class="cy-step-no">04</text>
          <text class="cy-step-label">推荐更准</text>
        </view>
      </view>
    </view>

    <scroll-view scroll-y class="cy-list-scroll">
      <view v-if="loading" class="cy-empty">加载中…</view>
      <view v-else-if="errored" class="cy-empty">加载失败，请稍后重试</view>
      <view v-else-if="list.length === 0" class="cy-empty-card">
        <text class="cy-empty-title">还没有反馈过</text>
        <text class="cy-empty-sub">在地点详情或攻略页提交有用或反馈，内容会进入知识库审核队列。</text>
      </view>

      <view v-for="item in list" :key="item.id" class="cy-card">
        <view class="cy-card-meta">
          <text class="cy-kind" :class="{ useful: item.useful }">
            {{ item.useful ? '有用' : '反馈' }}
          </text>
          <text class="cy-date">{{ formatDate(item.created_at) }}</text>
        </view>
        <text v-if="item.target_label" class="cy-target">{{ item.target_label }}</text>
        <text v-if="item.content" class="cy-content">{{ item.content }}</text>

        <view class="cy-card-status">
          <view
            v-for="phase in phases(item.status)"
            :key="phase.id"
            class="cy-phase"
            :class="{ active: phase.active, current: phase.current }"
          >
            <view class="cy-phase-dot" />
            <text class="cy-phase-label">{{ phase.label }}</text>
          </view>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../../api/index.js'
import CyNavBar from '../../components/cy/cy-nav-bar.vue'

const list    = ref([])
const loading = ref(true)
const errored = ref(false)

onMounted(async () => {
  try {
    const res = await api.getFeedbackList()
    list.value = Array.isArray(res) ? res : (res?.items ?? [])
  } catch (_) {
    errored.value = true
  } finally {
    loading.value = false
  }
})

function formatDate(ts) {
  if (!ts) return ''
  const d = new Date(typeof ts === 'number' ? ts : Date.parse(ts))
  if (Number.isNaN(d.getTime())) return ''
  return `${d.getMonth() + 1}/${d.getDate()}`
}

function phases(status) {
  const map = {
    pending:   { stage: 1, terminal: false },
    reviewing: { stage: 2, terminal: false },
    accepted:  { stage: 3, terminal: true, label: '已入库' },
    rejected:  { stage: 3, terminal: true, label: '已驳回', failed: true },
    applied:   { stage: 4, terminal: true, label: '已生效' },
  }
  const meta = map[status] || map.pending
  return [
    { id: 1, label: '已提交', active: meta.stage >= 1, current: meta.stage === 1 },
    { id: 2, label: '审核中', active: meta.stage >= 2, current: meta.stage === 2 },
    { id: 3, label: meta.failed ? '已驳回' : '已入库', active: meta.stage >= 3, current: meta.stage === 3 && !meta.terminal },
    { id: 4, label: '已生效', active: meta.stage >= 4, current: meta.stage === 4 },
  ]
}
</script>

<style lang="scss">
@import '../../uni.scss';

.cy-page {
  min-height: 100vh;
  background: $cy-bg;
  font-family: "PingFang SC", "HarmonyOS Sans SC", "Noto Sans SC", -apple-system, system-ui, sans-serif;
}

// KB banner
.cy-kb-banner {
  margin: 20rpx 24rpx 0;
  background: $cy-card;
  border-radius: 24rpx;
  padding: 24rpx;
  box-shadow: $cy-shadow;
}

.cy-kb-title {
  display: block;
  font-size: 26rpx;
  font-weight: 800;
  color: $cy-text;
  margin-bottom: 18rpx;
}

.cy-step-row {
  display: flex;
  align-items: center;
  gap: 6rpx;
}

.cy-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6rpx;
  flex: 1;
}

.cy-step-no    { font-size: 18rpx; color: $cy-green; font-weight: 800; letter-spacing: 1rpx; }
.cy-step-label { font-size: 19rpx; color: $cy-text-sub; text-align: center; }
.cy-step-arrow { color: $cy-muted; font-size: 20rpx; flex-shrink: 0; }

// List
.cy-list-scroll { padding: 20rpx 24rpx 32rpx; box-sizing: border-box; }

.cy-empty {
  display: block;
  color: $cy-muted;
  font-size: 26rpx;
  text-align: center;
  margin-top: 60rpx;
}

.cy-empty-card {
  margin-top: 24rpx;
  background: $cy-card;
  border-radius: 24rpx;
  padding: 36rpx 28rpx;
  text-align: center;
  box-shadow: $cy-shadow;
}

.cy-empty-title {
  display: block;
  font-size: 28rpx;
  font-weight: 800;
  color: $cy-text;
  margin-bottom: 10rpx;
}

.cy-empty-sub {
  display: block;
  font-size: 24rpx;
  color: $cy-muted;
  line-height: 1.5;
}

.cy-card {
  background: $cy-card;
  border-radius: 24rpx;
  padding: 24rpx;
  margin-bottom: 16rpx;
  box-shadow: $cy-shadow;
}

.cy-card-meta { display: flex; justify-content: space-between; margin-bottom: 10rpx; }
.cy-kind      { font-size: 22rpx; color: $cy-muted; &.useful { color: $cy-green; } }
.cy-date      { font-size: 22rpx; color: $cy-muted; }
.cy-target    { display: block; font-size: 28rpx; font-weight: 800; color: $cy-text; margin-bottom: 6rpx; }
.cy-content   { display: block; font-size: 24rpx; color: $cy-text-sub; line-height: 1.55; margin-bottom: 14rpx; }

// 4-step progress
.cy-card-status {
  display: flex;
  align-items: center;
  padding-top: 14rpx;
  border-top: 1rpx dashed $cy-border;
  margin-top: 4rpx;
}

.cy-phase {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4rpx;
  opacity: 0.4;

  &.active { opacity: 1; }
}

.cy-phase-dot {
  width: 14rpx;
  height: 14rpx;
  border-radius: 7rpx;
  background: $cy-muted;

  .cy-phase.active & { background: $cy-green; }
  .cy-phase.current & { background: $cy-green; box-shadow: 0 0 0 4rpx $cy-green-l; }
}

.cy-phase-label {
  font-size: 18rpx;
  color: $cy-muted;

  .cy-phase.active & { color: $cy-text-sub; }
}
</style>
