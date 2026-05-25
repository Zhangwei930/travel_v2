<template>
  <view class="page">
    <!-- 无数据时的占位（onMounted 跳回前短暂显示） -->
    <view v-if="!plan" class="loading-state" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="back-btn-plain" @tap="goBack">←</view>
      <text class="loading-tip mono">加载中…</text>
    </view>

    <template v-if="plan">
    <!-- Header 深墨青渐变 -->
    <view class="header" :style="{ paddingTop: statusBarHeight + 'px' }">
      <!-- 操作行 -->
      <view class="header-actions">
        <view class="back-btn" @tap="goBack">
          <svg xmlns="http://www.w3.org/2000/svg" width="9" height="16" viewBox="0 0 9 16">
            <path d="M7.5 1.5L2 8l5.5 6.5" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
          </svg>
        </view>
        <view class="header-right-btns">
          <view class="icon-btn" @tap="toggleFav">
            <text>{{ saved ? '❤️' : '🤍' }}</text>
          </view>
          <view class="icon-btn" @tap="onShare">
            <text>📤</text>
          </view>
        </view>
      </view>

      <!-- 方案编号 -->
      <text class="plan-no mono">{{ plan.no }}</text>

      <!-- AI 徽章（AI 生成时显示） -->
      <view v-if="isGenerated" class="ai-badge">
        <text>✨ AI · 新方案</text>
      </view>

      <!-- 标题 -->
      <text class="plan-title serif">{{ plan.title }}</text>
      <text class="plan-summary">{{ plan.summary }}</text>

      <!-- 4 个数据胶囊 -->
      <view class="meta-pills">
        <view class="meta-pill" v-for="m in planMeta" :key="m.label">
          <text class="meta-icon">{{ m.icon }}</text>
          <text class="meta-val">{{ m.val }}</text>
        </view>
      </view>
    </view>

    <scroll-view scroll-y class="scroll-body" :show-scrollbar="false">
      <!-- 地图缩略图卡片 -->
      <view class="section">
        <view class="map-card">
          <view class="map-header">
            <text class="map-label">🗺 路线总览</text>
            <text class="map-meta mono">{{ mapStops.length }} 站</text>
          </view>
          <!-- 真实地图：渲染带坐标的 stop 为 marker -->
          <view v-if="mapStops.length" class="mini-map">
            <map
              :latitude="mapCenter.lat"
              :longitude="mapCenter.lng"
              :markers="mapMarkers"
              :include-points="mapPoints"
              :scale="13"
              class="real-map"
              show-location
            />
          </view>
          <view v-else class="mini-map-empty mono">暂无站点坐标</view>
        </view>
      </view>

      <!-- 数据源标签 -->
      <view class="section">
        <scroll-view scroll-x :show-scrollbar="false">
          <view class="sources-row">
            <view class="source-chip" v-for="s in plan.sources" :key="s.kind">
              <text class="source-kind mono">[{{ s.kind }}]</text>
              <text class="source-t">{{ s.t }}</text>
            </view>
          </view>
        </scroll-view>
      </view>

      <!-- §ITN 路线时间线 -->
      <view class="section">
        <z-section-header no="ITN" title="详细路线" sub="行程时间线" />
        <view class="timeline">
          <view v-for="(stop, i) in plan.stops" :key="stop.idx" class="stop-row">
            <!-- 左：编号 + 时间线 -->
            <view class="stop-left">
              <view class="stop-num-circle">
                <text class="serif">{{ String(i + 1).padStart(2, '0') }}</text>
              </view>
              <view v-if="i < plan.stops.length - 1" class="timeline-line" />
              <text class="arrive-time mono">{{ stop.arrive }}</text>
            </view>
            <!-- 右：内容卡 -->
            <view class="stop-card">
              <text class="stop-name serif">{{ stop.name }}</text>
              <text class="stop-meta">{{ stop.cat }} · {{ stop.transport }}</text>
              <text class="stop-stay">⏱ 停留 {{ stop.stay }}</text>

              <view class="why-block">
                <text class="why-label">💡 为什么选这里</text>
                <text class="why-text">{{ stop.reason }}</text>
              </view>

              <view class="headsup-block">
                <text class="headsup-label">⚠️ 注意事项</text>
                <text class="headsup-text">{{ stop.tip }}</text>
              </view>

              <view class="stop-footer">
                <text class="stop-budget">💰 {{ stop.budget }}</text>
                <text class="nav-btn" @tap="onNav(stop)">导航 →</text>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 备用方案 -->
      <view class="section">
        <view class="backup-card">
          <text class="backup-title">🔄 备用方案</text>
          <text class="backup-text">{{ plan.backup }}</text>
        </view>
      </view>

      <!-- 免责声明 -->
      <view class="section">
        <view class="disclaimer">
          <text class="disclaimer-text">ℹ️ {{ plan.disclaimer }}</text>
        </view>
      </view>
    </scroll-view>

    <!-- 反馈输入弹层 -->
    <view v-if="feedbackOpen" class="feedback-mask" @tap="closeFeedback">
      <view class="feedback-card" @tap.stop>
        <text class="feedback-title serif">💬 具体哪里不准确？</text>
        <text class="feedback-sub">告诉我们问题，会进入审核队列改进知识库</text>
        <textarea
          class="feedback-textarea"
          v-model="feedbackText"
          placeholder="比如：第 2 站停车场已关闭 / 票价不对 / 路线太长…"
          placeholder-style="color: #8B9594; font-size: 25rpx;"
          :maxlength="500"
          auto-height
        />
        <view class="feedback-actions">
          <view class="feedback-btn cancel" @tap="closeFeedback">取消</view>
          <view class="feedback-btn submit" :class="{ disabled: submitting }" @tap="submitFeedback">
            {{ submitting ? '提交中…' : '提交' }}
          </view>
        </view>
      </view>
    </view>

    <!-- 底部操作栏 -->
    <view class="bottom-bar" :style="{ paddingBottom: safeBottom }">
      <view class="bottom-btn outline" @tap="onFeedback(true)">👍 有用</view>
      <view class="bottom-btn outline" @tap="openFeedback">💬 反馈</view>
      <view class="bottom-btn primary flex2" @tap="onStart">🧭 开始出发</view>
    </view>
    </template>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { onLoad, onShareAppMessage, onShareTimeline } from '@dcloudio/uni-app'
