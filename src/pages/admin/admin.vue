<template>
  <view class="page">
    <!-- Header -->
    <view class="header" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="header-inner">
        <text class="back" @tap="goBack">←</text>
        <text class="title serif">{{ tab === 'kb' ? '知识库审核' : '装备清单' }}</text>
        <text class="count mono">
          {{ tab === 'kb' ? `${list.length} 条待审核` : `${gear.length} 个场景` }}
        </text>
      </view>
      <view v-if="token" class="tabs">
        <view class="tab" :class="{ active: tab === 'kb' }" @tap="switchTab('kb')">知识审核</view>
        <view class="tab" :class="{ active: tab === 'gear' }" @tap="switchTab('gear')">装备清单</view>
      </view>
    </view>

    <!-- Token 未设置提示 -->
    <view v-if="!token" class="token-gate">
      <text class="gate-label">请输入管理员 Token</text>
      <input class="token-input" v-model="tokenInput" placeholder="X-Admin-Token" password />
      <view class="btn-confirm" @tap="saveToken">确认</view>
    </view>

    <!-- 知识库审核列表 -->
    <scroll-view v-else-if="tab === 'kb'" scroll-y class="list-scroll">
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

        <view v-if="analysisMap[item.id]" class="ai-box">
          <view class="ai-head">
            <text class="ai-title">AI分析</text>
            <text class="ai-status">{{ statusLabel(analysisMap[item.id].suggested_status) }} · 置信度{{ analysisMap[item.id].confidence }}</text>
          </view>
          <text
            v-for="issue in analysisMap[item.id].issues"
            :key="issue"
            class="ai-issue"
          >· {{ issue }}</text>
          <text v-if="analysisMap[item.id].revised_answer" class="ai-answer">{{ analysisMap[item.id].revised_answer }}</text>
        </view>

        <view v-if="item.source_urls?.length" class="urls">
          <text class="url-label mono">来源：</text>
          <text v-for="(u, i) in item.source_urls.slice(0, 2)" :key="i" class="url">{{ u }}</text>
        </view>

        <view class="actions">
          <view class="btn ai" @tap="analyze(item)">AI分析</view>
          <view class="btn approve" @tap="review(item, 'approved')">✓ 通过</view>
          <view class="btn reject" @tap="review(item, 'rejected')">✕ 拒绝</view>
          <view class="btn update" @tap="review(item, 'needs_update')">✎ 待修改</view>
        </view>
      </view>
    </scroll-view>

    <!-- 装备清单编辑 -->
    <scroll-view v-else scroll-y class="list-scroll">
      <view v-if="loading" class="empty-tip mono">加载中…</view>
      <view v-for="g in gear" :key="g.scene_id" class="card gear-card">
        <view class="gear-head">
          <text class="gear-icon">{{ g.icon }}</text>
          <text class="gear-label serif">{{ g.label }}</text>
          <text class="gear-id mono">{{ g.scene_id }}</text>
          <text class="gear-count mono">{{ (drafts[g.scene_id] || []).length }} 件</text>
        </view>
        <!-- 每行一件装备 -->
        <textarea
          class="gear-area"
          :value="(drafts[g.scene_id] || []).join('\n')"
          @input="onGearInput(g.scene_id, $event)"
          placeholder="每行一件装备，留空则该场景无装备"
          :auto-height="true"
        />
        <view class="gear-actions">
          <view class="btn reject" @tap="resetGear(g.scene_id)">还原</view>
          <view class="btn approve" @tap="saveGear(g.scene_id)">保存</view>
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
const gear = ref([])             // [{scene_id, label, icon, items}, ...]
const drafts = ref({})           // scene_id -> 编辑中的数组（未保存）
const analysisMap = ref({})      // pending id -> AI analysis
const loading = ref(false)
const tab = ref('kb')            // 'kb' | 'gear'

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

