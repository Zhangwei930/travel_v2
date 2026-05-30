<template>
  <view class="cy-page">
    <cy-nav-bar title="地点详情" />

    <scroll-view scroll-y class="cy-scroll" :style="{ paddingBottom: safeBottom }" :show-scrollbar="false">
      <!-- 英雄图 -->
      <view class="cy-hero-wrap">
        <image :src="heroImage" class="cy-hero-img" mode="aspectFill" @error="heroBroken = true" />
      </view>

      <!-- 主信息卡 -->
      <view class="cy-info-card">
        <!-- 名称 + 评分 -->
        <view class="cy-name-row">
          <text class="cy-poi-name">{{ poi.name }}</text>
          <view class="cy-rating-badge">
            <CyIcon name="star-yellow" :size="36" />
            <text class="cy-rating-num">{{ ratingFor }}</text>
          </view>
        </view>

        <!-- 类型 | 费用 | 距离 -->
        <text class="cy-poi-meta">
          <text style="color: #1A8870;">{{ poi.cat || '景点' }} | {{ poi.budget || '免费' }} | {{ poi.dist || '' }}</text>
        </text>

        <!-- 描述 -->
        <text class="cy-poi-desc">{{ poi.reason || '该地点环境优美，适合休闲游览。' }}</text>

        <!-- 标签 -->
        <view class="cy-poi-tags" v-if="poi.tags?.length">
          <text v-for="tag in poi.tags" :key="tag" class="cy-poi-tag">{{ tag }}</text>
        </view>

        <!-- 信息表 -->
        <view class="cy-info-list">
          <view class="cy-info-row" v-if="poi.address">
            <text class="cy-info-label">地址</text>
            <text class="cy-info-val">{{ poi.address }}</text>
          </view>
          <view class="cy-info-row">
            <text class="cy-info-label">开放时间</text>
            <text class="cy-info-val">{{ poi.open_time || '全天开放' }}</text>
          </view>
          <view class="cy-info-row">
            <text class="cy-info-label">门票费用</text>
            <text class="cy-info-val">{{ poi.budget || '免费' }}</text>
          </view>
          <view class="cy-info-row" v-if="fitItems[0]">
            <text class="cy-info-label">适合人群</text>
            <text class="cy-info-val">{{ fitItems[0].val || '亲子、老人、情侣' }}</text>
          </view>
          <view class="cy-info-row">
            <text class="cy-info-label">建议时长</text>
            <text class="cy-info-val">{{ poi.time || '1~2小时' }}</text>
          </view>
        </view>
      </view>
    </scroll-view>

    <!-- 底部操作栏 -->
    <view class="cy-action-bar" :style="{ paddingBottom: safeBarPadding }">
      <view class="cy-act-icon" @tap="toggleFav">
        <CyIcon :name="saved ? 'star-fill-green' : 'star-line-dark'" :size="50" />
        <text class="cy-act-icon-label">收藏</text>
      </view>
      <button class="cy-act-icon cy-share-btn" open-type="share">
        <CyIcon name="share-dark" :size="50" />
        <text class="cy-act-icon-label">发给朋友</text>
      </button>
      <button class="cy-act-icon cy-share-btn" open-type="shareTimeline">
        <CyIcon name="share-dark" :size="50" />
        <text class="cy-act-icon-label">朋友圈</text>
      </button>
      <view class="cy-nav-btn" @tap="goNav">
        <CyIcon name="send-white" :size="38" />
        <text>导航去这里</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { onLoad, onShareAppMessage, onShareTimeline } from '@dcloudio/uni-app'
import { api } from '../../api/index.js'
import { poiImage } from '../../api/assets.js'
import { toggleSavedPoi, isSavedPoi, trackVisit } from '../../api/storage.js'
import CyNavBar from '../../components/cy/cy-nav-bar.vue'
import CyIcon from '../../components/cy/cy-icon.vue'

const safeBottom = ref('140rpx')
const safeBarPadding = ref('24rpx')
const saved = ref(false)
const poiId = ref(0)
const heroBroken = ref(false)
const poiPreview = ref(null)

const poi = ref({
  no: '', name: '', cat: '', dist: '', time: '', budget: '',
  tags: [], img: '', reason: '', fit_items: [], avoid_tips: [],
})

onLoad((options) => {
  if (options?.id != null) poiId.value = Number(options.id) || 0
  try {
    const cached = uni.getStorageSync('currentPoiPreview')
    if (cached && String(cached.id) === String(options?.id)) {
      poiPreview.value = cached
      poi.value = { ...poi.value, ...cached, cat: cached.cat || cached.category || '', img: cached.img || '' }
    }
  } catch (_) {}
})

const ratingFor = computed(() => {
  if (poi.value.rating) return Number(poi.value.rating).toFixed(1)
  return (4.3 + (poiId.value % 7) / 10).toFixed(1)
})

const DEFAULT_FIT = [{ label: '适合人群', val: '亲子·情侣' }]
const fitItems = computed(() => poi.value.fit_items?.length ? poi.value.fit_items : DEFAULT_FIT)
const heroImage = computed(() => poiImage(poi.value, heroBroken.value))

