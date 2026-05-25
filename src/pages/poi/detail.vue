<template>
  <view class="page">
    <u-nav-bar title="地点详情" right-icon="share" @right="onShare" />

    <scroll-view scroll-y class="scroll-body" :style="{ paddingBottom: safeBottom }" :show-scrollbar="false">
      <!-- 英雄图 -->
      <view class="hero-img-wrap">
        <image :src="heroImage" class="hero-img" mode="aspectFill" @error="heroImageBroken = true" />
      </view>

      <!-- 信息区 -->
      <view class="info-card">
        <!-- 名称 + 评分 -->
        <view class="name-row">
          <text class="poi-name">{{ poi.name }}</text>
          <view class="rating-badge">
            <text class="rating-star">★</text>
            <text class="rating-num">{{ ratingFor }}</text>
          </view>
        </view>

        <!-- 类型 | 费用 | 距离 -->
        <text class="poi-meta">{{ poi.cat || '景点' }} | {{ poi.budget || '免费' }} | {{ poi.dist || '' }}</text>

        <!-- 描述 -->
        <text class="poi-desc">{{ poi.reason || '该地点环境优美，适合休闲游览。' }}</text>

        <!-- 标签 -->
        <view class="poi-tags" v-if="poi.tags?.length">
          <text v-for="tag in poi.tags" :key="tag" class="poi-tag">{{ tag }}</text>
        </view>

        <!-- 信息列表 -->
        <view class="info-list">
          <view class="info-row" v-if="poi.address">
            <text class="info-label">地址</text>
            <text class="info-val">{{ poi.address }}</text>
          </view>
          <view class="info-row">
            <text class="info-label">开放时间</text>
            <text class="info-val">{{ poi.open_time || '全天开放' }}</text>
          </view>
          <view class="info-row" v-if="fitItems[0]">
            <text class="info-label">适合人群</text>
            <text class="info-val">{{ fitItems[0].val || '亲子、老人、情侣、朋友' }}</text>
          </view>
          <view class="info-row">
            <text class="info-label">建议时长</text>
            <text class="info-val">{{ poi.time || '1~2小时' }}</text>
          </view>
        </view>
      </view>
    </scroll-view>

    <!-- 底部操作栏 -->
    <view class="action-bar" :style="{ paddingBottom: safeBottomPadding }">
      <view class="action-icon-btn" @tap="toggleFav">
        <text class="action-icon-text">{{ saved ? '❤️' : '♡' }}</text>
        <text class="action-icon-label">收藏</text>
      </view>
      <view class="action-icon-btn" @tap="onShare">
        <text class="action-icon-text">⬆️</text>
        <text class="action-icon-label">分享</text>
      </view>
      <view class="nav-btn" @tap="goNav">
        <text>导航去这里</text>
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

function onShare() {
  uni.showToast({ title: '分享功能开发中', icon: 'none' })
}
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


// ── 信息卡 ──────────────────────────────────────────────────
.info-card {
  background: $u-bg;
  padding: 32rpx 32rpx 48rpx;
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

.poi-meta {
  display: block;
  font-size: 24rpx;
  color: $u-text-mute;
  margin-bottom: 16rpx;
}

.poi-desc {
  display: block;
  font-size: 26rpx;
  color: $u-text-sub;
  line-height: 1.6;
  margin-bottom: 20rpx;
}

.poi-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx;
  margin-bottom: 28rpx;
}

.poi-tag {
  font-size: 22rpx;
  color: $u-text-sub;
  background: $u-bg-soft;
  padding: 6rpx 18rpx;
  border-radius: 10rpx;
}

// ── 信息列表 ────────────────────────────────────────────────
.info-list {
  border-top: 1rpx solid $u-line;
  padding-top: 24rpx;
  display: flex;
  flex-direction: column;
  gap: 18rpx;
}

.info-row {
  display: flex;
  align-items: flex-start;
  gap: 24rpx;
}

.info-label {
  font-size: 24rpx;
  color: $u-text-mute;
  flex-shrink: 0;
  width: 120rpx;
}

.info-val {
  font-size: 24rpx;
  color: $u-text-sub;
  flex: 1;
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
  padding: 16rpx 32rpx;
  display: flex;
  align-items: center;
  gap: 24rpx;
  z-index: 100;
}

.action-icon-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4rpx;
  flex-shrink: 0;
  width: 80rpx;
}

.action-icon-text { font-size: 36rpx; line-height: 1; }
.action-icon-label { font-size: 20rpx; color: $u-text-mute; }

.nav-btn {
  flex: 1;
  height: 88rpx;
  border-radius: 44rpx;
  background: $z-primary;
  color: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30rpx;
  font-weight: 700;
  box-shadow: 0 8rpx 20rpx rgba(13, 79, 74, 0.2);
}
</style>
