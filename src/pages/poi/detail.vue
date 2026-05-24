<template>
  <view class="page">
    <u-nav-bar :title="poi.name || '地点详情'" transparent />

    <scroll-view scroll-y class="scroll-body" :style="{ paddingBottom: safeBottom }" :show-scrollbar="false">
      <!-- 英雄图 -->
      <view class="hero-img-wrap">
        <image :src="heroImage" class="hero-img" mode="aspectFill" @error="heroImageBroken = true" />
        <view class="hero-mask" />
        <view class="fav-btn" @tap="toggleFav">
          <text>{{ saved ? '❤️' : '🤍' }}</text>
        </view>
      </view>

      <!-- 信息卡 -->
      <view class="info-card">
        <view class="name-row">
          <text class="poi-name">{{ poi.name }}</text>
          <view class="rating-badge">
            <text class="rating-star">★</text>
            <text class="rating-num">{{ ratingFor }}</text>
          </view>
        </view>
        <text class="poi-cat-dist">{{ poi.cat || '景点' }} · {{ poi.dist || '距离获取中' }}</text>

        <view class="poi-tags">
          <text v-for="tag in (poi.tags || [])" :key="tag" class="poi-tag">{{ tag }}</text>
        </view>

        <view class="stats-grid">
          <view class="stat-item">
            <text class="stat-label">推荐时长</text>
            <text class="stat-val">{{ poi.time || '1-2小时' }}</text>
          </view>
          <view class="stat-divider" />
          <view class="stat-item">
            <text class="stat-label">参考费用</text>
            <text class="stat-val">{{ poi.budget || '免费' }}</text>
          </view>
          <view class="stat-divider" />
          <view class="stat-item">
            <text class="stat-label">开放时段</text>
            <text class="stat-val">全天</text>
          </view>
        </view>
      </view>

      <!-- 推荐理由 -->
      <view class="section">
        <view class="section-head">
          <text class="section-title">推荐理由</text>
        </view>
        <view class="reason-box">
          <text class="reason-text">{{ poi.reason || '该地点暂无详细推荐理由。' }}</text>
        </view>
      </view>

      <!-- 适合人群与场景 -->
      <view class="section">
        <view class="section-head">
          <text class="section-title">适合场景</text>
        </view>
        <view class="fit-grid">
          <view class="fit-card" v-for="item in fitItems" :key="item.label">
            <view class="fit-icon-bg">
              <text class="fit-icon">{{ item.icon }}</text>
            </view>
            <view class="fit-text">
              <text class="fit-label">{{ item.label }}</text>
              <text class="fit-val">{{ item.val }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 避坑提醒 -->
      <view class="section avoid-section">
        <view class="section-head">
          <text class="section-title">避坑提醒</text>
        </view>
        <view class="tips-list">
          <view class="tip-item" v-for="(tip, i) in avoidTips" :key="i">
            <view class="tip-dot" />
            <text class="tip-text">{{ tip }}</text>
          </view>
        </view>
      </view>
    </scroll-view>

    <!-- 底部操作栏 -->
    <view class="action-bar" :style="{ paddingBottom: safeBottomPadding }">
      <view class="action-btn outline" @tap="goAssistant">
        <text>💬 咨询助手</text>
      </view>
      <view class="action-btn primary" @tap="goNav">
        <text>🧭 导航前往</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { api } from '../../api/mock.js'
import { poiImage } from '../../api/assets.js'
import { toggleSavedPoi, isSavedPoi, trackVisit } from '../../api/storage.js'
import UNavBar from '../../components/UNavBar.vue'

const safeBottom = ref('140rpx')
const safeBottomPadding = ref('24rpx')
const saved      = ref(false)
const poiId      = ref(0)
const heroImageBroken = ref(false)
const poiPreview = ref(null)

const poi = ref({
  no: '', name: '', cat: '', dist: '', time: '', budget: '',
  tags: [], img: '', reason: '', fit_items: [], avoid_tips: [],
})

onLoad((options) => {
  const raw = options?.id
  if (raw != null) poiId.value = Number(raw) || 0
  try {
    const cached = uni.getStorageSync('currentPoiPreview')
    if (cached && String(cached.id) === String(raw)) {
      poiPreview.value = cached
      poi.value = {
        ...poi.value,
        ...cached,
        cat: cached.cat || cached.category || poi.value.cat,
        img: cached.img || poi.value.img,
      }
    }
  } catch (_) {}
})

const ratingFor = computed(() => {
  if (poi.value.rating) return Number(poi.value.rating).toFixed(1)
  return (4.3 + (poiId.value % 7) / 10).toFixed(1)
})

const DEFAULT_FIT = [
  { icon: '👨‍👩‍👧', label: '适合人群', val: '亲子·情侣' },
  { icon: '🌤', label: '推荐天气', val: '晴天/多云' },
  { icon: '⏰', label: '推荐时段', val: '上午/下午' },
  { icon: '💪', label: '活动强度', val: '轻量' },
]
const DEFAULT_TIPS = [
  '该地点人气较旺，建议错峰出行',
  '户外站点请注意防蚊防晒',
  '周边车位有限，建议使用公共交通',
]

const fitItems  = computed(() => (poi.value.fit_items?.length ? poi.value.fit_items : DEFAULT_FIT))
const avoidTips = computed(() => (poi.value.avoid_tips?.length ? poi.value.avoid_tips : DEFAULT_TIPS))
const heroImage = computed(() => poiImage(poi.value, heroImageBroken.value))

onMounted(async () => {
  try {
    const sys = uni.getSystemInfoSync()
    const sb = Math.max(sys.safeAreaInsets?.bottom || 18, 18)
    safeBottomPadding.value = sb + 'px'
    safeBottom.value = (sb + 140) + 'rpx'
  } catch (_) {}

  if (!poiId.value) return

  try {
    let coords = {}
    try {
      coords = await new Promise((res) => uni.getLocation({ type: 'gcj02', success: res, fail: () => res({}) }))
    } catch (_) {}
    const detail = await api.getPoiDetail(poiId.value, coords.latitude, coords.longitude)
    const preview = poiPreview.value || {}
    poi.value = {
      ...preview,
      ...detail,
      cat: detail.cat || detail.category || preview.cat || preview.category || '',
      img: detail.img || preview.img || '',
    }
    heroImageBroken.value = false
    trackVisit({
      id: poi.value.id ?? poiId.value, no: poi.value.no, name: poi.value.name,
      cat: poi.value.cat, img: poi.value.img, dist: poi.value.dist,
    })
    saved.value = isSavedPoi(poiId.value)
  } catch (_) {
    uni.showToast({ title: '加载失败', icon: 'none' })
  }
})

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
    uni.showToast({ title: '暂无坐标', icon: 'none' })
  }
}
</script>