import { api } from '../../api/mock.js'
import { addPlanHistory, toggleSavedPlan, isSavedPlan } from '../../api/storage.js'
import ZSectionHeader from '../../components/ZSectionHeader.vue'

const statusBarHeight = ref(44)
const safeBottom      = ref('18px')
const saved           = ref(false)

const plan = ref(null)

// 反馈表单
const feedbackOpen = ref(false)
const feedbackText = ref('')
const submitting   = ref(false)

// 路由参数：用 onLoad 钩子拿最稳。setup() 顶层 currentPage.options 在小程序里时机不可靠。
const routeQuery = ref({})
onLoad((options) => {
  if (options && typeof options === 'object') routeQuery.value = { ...options }
})
const isGenerated   = computed(() => String(routeQuery.value.generated || '') === '1')
const planNoFromUrl = computed(() => String(routeQuery.value.no || ''))

const planMeta = computed(() => plan.value ? [
  { icon: '⏱', val: plan.value.totalTime },
  { icon: '💰', val: plan.value.totalBudget },
  { icon: '👥', val: plan.value.people },
  { icon: '🌤', val: plan.value.weather },
] : [])
// 真实地图：从 plan.stops 中取出有坐标的 stop，转成 marker
const mapStops = computed(() =>
  (plan.value?.stops || []).filter(s => s.lat != null && s.lng != null)
)
const mapMarkers = computed(() => mapStops.value.map((s, i) => ({
  id: i + 1,
  latitude: Number(s.lat),
  longitude: Number(s.lng),
  title: s.name,
  // 微信小程序 marker 强制要求 width/height；不指定 iconPath 时使用默认气泡
  width: 32,
  height: 32,
  label: {
    content: String(i + 1),
    fontSize: 12,
    color: '#FFFFFF',
    bgColor: '#FF6B35',
    padding: 6,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#FFFFFF',
    anchorX: -10,
    anchorY: -36,
  },
  callout: {
    content: `${i + 1}. ${s.name || ''}`,
    fontSize: 12, padding: 6, borderRadius: 6,
    color: '#1A2E2C', bgColor: '#FFFFFF',
    display: 'BYCLICK',
  },
})))
const mapPoints = computed(() => mapStops.value.map(s => ({
  latitude: Number(s.lat), longitude: Number(s.lng),
})))
const mapCenter = computed(() => {
  const arr = mapStops.value
  if (!arr.length) return { lat: 30.6586, lng: 104.0648 }  // 成都市中心兜底
  const avg = (k) => arr.reduce((a, b) => a + Number(b[k]), 0) / arr.length
  return { lat: avg('lat'), lng: avg('lng') }
})

