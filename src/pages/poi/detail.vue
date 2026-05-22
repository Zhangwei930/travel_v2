<template>
  <view class="page">
    <!-- 英雄图 -->
    <view class="hero-img-wrap">
      <image :src="poi.img" class="hero-img" mode="aspectFill" />
      <view class="hero-gradient" />
      <view class="back-btn" @tap="goBack">
        <svg xmlns="http://www.w3.org/2000/svg" width="9" height="16" viewBox="0 0 9 16">
          <path d="M7.5 1.5L2 8l5.5 6.5" stroke="#1A2E2C" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
        </svg>
      </view>
      <view class="fav-btn" @tap="toggleFav">
        <text>{{ saved ? '❤️' : '🤍' }}</text>
      </view>
    </view>

    <scroll-view scroll-y class="scroll-body" :show-scrollbar="false">
      <!-- 信息卡（悬浮 -32px） -->
      <view class="info-card">
        <text class="poi-no mono">{{ poi.no }}</text>
        <text class="poi-name serif">{{ poi.name }}</text>
        <text class="poi-meta">{{ poi.cat }} · {{ poi.dist }}</text>
        <view class="poi-tags">
          <z-tag v-for="tag in poi.tags" :key="tag" :label="tag" color="#0D4F4A" />
        </view>
        <view class="poi-stats">
          <view class="poi-stat" v-for="s in stats" :key="s.label">
            <text class="stat-num">{{ s.val }}</text>
            <text class="stat-label">{{ s.label }}</text>
          </view>
        </view>
      </view>

      <!-- §01 推荐理由 -->
      <view class="section">
        <z-section-header no="01" title="推荐理由" />
        <view class="reason-card">
          <text class="reason-text">{{ poi.reason }}</text>
        </view>
      </view>

      <!-- §02 适合人群与场景 -->
      <view class="section">
        <z-section-header no="02" title="适合人群与场景" />
        <view class="fit-grid">
          <view class="fit-item" v-for="item in fitItems" :key="item.label">
            <text class="fit-icon">{{ item.icon }}</text>
            <text class="fit-label">{{ item.label }}</text>
            <text class="fit-val">{{ item.val }}</text>
          </view>
        </view>
      </view>

      <!-- §03 避坑提醒 -->
      <view class="section">
        <z-section-header no="03" title="避坑提醒" />
        <view class="tips-card">
          <view class="tip-row" v-for="(tip, i) in avoidTips" :key="i">
            <text class="tip-no mono">{{ String(i + 1).padStart(2, '0') }}</text>
            <text class="tip-text">{{ tip }}</text>
          </view>
        </view>
      </view>
    </scroll-view>

    <!-- 底部操作栏 -->
    <view class="bottom-bar" :style="{ paddingBottom: safeBottom }">
      <view class="bottom-btn outline" @tap="goAssistant">💬 问助手</view>
      <view class="bottom-btn primary flex2" @tap="goNav">🧭 地图导航前往</view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '../../api/mock.js'
import { toggleSavedPoi, isSavedPoi, trackVisit } from '../../api/storage.js'
import ZSectionHeader from '../../components/ZSectionHeader.vue'
import ZTag from '../../components/ZTag.vue'

const safeBottom = ref('18px')
const saved      = ref(false)

// 从路由参数获取 id
const pages = getCurrentPages()
const currentPage = pages[pages.length - 1]
let poiId = 1
try { poiId = Number(currentPage.$page?.fullPath?.match(/id=(\d+)/)?.[1]) || 1 } catch (_) {}

const poi = ref({
  no: '', name: '', cat: '', dist: '', time: '', budget: '',
  tags: [], img: '', reason: '', fit_items: [], avoid_tips: [],
})

const stats = computed(() => [
  { val: poi.value.time,   label: '推荐时长' },
  { val: poi.value.budget, label: '参考费用' },
  { val: poi.value.dist,   label: '距离' },
])

const DEFAULT_FIT = [
  { icon: '👨‍👩‍👧', label: '人群', val: '亲子·情侣' },
  { icon: '🌤', label: '天气', val: '晴天最佳' },
  { icon: '⏰', label: '时段', val: '清晨·上午' },
  { icon: '💪', label: '强度', val: '轻量' },
]
const DEFAULT_TIPS = [
  '节假日人多，建议提前到达',
  '自备充足饮用水',
  '注意防晒，夏季阳光较强',
]

const fitItems  = computed(() => (poi.value.fit_items?.length ? poi.value.fit_items : DEFAULT_FIT))
const avoidTips = computed(() => (poi.value.avoid_tips?.length ? poi.value.avoid_tips : DEFAULT_TIPS))