<style lang="scss">
@import '../../uni.scss';

.page {
  min-height: 100vh;
  background: $u-bg;
}

.scroll-body {
  position: relative;
}

// ── 英雄图 ──────────────────────────────────────────────────
.hero-img-wrap {
  height: 540rpx;
  position: relative;
  background: $u-bg-soft;
}

.hero-img {
  width: 100%;
  height: 100%;
}

.hero-mask {
  position: absolute;
  inset: 0;
  background: linear-gradient(to bottom, rgba(0,0,0,0.15) 0%, transparent 40%, rgba(255,255,255,0.4) 100%);
}

.fav-btn {
  position: absolute;
  top: 100rpx;
  right: 32rpx;
  width: 72rpx;
  height: 72rpx;
  border-radius: 36rpx;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32rpx;
  box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.08);
  z-index: 10;
}

// ── 信息卡 ──────────────────────────────────────────────────
.info-card {
  margin: -60rpx 32rpx 0;
  background: $u-bg;
  border-radius: 28rpx;
  padding: 36rpx 32rpx;
  box-shadow: $u-shadow-lg;
  position: relative;
  z-index: 2;
}

.name-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16rpx;
  margin-bottom: 8rpx;
}

.poi-name {
  font-size: 36rpx;
  font-weight: 800;
  color: $u-text;
  line-height: 1.25;
}