onMounted(async () => {
  try {
    const sys = uni.getSystemInfoSync()
    statusBarHeight.value = sys.statusBarHeight || 44
    safeBottom.value = Math.max(sys.safeAreaInsets?.bottom || 18, 18) + 'px'
  } catch (_) {}

  // 优先：URL 里的 plan_no → 后端拉取（支持刷新/深链/换设备）
  // 兜底：lastPlan 本地缓存（用户上一次生成的方案，离线可看）
  const isValid = (p) => p && p.no && p.title && Array.isArray(p.stops) && p.stops.length > 0

  const no = planNoFromUrl.value
  let loaded = null
  if (no) {
    try {
      const r = await api.getPlan(no)
      if (isValid(r)) loaded = r
    } catch (_) {}
  }
  if (!loaded) {
    try {
      const cached = uni.getStorageSync('lastPlan')
      if (isValid(cached) && (!no || cached.no === no)) {
        loaded = cached
      }
    } catch (_) {}
  }

  if (loaded) {
    plan.value = loaded
    try { addPlanHistory(loaded) } catch (e) { console.warn('addPlanHistory failed', e) }
    try { saved.value = isSavedPlan(loaded.no) } catch (e) { console.warn('isSavedPlan failed', e) }
  } else {
    console.warn('plan load failed: no URL param matched and no valid cache', { no })
    uni.showToast({ title: '攻略不存在或已过期，请重新生成', icon: 'none' })
    setTimeout(() => uni.navigateBack(), 1500)
  }
})

function goBack() { uni.navigateBack() }
function toggleFav() {
  if (!plan.value) return
  saved.value = toggleSavedPlan(plan.value)
  uni.showToast({ title: saved.value ? '已收藏' : '已取消收藏', icon: 'none' })
}
function onShare() {
  uni.showShareMenu({ withShareTicket: false, menus: ['shareAppMessage', 'shareTimeline'] })
}

onShareAppMessage(() => {
  const p = plan.value
  const cover = p?.stops?.find(s => s.img)?.img || ''
  return {
    title: p ? `${p.title}｜周密出游为你定制` : '周密出游帮我规划了一条路线',
    path: p?.no ? `/pages/result/result?no=${p.no}` : '/pages/index/index',
    imageUrl: cover,
  }
})

onShareTimeline(() => {
  const p = plan.value
  const cover = p?.stops?.find(s => s.img)?.img || ''
  return {
    title: p ? `${p.title}，${p.totalTime}·${p.totalBudget}` : '今天的出游路线来了',
    query: p?.no ? `no=${p.no}` : '',
    imageUrl: cover,
  }
})
function onNav(stop) {
  if (stop.lat && stop.lng) {
    uni.openLocation({ latitude: stop.lat, longitude: stop.lng, name: stop.name, address: stop.cat })
  } else {
    uni.showToast({ title: '暂无坐标，无法导航', icon: 'none' })
  }
}
async function onFeedback(useful) {
  if (!plan.value?.no) return
  try {
    const r = await api.sendFeedback({ target_type: 'plan', target_id: plan.value.no, useful })
    uni.showToast({ title: r?.message || '感谢反馈', icon: 'success' })
  } catch (e) {
    uni.showToast({ title: '反馈失败，请稍后重试', icon: 'none' })
  }
}

