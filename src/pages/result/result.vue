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
          <view class="icon-btn">
            <text>📤</text>
          </view>
        </view>
      </view>

      <!-- 方案编号 -->
      <text class="plan-no mono">{{ plan.no }}</text>

      <!-- AI 徽章（AI 生成时显示） -->
      <view v-if="isGenerated" class="ai-badge">
        <text>✨ AI · NEW</text>
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
            <text class="map-meta mono">{{ plan.stops.length }} STOPS · ~90 MIN</text>
          </view>
          <!-- SVG 简化地图 -->
          <view class="mini-map">
            <svg :viewBox="'0 0 360 140'" style="width:100%;height:140px;border-radius:11px;background:#E8F0EE;display:block">
              <defs>
                <pattern id="grid2" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
                  <path d="M 20 0 L 0 0 0 20" stroke="#D5E3DF" stroke-width="0.5" fill="none"/>
                </pattern>
              </defs>
              <rect width="360" height="140" fill="url(#grid2)"/>
              <path d="M 0 80 Q 100 50 200 85 T 360 75" stroke="#fff" stroke-width="13" fill="none"/>
              <path d="M 0 80 Q 100 50 200 85 T 360 75" stroke="#CCD9D5" stroke-width="1.5" fill="none"/>
              <path d="M 40 90 L 160 35 L 300 70" stroke="#FF6B35" stroke-width="2.5" stroke-dasharray="5 4" fill="none"/>
              <g v-for="(stop, i) in plan.stops" :key="i">
                <circle :cx="[40,160,300][i]" :cy="[90,35,70][i]" r="11" fill="#fff" stroke="#FF6B35" stroke-width="2.2"/>
                <text :x="[40,160,300][i]" :y="[90,35,70][i]+4" text-anchor="middle" font-size="11" font-weight="700" fill="#FF6B35">{{ i+1 }}</text>
              </g>
            </svg>
          </view>
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
                <text class="why-label">💡 WHY HERE</text>
                <text class="why-text">{{ stop.reason }}</text>
              </view>

              <view class="headsup-block">
                <text class="headsup-label">⚠️ HEADS UP</text>
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

    <!-- 底部操作栏 -->
    <view class="bottom-bar" :style="{ paddingBottom: safeBottom }">
      <view class="bottom-btn outline" @tap="onFeedback(true)">👍 有用</view>
      <view class="bottom-btn outline" @tap="onFeedback(false)">💬 反馈</view>
      <view class="bottom-btn primary flex2" @tap="onStart">🧭 开始出发</view>
    </view>
    </template>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '../../api/mock.js'
import ZSectionHeader from '../../components/ZSectionHeader.vue'

const statusBarHeight = ref(44)
const safeBottom      = ref('18px')
const saved           = ref(false)

const plan = ref(null)

const pages = getCurrentPages()
const currentPage = pages[pages.length - 1]
const isGenerated = computed(() => {
  try { return !!currentPage.$page?.fullPath?.includes('generated=1') } catch (_) { return false }
})

const planMeta = computed(() => plan.value ? [
  { icon: '⏱', val: plan.value.totalTime },
  { icon: '💰', val: plan.value.totalBudget },
  { icon: '👥', val: plan.value.people },
  { icon: '🌤', val: plan.value.weather },
] : [])

onMounted(async () => {
  try {
    const sys = uni.getSystemInfoSync()
    statusBarHeight.value = sys.statusBarHeight || 44
    safeBottom.value = Math.max(sys.safeAreaInsets?.bottom || 18, 18) + 'px'
  } catch (_) {}

  // 读取生成页存入的真实攻略结果，无数据则返回上一页
  try {
    const cached = uni.getStorageSync('lastPlan')
    if (cached && cached.stops) {
      plan.value = cached
    } else {
      uni.showToast({ title: '暂无攻略，请先生成', icon: 'none' })
      setTimeout(() => uni.navigateBack(), 1200)
    }
  } catch (_) {
    uni.navigateBack()
  }
})

function goBack() { uni.navigateBack() }
function toggleFav() { saved.value = !saved.value }
function onNav(stop) {
  if (stop.lat && stop.lng) {
    uni.openLocation({ latitude: stop.lat, longitude: stop.lng, name: stop.name, address: stop.cat })
  } else {
    uni.showToast({ title: '暂无坐标，无法导航', icon: 'none' })
  }
}
function onFeedback(useful) {
  api.sendFeedback({ target_type: 'plan', target_id: plan.value.no, useful }).catch(() => {})
  uni.showToast({ title: '感谢反馈', icon: 'success' })
}
function onStart() { uni.showToast({ title: '调起地图导航', icon: 'none' }) }
</script>

<style lang="scss">
@import '../../uni.scss';

.page {
  min-height: 100vh;
  background: $z-bg;
  display: flex;
  flex-direction: column;
}

.loading-state {
  padding: 16rpx 32rpx;
  background: $z-primary;
  min-height: 100vh;
}
.back-btn-plain { color: #fff; font-size: 36rpx; padding: 8rpx; }
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
  color: #fff;
  font-weight: 700;
}

.plan-title {
  display: block;
  color: #fff;
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
.meta-val  { font-size: 22rpx; color: #fff; font-weight: 600; }

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
  color: #0D4F4A;
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
  color: #fff;
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
  color: #0D4F4A;
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
  color: #B8860B;
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
  color: #0D4F4A;
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
    background: linear-gradient(135deg, #0D4F4A 0%, #1A7A73 100%);
    color: #fff;
    box-shadow: 0 6rpx 20rpx rgba(13, 79, 74, 0.33);
  }

  &.flex2 {
    flex: 2;
  }
}
</style>