.rating-badge {
  display: flex;
  align-items: center;
  gap: 4rpx;
  background: $u-bg-soft;
  padding: 4rpx 14rpx;
  border-radius: 10rpx;
  flex-shrink: 0;
}

.rating-star { color: #F59E0B; font-size: 24rpx; }
.rating-num { font-size: 24rpx; font-weight: 700; color: $u-text; }

.poi-cat-dist {
  display: block;
  font-size: 24rpx;
  color: $u-text-mute;
  margin-bottom: 20rpx;
}

.poi-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx;
  margin-bottom: 32rpx;
}

.poi-tag {
  font-size: 20rpx;
  color: $u-text-sub;
  background: $u-bg-soft;
  padding: 4rpx 16rpx;
  border-radius: 8rpx;
}

.stats-grid {
  display: flex;
  align-items: center;
  padding-top: 28rpx;
  border-top: 1rpx solid $u-line;
}

.stat-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6rpx;
}

.stat-label { font-size: 20rpx; color: $u-text-mute; }
.stat-val { font-size: 26rpx; font-weight: 700; color: $u-text; }
.stat-divider { width: 1rpx; height: 32rpx; background: $u-line; }

// ── 推荐理由 ────────────────────────────────────────────────
.section { padding: 32rpx 32rpx 0; }
.section-head { margin-bottom: 20rpx; }
.section-title { font-size: 32rpx; font-weight: 800; color: $u-text; }

.reason-box {
  background: $u-bg-soft;
  border-radius: 20rpx;
  padding: 24rpx 28rpx;
}

.reason-text {
  font-size: 26rpx;
  color: $u-text-sub;
  line-height: 1.6;
}

// ── 适合场景 ────────────────────────────────────────────────
.fit-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16rpx;
}

.fit-card {
  background: $u-bg;
  border-radius: 18rpx;
  padding: 20rpx;
  display: flex;
  align-items: center;
  gap: 16rpx;
  box-shadow: $u-shadow;
}

.fit-icon-bg {
  width: 60rpx;
  height: 60rpx;
  border-radius: 16rpx;
  background: $u-bg-soft;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.fit-icon { font-size: 30rpx; }
.fit-text { display: flex; flex-direction: column; gap: 2rpx; }
.fit-label { font-size: 20rpx; color: $u-text-mute; }
.fit-val { font-size: 24rpx; font-weight: 700; color: $u-text; }

// ── 避坑提醒 ────────────────────────────────────────────────
.avoid-section { padding-bottom: 40rpx; }
.tips-list { display: flex; flex-direction: column; gap: 16rpx; }

.tip-item {
  display: flex;
  gap: 18rpx;
  align-items: flex-start;
}

.tip-dot {
  width: 8rpx;
  height: 8rpx;
  border-radius: 4rpx;
  background: #F59E0B;
  margin-top: 14rpx;
  flex-shrink: 0;
}

.tip-text {
  font-size: 26rpx;
  color: $u-text-sub;
  line-height: 1.5;
}

// ── 底部栏 ──────────────────────────────────────────────────
.action-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  background: #fff;
  border-top: 1rpx solid $u-line;
  padding: 20rpx 32rpx;
  display: flex;
  gap: 18rpx;
  z-index: 100;
}

.action-btn {
  height: 88rpx;
  border-radius: 44rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
  font-weight: 800;

  &.outline {
    flex: 1;
    background: $u-bg-soft;
    color: $u-text;
  }

  &.primary {
    flex: 1.8;
    background: $z-primary;
    color: #fff;
    box-shadow: 0 8rpx 20rpx rgba(13, 79, 74, 0.2);
  }
}
</style>