function openFeedback() {
  if (!plan.value?.no) return
  feedbackText.value = ''
  feedbackOpen.value = true
}

function closeFeedback() {
  if (submitting.value) return
  feedbackOpen.value = false
}

async function submitFeedback() {
  if (submitting.value) return
  const comment = feedbackText.value.trim()
  if (!comment) {
    uni.showToast({ title: '请输入具体问题', icon: 'none' })
    return
  }
  submitting.value = true
  try {
    const r = await api.sendFeedback({
      target_type: 'plan', target_id: plan.value.no,
      useful: false, comment,
    })
    uni.showToast({ title: r?.message || '已提交审核', icon: 'success' })
    feedbackOpen.value = false
  } catch (e) {
    uni.showToast({ title: '提交失败，请稍后重试', icon: 'none' })
  } finally {
    submitting.value = false
  }
}
function onStart() {
  const all = (plan.value?.stops || []).filter(s => s.lat && s.lng)
  if (!all.length) {
    uni.showToast({ title: '暂无坐标，请手动导航', icon: 'none' })
    return
  }
  if (all.length === 1) {
    const s = all[0]
    uni.openLocation({ latitude: s.lat, longitude: s.lng, name: s.name, address: s.cat })
    return
  }
  // showActionSheet 最多 6 项；超过则截断（剩下的请用时间线里每个 stop 的导航按钮）
  const candidates = all.slice(0, 6)
  uni.showActionSheet({
    itemList: candidates.map((s, i) => `${i + 1}. ${s.name || ''}`),
    success: ({ tapIndex }) => {
      const s = candidates[tapIndex]
      if (s) uni.openLocation({ latitude: s.lat, longitude: s.lng, name: s.name, address: s.cat })
    },
  })
}
</script>

<style lang="scss">
@import '../../uni.scss';

.page {
  min-height: 100vh;
  background: $z-bg;
  display: flex;
  flex-direction: column;
}

// scroll-view 必须显式撑满剩余空间，否则 sticky bottom-bar 会浮在内容流里
.scroll-body {
  flex: 1;
  min-height: 0;
}

// 反馈弹层
.feedback-mask {
  position: fixed; left: 0; right: 0; top: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 9999;
  display: flex; align-items: center; justify-content: center;
  padding: 32rpx;
}
.feedback-card {
  width: 100%;
  background: $z-card;
  border-radius: $radius-card;
  padding: 36rpx 32rpx;
  box-shadow: 0 12rpx 48rpx rgba(0, 0, 0, 0.2);
}
.feedback-title { display: block; font-size: 34rpx; font-weight: 800; color: $z-text; margin-bottom: 8rpx; }
.feedback-sub   { display: block; font-size: 23rpx; color: $z-muted; margin-bottom: 20rpx; }
.feedback-textarea {
  width: 100%; min-height: 180rpx; max-height: 320rpx;
  background: $z-bg; border-radius: 16rpx;
  padding: 20rpx 22rpx; font-size: 26rpx; color: $z-text;
  box-sizing: border-box;
}
.feedback-actions { display: flex; gap: 18rpx; margin-top: 24rpx; }
.feedback-btn {
  flex: 1; height: 84rpx; border-radius: $radius-pill;
  display: flex; align-items: center; justify-content: center;
  font-size: 28rpx; font-weight: 700;
  &.cancel { background: $z-bg; color: $z-text2; }
  &.submit { background: $z-primary; color: $z-card;
    &.disabled { opacity: 0.5; }
  }
}