onMounted(async () => {
  try {
    const sys = uni.getSystemInfoSync()
    safeBottom.value = Math.max(sys.safeAreaInsets?.bottom || 18, 18) + 'px'
  } catch (_) {}

  try {
    poi.value = await api.getPoiDetail(poiId)
    trackVisit(poiId)
    saved.value = isSavedPoi(poiId)
  } catch (_) {
    uni.showToast({ title: '地点信息加载失败', icon: 'none' })
  }
})

function goBack()      { uni.navigateBack() }
function toggleFav() {
  saved.value = toggleSavedPoi({
    id: poi.value.id, no: poi.value.no,
    name: poi.value.name, cat: poi.value.cat,
    dist: poi.value.dist, img: poi.value.img,
  })
  uni.showToast({ title: saved.value ? '已收藏' : '已取消收藏', icon: 'none' })
}
function goAssistant() { uni.switchTab({ url: '/pages/assistant/chat' }) }
function goNav() {
  if (poi.value.lat && poi.value.lng) {
    uni.openLocation({
      latitude:  poi.value.lat,
      longitude: poi.value.lng,
      name:      poi.value.name,
      address:   poi.value.cat,
    })
  } else {
    uni.showToast({ title: '暂无坐标，无法导航', icon: 'none' })
  }
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

.hero-img-wrap {
  height: 460rpx;
  position: relative;
  flex-shrink: 0;
}

.hero-img {
  width: 100%;
  height: 100%;
}

.hero-gradient {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 200rpx;
  background: linear-gradient(to top, rgba(245, 241, 235, 0.9), transparent);
}

.back-btn {
  position: absolute;
  top: 100rpx;
  left: 28rpx;
  width: 68rpx;
  height: 68rpx;
  border-radius: 34rpx;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(8px);
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.12);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  cursor: pointer;
}

.fav-btn {
  position: absolute;
  top: 100rpx;
  right: 28rpx;
  width: 68rpx;
  height: 68rpx;
  border-radius: 34rpx;
  background: rgba(255, 255, 255, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32rpx;
  cursor: pointer;
}

.scroll-body {
  flex: 1;
}

// 信息卡悬浮
.info-card {
  margin: -64rpx 32rpx 0;
  background: $z-card;
  border-radius: $radius-card;
  padding: 28rpx;
  box-shadow: 0 8rpx 32rpx rgba(13, 79, 74, 0.12);
  position: relative;
  z-index: 2;
}

.poi-no {
  display: block;
  font-size: 19rpx;
  color: $z-muted;
  letter-spacing: 1rpx;
  margin-bottom: 6rpx;
}

.poi-name {
  display: block;
  font-size: 36rpx;
  font-weight: 900;
  color: $z-text;
  margin-bottom: 8rpx;
}

.poi-meta {
  display: block;
  font-size: 23rpx;
  color: $z-muted;
  margin-bottom: 14rpx;
}

.poi-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx;
  margin-bottom: 20rpx;
}

.poi-stats {
  display: flex;
  border-top: 1rpx solid $z-line;
  padding-top: 18rpx;
}

.poi-stat {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6rpx;

  &:not(:last-child) {
    border-right: 1rpx solid $z-line;
  }
}

.stat-num {
  display: block;
  font-size: 26rpx;
  font-weight: 700;
  color: $z-text;
}

.stat-label {
  display: block;
  font-size: 21rpx;
  color: $z-muted;
}

.section {
  padding: 28rpx 32rpx 0;
}

.reason-card {
  background: $z-card;
  border-radius: $radius-card;
  padding: 24rpx;
  box-shadow: 0 2rpx 10rpx rgba(13, 79, 74, 0.05);
}

.reason-text {
  font-size: 26rpx;
  color: $z-text2;
  line-height: 1.65;
}

.fit-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16rpx;
}

.fit-item {
  background: $z-card;
  border-radius: $radius-small;
  padding: 20rpx;
  display: flex;
  flex-direction: column;
  gap: 6rpx;
  box-shadow: 0 2rpx 8rpx rgba(13, 79, 74, 0.05);
}

.fit-icon { font-size: 28rpx; }
.fit-label { font-size: 21rpx; color: $z-muted; }
.fit-val   { font-size: 25rpx; font-weight: 700; color: $z-text; }

.tips-card {
  background: rgba(244, 185, 66, 0.08);
  border: 1rpx solid rgba(244, 185, 66, 0.3);
  border-radius: $radius-card;
  padding: 24rpx;
  display: flex;
  flex-direction: column;
  gap: 14rpx;
  margin-bottom: 28rpx;
}

.tip-row {
  display: flex;
  align-items: flex-start;
  gap: 16rpx;
}

.tip-no {
  font-size: 20rpx;
  color: $z-muted;
  font-weight: 700;
  letter-spacing: 1rpx;
  flex-shrink: 0;
  margin-top: 3rpx;
}

.tip-text {
  font-size: 25rpx;
  color: $z-text2;
  line-height: 1.5;
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

  &.flex2 { flex: 2; }
}
</style>
