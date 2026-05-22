<template>
  <view class="page">
    <!-- Header -->
    <view class="header" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="header-inner">
        <text class="back" @tap="goBack">←</text>
        <text class="title serif">知识库审核</text>
        <text class="count mono">{{ list.length }} 条待审核</text>
      </view>
    </view>

    <!-- Token 未设置提示 -->
    <view v-if="!token" class="token-gate">
      <text class="gate-label">请输入管理员 Token</text>
      <input class="token-input" v-model="tokenInput" placeholder="X-Admin-Token" password />
      <view class="btn-confirm" @tap="saveToken">确认</view>
    </view>

    <!-- 列表 -->
    <scroll-view v-else scroll-y class="list-scroll">
      <view v-if="loading" class="empty-tip mono">加载中…</view>
      <view v-else-if="list.length === 0" class="empty-tip mono">暂无待审核记录</view>

      <view v-for="item in list" :key="item.id" class="card">
        <view class="card-meta mono">
          <text class="risk" :class="'risk-' + riskClass(item.risk_level)">
            {{ item.risk_level }}风险
          </text>
          <text class="cat">{{ item.category }}</text>
          <text class="time">{{ formatTime(item.created_at) }}</text>
        </view>

        <text class="question serif">{{ item.question }}</text>
        <text class="answer">{{ item.generated_answer }}</text>

        <view v-if="item.source_urls?.length" class="urls">
          <text class="url-label mono">来源：</text>
          <text v-for="(u, i) in item.source_urls.slice(0, 2)" :key="i" class="url">{{ u }}</text>
        </view>

        <view class="actions">
          <view class="btn approve" @tap="review(item.id, 'approved')">✓ 通过</view>
          <view class="btn reject" @tap="review(item.id, 'rejected')">✕ 拒绝</view>
          <view class="btn update" @tap="review(item.id, 'needs_update')">✎ 待修改</view>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { request } from '@/api/request.js'

const statusBarHeight = ref(0)
const token = ref('')
const tokenInput = ref('')
const list = ref([])
const loading = ref(false)

onMounted(() => {
  const info = uni.getSystemInfoSync()
  statusBarHeight.value = info.statusBarHeight || 0
  token.value = uni.getStorageSync('admin_token') || ''
  if (token.value) loadList()
})

function saveToken() {
  if (!tokenInput.value.trim()) return
  token.value = tokenInput.value.trim()
  uni.setStorageSync('admin_token', token.value)
  loadList()
}

async function loadList() {
  loading.value = true
  try {
    list.value = await request('/api/admin/kb/pending?status=pending', {
      header: { 'X-Admin-Token': token.value },
    })
  } catch (e) {
    uni.showToast({ title: 'Token 无效或请求失败', icon: 'none' })
    token.value = ''
    uni.removeStorageSync('admin_token')
  } finally {
    loading.value = false
  }
}

async function review(id, status) {
  try {
    await request('/api/admin/kb/approve', {
      method: 'POST',
      data: { id, status },
      header: { 'X-Admin-Token': token.value },
    })
    list.value = list.value.filter(i => i.id !== id)
    uni.showToast({ title: status === 'approved' ? '已通过' : '已处理', icon: 'success' })
  } catch {
    uni.showToast({ title: '操作失败', icon: 'none' })
  }
}

function riskClass(level) {
  return level === '高' ? 'high' : level === '中' ? 'mid' : 'low'
}

function formatTime(iso) {
  if (!iso) return ''
  return iso.slice(0, 16).replace('T', ' ')
}

function goBack() {
  uni.navigateBack()
}
</script>

<style lang="scss" scoped>
@import '@/uni.scss';

.page { min-height: 100vh; background: $z-bg; }

.header {
  background: $z-card;
  border-bottom: 1rpx solid $z-border;
  padding-bottom: 24rpx;

  &-inner {
    display: flex;
    align-items: center;
    padding: 16rpx 32rpx 0;
    gap: 16rpx;
  }
}

.back { font-size: 36rpx; color: $z-accent; padding: 8rpx; }
.title { font-size: 36rpx; font-family: $serif; color: $z-text; flex: 1; }
.count { font-size: $font-mono; color: $z-muted; font-family: $mono; }

/* token gate */
.token-gate {
  margin: 80rpx 40rpx 0;
  display: flex; flex-direction: column; gap: 24rpx;
}
.gate-label { font-size: 28rpx; color: $z-text; }
.token-input {
  border: 1rpx solid $z-border;
  border-radius: $radius-card;
  padding: 20rpx 24rpx;
  font-size: 28rpx;
  background: $z-card;
}
.btn-confirm {
  background: $z-accent;
  color: #fff;
  text-align: center;
  padding: 24rpx;
  border-radius: $radius-card;
  font-size: 30rpx;
}

/* list */
.list-scroll { height: calc(100vh - 120rpx); padding: 24rpx 24rpx 40rpx; box-sizing: border-box; }
.empty-tip { color: $z-muted; font-family: $mono; font-size: $font-mono; text-align: center; margin-top: 80rpx; }

.card {
  background: $z-card;
  border-radius: $radius-card;
  padding: 28rpx;
  margin-bottom: 24rpx;
}

.card-meta {
  display: flex; align-items: center; gap: 16rpx;
  font-family: $mono; font-size: $font-mono;
  margin-bottom: 16rpx;
}
.risk { padding: 4rpx 12rpx; border-radius: 8rpx; font-size: 20rpx; }
.risk-high { background: #FEE2E2; color: #DC2626; }
.risk-mid  { background: #FEF3C7; color: #D97706; }
.risk-low  { background: #D1FAE5; color: #059669; }
.cat, .time { color: $z-muted; }

.question {
  display: block;
  font-family: $serif;
  font-size: 32rpx;
  color: $z-text;
  margin-bottom: 16rpx;
}
.answer {
  display: block;
  font-size: 28rpx;
  color: $z-text2;
  line-height: 1.6;
  margin-bottom: 20rpx;
}

.urls { margin-bottom: 20rpx; }
.url-label { font-family: $mono; font-size: $font-mono; color: $z-muted; }
.url {
  display: block;
  font-size: 22rpx;
  color: $z-accent;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-top: 4rpx;
}

.actions { display: flex; gap: 16rpx; }
.btn {
  flex: 1; text-align: center; padding: 16rpx 0;
  border-radius: $radius-card; font-size: 26rpx;
  &.approve { background: $z-accent; color: #fff; }
  &.reject  { background: #FEE2E2; color: #DC2626; }
  &.update  { background: #F3F4F6; color: $z-text; }
}
</style>
