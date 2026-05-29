<template>
  <view class="cy-page">
    <cy-nav-bar title="我的足迹" />

    <scroll-view scroll-y class="cy-list-scroll">
      <view v-if="list.length === 0" class="cy-empty">还没有访问过任何地点，去地点详情页打卡吧</view>

      <view v-for="item in list" :key="item.id" class="cy-card" @tap="viewPoi(item.id)">
        <image :src="thumbFor(item)" class="cy-thumb" mode="aspectFill" lazy-load @error="onImageError(item)" />
        <view class="cy-card-info">
          <view class="cy-meta-row">
            <text class="cy-no">{{ item.no }}</text>
            <text class="cy-date">{{ formatDate(item.visitedAt) }}</text>
          </view>
          <text class="cy-name">{{ item.name }}</text>
          <text class="cy-meta">{{ item.cat }} · {{ item.dist }}</text>
        </view>
        <text class="cy-arrow">›</text>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getVisitedList } from '../../api/storage.js'
import { poiImage } from '../../api/assets.js'
import CyNavBar from '../../components/cy/cy-nav-bar.vue'

const list = ref([])
const brokenImages = ref({})

onMounted(() => {
  list.value = getVisitedList()
})

function viewPoi(id) { uni.navigateTo({ url: `/pages/poi/detail?id=${id}` }) }
function thumbFor(item) { return poiImage(item, Boolean(brokenImages.value[item.id])) }
function onImageError(item) {
  brokenImages.value = { ...brokenImages.value, [item.id]: true }
}
function formatDate(ts) {
  if (!ts) return ''
  const d = new Date(ts)
  return `${d.getMonth() + 1}/${d.getDate()}`
}
</script>

<style lang="scss">
@import '../../uni.scss';

.cy-page {
  min-height: 100vh;
  background: $cy-bg;
  font-family: "PingFang SC", "HarmonyOS Sans SC", "Noto Sans SC", -apple-system, system-ui, sans-serif;
}

.cy-list-scroll { padding: 24rpx; box-sizing: border-box; }

.cy-empty {
  display: block;
  color: $cy-muted;
  font-size: 26rpx;
  text-align: center;
  margin-top: 80rpx;
}

.cy-card {
  display: flex;
  align-items: center;
  background: $cy-card;
  border-radius: 24rpx;
  padding: 20rpx;
  margin-bottom: 16rpx;
  gap: 20rpx;
  box-shadow: $cy-shadow;
}

.cy-thumb { width: 120rpx; height: 120rpx; border-radius: 16rpx; flex-shrink: 0; background: $cy-green-ls; }
.cy-card-info { flex: 1; }

.cy-meta-row { display: flex; justify-content: space-between; margin-bottom: 6rpx; }
.cy-no   { font-size: 20rpx; color: $cy-muted; }
.cy-date { font-size: 20rpx; color: $cy-muted; }
.cy-name { display: block; font-size: 30rpx; font-weight: 700; color: $cy-text; margin-bottom: 6rpx; }
.cy-meta { display: block; font-size: 24rpx; color: $cy-text-sub; }
.cy-arrow { font-size: 36rpx; color: $cy-muted; }
</style>