onMounted(async () => {
  try {
    const sys = uni.getWindowInfo()
    const sb = Math.max(sys.safeAreaInsets?.bottom || 18, 18)
    safeBarPadding.value = sb + 'px'
    safeBottom.value = (sb + 140) + 'rpx'
  } catch (_) {}

  if (!poiId.value) return

  try {
    let coords = {}
    try { coords = await new Promise((res) => uni.getLocation({ type: 'gcj02', success: res, fail: () => res({}) })) } catch (_) {}
    const detail = await api.getPoiDetail(poiId.value, coords.latitude, coords.longitude)
    const preview = poiPreview.value || {}
    poi.value = { ...preview, ...detail, cat: detail.cat || detail.category || preview.cat || '', img: detail.img || preview.img || '' }
    heroBroken.value = false
    trackVisit({ id: poi.value.id ?? poiId.value, no: poi.value.no, name: poi.value.name, cat: poi.value.cat, img: poi.value.img, dist: poi.value.dist })
    saved.value = isSavedPoi(poiId.value)
  } catch (_) {
    uni.showToast({ title: '加载失败', icon: 'none' })
  }
})

function toggleFav() {
  saved.value = toggleSavedPoi({ id: poi.value.id, no: poi.value.no, name: poi.value.name, cat: poi.value.cat, dist: poi.value.dist, img: poi.value.img })
  uni.showToast({ title: saved.value ? '已收藏' : '已取消收藏', icon: 'none' })
}


onShareAppMessage(() => {
  const p = poi.value
  return { title: p ? `${p.name}｜${p.cat || '出游地'}推荐` : '发现一个好去处', path: p?.id ? `/pages/poi/detail?id=${p.id}` : '/pages/index/index', imageUrl: heroImage.value || '' }
})

onShareTimeline(() => {
  const p = poi.value
  return { title: p ? `${p.name}${p.dist ? '·' + p.dist + '外' : ''}` : '发现一个好去处', query: p?.id ? `id=${p.id}` : '', imageUrl: heroImage.value || '' }
})

function goNav() {
  if (poi.value.lat && poi.value.lng) {
    uni.openLocation({ latitude: poi.value.lat, longitude: poi.value.lng, name: poi.value.name, address: poi.value.cat })
  } else {
    uni.showToast({ title: '暂无坐标', icon: 'none' })
  }
}
</script>

<style lang="scss">
@import '../../uni.scss';

.cy-page {
  min-height: 100vh;
  background: $cy-bg;
  font-family: "PingFang SC", "HarmonyOS Sans SC", "Noto Sans SC", -apple-system, system-ui, sans-serif;
}

// ── 英雄图 ─────────────────────────────────────────────────
.cy-hero-wrap {
  margin: 24rpx 24rpx 0;
  height: 400rpx;
  border-radius: 28rpx;
  overflow: hidden;
  background: $cy-green-ls;
}

.cy-hero-img { width: 100%; height: 100%; }

// ── 信息卡 ─────────────────────────────────────────────────
.cy-info-card {
  background: $cy-card;
  margin: 20rpx 24rpx;
  border-radius: 24rpx;
  padding: 28rpx;
  box-shadow: $cy-shadow;
}

.cy-name-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16rpx;
  margin-bottom: 12rpx;
}

.cy-poi-name {
  font-size: 56rpx;
  font-weight: 800;
  color: $cy-text;
  line-height: 1.2;
  flex: 1;
}

.cy-rating-badge {
  display: flex;
  align-items: center;
  gap: 4rpx;
  padding: 4rpx 16rpx;
  border-radius: 12rpx;
  background: #FFF9E6;
  flex-shrink: 0;
}

.cy-rating-num { font-size: 24rpx; font-weight: 700; color: $cy-text; }

.cy-poi-meta {
  display: block;
  font-size: 28rpx;
  font-weight: 500;
  margin-bottom: 16rpx;
}

.cy-poi-desc {
  display: block;
  font-size: 28rpx;
  color: $cy-text-sub;
  line-height: 1.7;
  margin-bottom: 20rpx;
}

.cy-poi-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx;
  margin-bottom: 24rpx;
}

.cy-poi-tag {
  font-size: 22rpx;
  color: $cy-green-d;
  background: $cy-green-l;
  padding: 6rpx 20rpx;
  border-radius: 9999rpx;
}

// ── 信息列表 ───────────────────────────────────────────────
.cy-info-list {
  border-top: 1rpx solid $cy-border;
  padding-top: 24rpx;
  display: flex;
  flex-direction: column;
}

.cy-info-row {
  display: flex;
  align-items: flex-start;
  gap: 24rpx;
  padding: 16rpx 0;
  border-bottom: 1rpx solid $cy-border;

  &:last-child { border-bottom: none; }
}

.cy-info-label {
  font-size: 26rpx;
  color: $cy-green;
  font-weight: 600;
  flex-shrink: 0;
  width: 140rpx;
}

.cy-info-val {
  font-size: 26rpx;
  color: $cy-text;
  flex: 1;
  line-height: 1.5;
}

// ── 底部操作栏 ─────────────────────────────────────────────
.cy-action-bar {
  position: fixed;
  left: 0; right: 0; bottom: 0;
  background: rgba(255,255,255,0.97);
  backdrop-filter: blur(12px);
  padding: 16rpx 28rpx;
  display: flex;
  align-items: center;
  gap: 20rpx;
  border-top: 1rpx solid $cy-border;
  z-index: 99;
}

.cy-act-icon {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4rpx;
  flex-shrink: 0;
  width: 80rpx;
}

.cy-act-icon-label { font-size: 20rpx; color: $cy-text-sub; }

.cy-share-btn {
  background: transparent;
  border: none;
  padding: 0;
  margin: 0;
  line-height: 1;
  &::after { border: none; }
}

.cy-nav-btn {
  flex: 1;
  height: 88rpx;
  background: $cy-green;
  color: #fff;
  border-radius: 44rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10rpx;
  font-size: 30rpx;
  font-weight: 800;
  box-shadow: 0 6rpx 16rpx rgba(26,136,112,0.3);
}
</style>
