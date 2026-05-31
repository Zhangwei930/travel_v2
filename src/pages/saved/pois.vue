<template>
  <view class="cy-page">
    <cy-nav-bar title="我的收藏" />

    <scroll-view scroll-y class="cy-list-scroll">
      <view v-if="list.length === 0" class="cy-empty">还没有收藏地点，去地点详情页点收藏试试</view>

      <view v-if="list.length" class="cy-list-head">
        <text class="cy-count">共 {{ list.length }} 个</text>
        <text class="cy-clear" @tap="clearAll">清空</text>
      </view>

      <view v-for="item in list" :key="item.id" class="cy-card" @tap="viewPoi(item.id)">
        <image :src="thumbFor(item)" class="cy-thumb" mode="aspectFill" lazy-load @error="onImageError(item)" />
        <view class="cy-card-info">
          <text class="cy-no">{{ item.no }}</text>
          <text class="cy-name">{{ item.name }}</text>
          <text class="cy-meta">{{ item.cat }} · {{ item.dist }}</text>
        </view>
        <view class="cy-del-btn" @tap.stop="removeItem(item)"><text>删除</text></view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getSavedPois, removeSavedPoi, clearSavedPois } from '../../api/storage.js'
import { poiImage } from '../../api/assets.js'
import CyNavBar from '../../components/cy/cy-nav-bar.vue'

const list = ref([])
const brokenImages = ref({})

// onShow：从详情页取消收藏后返回也能刷新
onShow(() => {
  list.value = getSavedPois()
})

function viewPoi(id) { uni.navigateTo({ url: `/pages/poi/detail?id=${id}` }) }
function removeItem(item) {
  uni.showModal({
    title: '删除收藏',
    content: `确定删除「${item.name}」？`,
    confirmColor: '#e25b4b',
    success: (r) => {
      if (!r.confirm) return
      removeSavedPoi(item.id)
      list.value = getSavedPois()
      uni.showToast({ title: '已删除', icon: 'none' })
    },
  })
}
function clearAll() {
  uni.showModal({
    title: '清空收藏',
    content: '确定清空全部收藏地点？',
    confirmColor: '#e25b4b',
    success: (r) => {
      if (!r.confirm) return
      clearSavedPois()
      list.value = []
      uni.showToast({ title: '已清空', icon: 'none' })
    },
  })
}
function thumbFor(item) { return poiImage(item, brokenImages.value[item.id] || 0) }
function onImageError(item) {
  brokenImages.value = { ...brokenImages.value, [item.id]: (brokenImages.value[item.id] || 0) + 1 }
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

.cy-list-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 8rpx 16rpx;
}
.cy-count { font-size: 24rpx; color: $cy-muted; }
.cy-clear { font-size: 26rpx; color: #e25b4b; font-weight: 600; }

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

.cy-no   { display: block; font-size: 20rpx; color: $cy-muted; margin-bottom: 6rpx; }
.cy-name { display: block; font-size: 30rpx; font-weight: 700; color: $cy-text; margin-bottom: 6rpx; }
.cy-meta { display: block; font-size: 24rpx; color: $cy-text-sub; }
.cy-del-btn {
  flex-shrink: 0;
  padding: 12rpx 22rpx;
  border-radius: 28rpx;
  background: rgba(226,91,75,0.1);
  color: #e25b4b;
  font-size: 24rpx;
  font-weight: 600;
}
</style>