.loading-state {
  padding: 16rpx 32rpx;
  background: $z-primary;
  min-height: 100vh;
}
.back-btn-plain { color: $z-card; font-size: 36rpx; padding: 8rpx; }
.loading-tip { display: block; color: rgba(255,255,255,0.6); font-family: $mono; font-size: $font-mono; margin-top: 40rpx; text-align: center; }

// Header
.header {
  background: linear-gradient(180deg, $z-primary 0%, $z-primary-d 85%, $z-bg 100%);
  padding: 0 32rpx 48rpx;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
  padding-top: 16rpx;
}

.back-btn {
  width: 68rpx;
  height: 68rpx;
  border-radius: 34rpx;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.header-right-btns {
  display: flex;
  gap: 12rpx;
}

.icon-btn {
  width: 68rpx;
  height: 68rpx;
  border-radius: 34rpx;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 32rpx;
}

.plan-no {
  display: block;
  font-size: 20rpx;
  color: rgba(255, 255, 255, 0.6);
  letter-spacing: 2rpx;
  margin-bottom: 10rpx;
}

.ai-badge {
  display: inline-block;
  background: $z-accent;
  border-radius: $radius-pill;
  padding: 6rpx 18rpx;
  margin-bottom: 10rpx;
  font-size: 22rpx;
  color: $z-card;
  font-weight: 700;
}

.plan-title {
  display: block;
  color: $z-card;
  font-size: 38rpx;
  font-weight: 900;
  margin-bottom: 10rpx;
}

.plan-summary {
  display: block;
  color: rgba(255, 255, 255, 0.75);
  font-size: 24rpx;
  line-height: 1.5;
  margin-bottom: 20rpx;
}

.meta-pills {
  display: flex;
  gap: 12rpx;
  flex-wrap: wrap;
}

.meta-pill {
  display: flex;
  align-items: center;
  gap: 8rpx;
  background: rgba(255, 255, 255, 0.15);
  border-radius: $radius-pill;
  padding: 8rpx 18rpx;
}

.meta-icon { font-size: 22rpx; }
.meta-val  { font-size: 22rpx; color: $z-card; font-weight: 600; }

// 地图
.section { padding: 28rpx 32rpx 0; }

.map-card {
  background: $z-card;
  border-radius: $radius-card;
  overflow: hidden;
  box-shadow: 0 2rpx 12rpx rgba(13, 79, 74, 0.06);
}

.map-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 22rpx 24rpx 16rpx;
}

.map-label {
  font-size: 26rpx;
  font-weight: 700;
  color: $z-text;
}

.map-meta {
  font-size: 20rpx;
  color: $z-muted;
  letter-spacing: 1rpx;
}

.mini-map {
  padding: 0 24rpx 24rpx;
}

.real-map {
  width: 100%;
  height: 300rpx;
  border-radius: 11px;
  display: block;
}

.mini-map-empty {
  padding: 28rpx 24rpx 32rpx;
  color: $z-muted;
  font-size: 22rpx;
  text-align: center;
}

// 数据源
.sources-row {
  display: flex;
  gap: 12rpx;
  padding-bottom: 4rpx;
  white-space: nowrap;
}

.source-chip {
  display: inline-flex;
  align-items: center;
  gap: 8rpx;
  background: $z-card;
  border-radius: $radius-small;
  padding: 10rpx 18rpx;
  box-shadow: 0 2rpx 8rpx rgba(13, 79, 74, 0.06);
  flex-shrink: 0;
}

.source-kind {
  font-size: 19rpx;
  color: $z-primary;
  font-weight: 700;
}

.source-t {
  font-size: 22rpx;
  color: $z-muted;
}

// 时间线
.timeline {
  display: flex;
  flex-direction: column;
}

.stop-row {
  display: flex;
  gap: 24rpx;
}

.stop-left {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 72rpx;
  flex-shrink: 0;
}

