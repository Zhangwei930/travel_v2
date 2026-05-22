<template>
  <view class="page">
    <view class="header" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="header-inner">
        <text class="back" @tap="goBack">←</text>
        <text class="title serif">我的收藏</text>
        <text class="count mono">{{ list.length }} 个</text>
      </view>
    </view>

    <scroll-view scroll-y class="list-scroll">
      <view v-if="list.length === 0" class="empty mono">还没有收藏地点，去地点详情页点 ❤️ 试试</view>

      <view v-for="item in list" :key="item.id" class="card" @tap="viewPoi(item.id)">
        <image v-if="item.img" :src="item.img" class="thumb" mode="aspectFill" lazy-load />
        <view class="card-info">
          <text class="no mono">{{ item.no }}</text>
          <text class="name serif">{{ item.name }}</text>
          <text class="meta">{{ item.cat }} · {{ item.dist }}</text>
        </view>
        <text class="arrow">›</text>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getSavedPois } from '../../api/storage.js'

const statusBarHeight = ref(44)
const list = ref([])

onMounted(() => {
  try { statusBarHeight.value = uni.getSystemInfoSync().statusBarHeight || 44 } catch (_) {}
  list.value = getSavedPois()
})

function goBack() { uni.navigateBack() }
function viewPoi(id) { uni.navigateTo({ url: `/pages/poi/detail?id=${id}` }) }
</script>

<style lang="scss" scoped>
@import '@/uni.scss';

.page { min-height: 100vh; background: $z-bg; }

.header {
  background: $z-card;
  border-bottom: 1rpx solid $z-border;
  padding-bottom: 24rpx;
  &-inner { display: flex; align-items: center; padding: 16rpx 32rpx 0; gap: 16rpx; }
}
.back { font-size: 36rpx; color: $z-accent; padding: 8rpx; }
.title { font-size: 36rpx; font-family: $serif; color: $z-text; flex: 1; }
.count { font-size: $font-mono; color: $z-muted; font-family: $mono; }

.list-scroll { height: calc(100vh - 120rpx); padding: 24rpx; box-sizing: border-box; }
.empty { color: $z-muted; font-family: $mono; font-size: $font-mono; text-align: center; margin-top: 80rpx; display: block; }

.card {
  display: flex;
  align-items: center;
  background: $z-card;
  border-radius: $radius-card;
  padding: 20rpx;
  margin-bottom: 16rpx;
  gap: 20rpx;
}
.thumb { width: 120rpx; height: 120rpx; border-radius: $radius-small; flex-shrink: 0; }
.card-info { flex: 1; }
.no { display: block; font-family: $mono; font-size: $font-mono; color: $z-muted; margin-bottom: 6rpx; }
.name { display: block; font-family: $serif; font-size: 30rpx; color: $z-text; margin-bottom: 6rpx; }
.meta { display: block; font-size: $font-sm; color: $z-text2; }
.arrow { font-size: 36rpx; color: $z-muted; }
</style>