function switchTab(t) {
  if (tab.value === t) return
  tab.value = t
  if (t === 'kb') loadList()
  else loadGear()
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

async function loadGear() {
  loading.value = true
  try {
    const list = await request('/api/admin/gear', {
      header: { 'X-Admin-Token': token.value },
    })
    gear.value = list
    drafts.value = Object.fromEntries(list.map(g => [g.scene_id, [...g.items]]))
  } catch (e) {
    uni.showToast({ title: 'Token 无效或请求失败', icon: 'none' })
    token.value = ''
    uni.removeStorageSync('admin_token')
  } finally {
    loading.value = false
  }
}

function onGearInput(sceneId, e) {
  const text = e.detail?.value ?? ''
  drafts.value[sceneId] = text.split('\n').map(s => s.trim()).filter(Boolean)
}

function resetGear(sceneId) {
  const original = gear.value.find(g => g.scene_id === sceneId)
  if (original) drafts.value[sceneId] = [...original.items]
}

async function saveGear(sceneId) {
  const items = drafts.value[sceneId] || []
  try {
    await request(`/api/admin/gear/${encodeURIComponent(sceneId)}`, {
      method: 'PUT',
      data: { items },
      header: { 'X-Admin-Token': token.value },
    })
    // 更新本地 source of truth
    const g = gear.value.find(x => x.scene_id === sceneId)
    if (g) g.items = [...items]
    uni.showToast({ title: `已保存（${items.length} 件）`, icon: 'success' })
  } catch (e) {
    uni.showToast({ title: '保存失败', icon: 'none' })
  }
}

async function analyze(item) {
  try {
    const res = await request('/api/admin/kb/analyze', {
      method: 'POST',
      data: { id: item.id },
      header: { 'X-Admin-Token': token.value },
    })
    analysisMap.value = { ...analysisMap.value, [item.id]: res }
    uni.showToast({ title: 'AI分析完成', icon: 'success' })
  } catch {
    uni.showToast({ title: 'AI分析失败', icon: 'none' })
  }
}

async function review(item, status) {
  const analysis = analysisMap.value[item.id]
  const generatedAnswer = analysis?.revised_answer || item.generated_answer
  try {
    await request('/api/admin/kb/approve', {
      method: 'POST',
      data: { id: item.id, status, generated_answer: generatedAnswer },
      header: { 'X-Admin-Token': token.value },
    })
    list.value = list.value.filter(i => i.id !== item.id)
    uni.showToast({ title: status === 'approved' ? '已通过' : '已处理', icon: 'success' })
  } catch {
    uni.showToast({ title: '操作失败', icon: 'none' })
  }
}

function statusLabel(status) {
  return {
    approved: '建议通过',
    rejected: '建议拒绝',
    needs_update: '建议修改',
  }[status] || '建议复核'
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
  color: $z-card;
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
.risk-high { background: $z-danger-bg; color: $z-danger; }
.risk-mid  { background: $z-warning-bg; color: $z-warning; }
.risk-low  { background: $z-success-bg; color: $z-success-d; }
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

.ai-box {
  background: $z-neutral-bg;
  border-radius: $radius-card;
  padding: 20rpx;
  margin-bottom: 20rpx;
}
.ai-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16rpx;
  margin-bottom: 10rpx;
}
.ai-title { font-size: 24rpx; font-weight: 800; color: $z-accent; }
.ai-status { font-size: 22rpx; color: $z-muted; }
.ai-issue {
  display: block;
  font-size: 24rpx;
  color: $z-text2;
  line-height: 1.45;
}
.ai-answer {
  display: block;
  margin-top: 12rpx;
  font-size: 24rpx;
  color: $z-text;
  line-height: 1.5;
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
  &.ai      { background: $z-success-bg; color: $z-success-d; }
  &.approve { background: $z-accent; color: $z-card; }
  &.reject  { background: $z-danger-bg; color: $z-danger; }
  &.update  { background: $z-neutral-bg; color: $z-text; }
}

/* Tab 切换 */
.tabs {
  display: flex;
  gap: 0;
  padding: 0 32rpx;
  margin-top: 16rpx;
}
.tab {
  flex: 1;
  text-align: center;
  padding: 16rpx 0;
  font-size: 26rpx;
  color: $z-muted;
  border-bottom: 3rpx solid transparent;
  &.active {
    color: $z-accent;
    border-bottom-color: $z-accent;
    font-weight: 700;
  }
}

/* 装备清单卡片 */
.gear-card { padding: 24rpx 28rpx; }
.gear-head {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 16rpx;
}
.gear-icon { font-size: 36rpx; }
.gear-label { font-size: 30rpx; color: $z-text; flex: 1; }
.gear-id { font-size: 20rpx; color: $z-muted; }
.gear-count { font-size: 22rpx; color: $z-muted; }
.gear-area {
  width: 100%;
  min-height: 160rpx;
  padding: 16rpx 20rpx;
  border: 1rpx solid $z-border;
  border-radius: $radius-card;
  background: $z-bg;
  font-size: 26rpx;
  color: $z-text;
  line-height: 1.6;
  box-sizing: border-box;
  margin-bottom: 16rpx;
}
.gear-actions { display: flex; gap: 16rpx; }
</style>