.stop-num-circle {
  width: 72rpx;
  height: 72rpx;
  border-radius: 36rpx;
  background: $z-accent;
  display: flex;
  align-items: center;
  justify-content: center;
  color: $z-card;
  font-size: 26rpx;
  font-weight: 800;
  flex-shrink: 0;
}

.timeline-line {
  flex: 1;
  width: 2rpx;
  background: linear-gradient(to bottom, $z-accent, $z-accent + '44');
  margin: 8rpx 0;
  min-height: 40rpx;
}

.arrive-time {
  font-size: 18rpx;
  color: $z-muted;
  letter-spacing: 0.5rpx;
  margin-top: 8rpx;
}

.stop-card {
  flex: 1;
  background: $z-card;
  border-radius: $radius-card;
  padding: 22rpx 24rpx;
  box-shadow: 0 2rpx 10rpx rgba(13, 79, 74, 0.06);
  margin-bottom: 20rpx;
}

.stop-name {
  display: block;
  font-size: 28rpx;
  font-weight: 800;
  color: $z-text;
  margin-bottom: 6rpx;
}

.stop-meta {
  display: block;
  font-size: 21rpx;
  color: $z-muted;
  margin-bottom: 4rpx;
}

.stop-stay {
  display: block;
  font-size: 21rpx;
  color: $z-muted;
  margin-bottom: 14rpx;
}

.why-block {
  background: rgba(13, 79, 74, 0.06);
  border-radius: 12rpx;
  padding: 14rpx 18rpx;
  margin-bottom: 10rpx;
}

.why-label {
  display: block;
  font-size: 20rpx;
  font-weight: 700;
  color: $z-primary;
  margin-bottom: 4rpx;
}

.why-text {
  display: block;
  font-size: 22rpx;
  color: $z-text2;
  line-height: 1.5;
}

.headsup-block {
  background: rgba(244, 185, 66, 0.1);
  border-radius: 12rpx;
  padding: 14rpx 18rpx;
  margin-bottom: 14rpx;
}

.headsup-label {
  display: block;
  font-size: 20rpx;
  font-weight: 700;
  color: $z-amber-d;
  margin-bottom: 4rpx;
}

.headsup-text {
  display: block;
  font-size: 22rpx;
  color: $z-text2;
  line-height: 1.5;
}

.stop-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stop-budget {
  font-size: 22rpx;
  color: $z-muted;
}

.nav-btn {
  font-size: 24rpx;
  color: $z-primary;
  font-weight: 700;
  cursor: pointer;
}

// 备用 & 免责
.backup-card {
  background: $z-card;
  border-radius: $radius-card;
  padding: 24rpx;
  box-shadow: 0 2rpx 10rpx rgba(13, 79, 74, 0.06);
}

.backup-title {
  display: block;
  font-size: 26rpx;
  font-weight: 700;
  color: $z-text;
  margin-bottom: 10rpx;
}

.backup-text {
  display: block;
  font-size: 23rpx;
  color: $z-text2;
  line-height: 1.6;
}

.disclaimer {
  border: 2rpx dashed $z-border;
  border-radius: $radius-card;
  padding: 20rpx 24rpx;
  margin-bottom: 28rpx;
}

.disclaimer-text {
  font-size: 22rpx;
  color: $z-muted;
  line-height: 1.6;
}

// 底部操作栏
.bottom-bar {
  position: sticky;
  bottom: 0;
  background: $z-card;
  border-top: 1rpx solid $z-border;
  padding: 16rpx 32rpx;
  display: flex;
  gap: 16rpx;
  z-index: 10;
}

.bottom-btn {
  height: 88rpx;
  border-radius: 18rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26rpx;
  font-weight: 700;
  cursor: pointer;

  &.outline {
    flex: 1;
    border: 2rpx solid $z-border;
    color: $z-text;
  }

  &.primary {
    background: linear-gradient(135deg, $z-primary 0%, $z-primary-m 100%);
    color: $z-card;
    box-shadow: 0 6rpx 20rpx rgba(13, 79, 74, 0.33);
  }

  &.flex2 {
    flex: 2;
  }
}
</style>
