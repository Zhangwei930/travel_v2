<template>
  <view class="cy-page">
    <cy-nav-bar title="按场所索引" subtitle="选择你感兴趣的类型" />

    <scroll-view
      scroll-y
      class="cy-scroll"
      :style="{ paddingBottom: tabBarH }"
      :show-scrollbar="false"
    >
      <view v-if="!scenes.length" class="cy-hint-muted"><text>场景加载中…</text></view>

      <view class="cy-scenes-grid">
        <cy-category-card
          v-for="s in scenesWithMeta"
          :key="s.id"
          :icon-type="s.iconType"
          :title="s.label"
          :desc="s.desc"
          :bg="s.bg"
          @tap="goScene(s)"
        />
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { api } from '../../api/index.js'
import { useCityStore } from '../../store/city.js'
import { consumePendingScene } from '../../api/storage.js'
import { setTabBarSelected } from '../../api/tabbar.js'
import CyNavBar from '../../components/cy/cy-nav-bar.vue'
import CyCategoryCard from '../../components/cy/cy-category-card.vue'

const cityStore = useCityStore()
const tabBarH = ref('80px')
const scenes = ref([])

const META = {
  family: { iconType: 'family', bg: '#DCEDE0' },
  couple: { iconType: 'couple', bg: '#FAE2E7' },
  rainy:  { iconType: 'rainy',  bg: '#E2EBF7' },
  budget: { iconType: 'budget', bg: '#FAEED0' },
  night:  { iconType: 'night',  bg: '#E5E2EF' },
  walk:   { iconType: 'walk',   bg: '#DCEDE0' },
  photo:  { iconType: 'photo',  bg: '#FAE2E7' },
  fish:   { iconType: 'fish',   bg: '#DCEDE0' },
  old:    { iconType: 'old',    bg: '#F0E8DC' },
  hike:   { iconType: 'hike',   bg: '#DCEDE0' },
  food:   { iconType: 'food',   bg: '#FAE2D6' },
  cycle:  { iconType: 'cycle',  bg: '#D6EAF0' },
  camp:   { iconType: 'camp',   bg: '#F5E6D3' },
}

const scenesWithMeta = computed(() =>
  scenes.value.map(s => ({
    ...s,
    iconType: META[s.id]?.iconType || '',
    bg:       META[s.id]?.bg       || '#DCEDE0',
  }))
)

function navigateToResult(sceneId) {
  if (!sceneId) return
  uni.navigateTo({ url: `/pages/scenes/result?scene=${encodeURIComponent(sceneId)}` })
}

function goScene(s) { navigateToResult(s.id) }

function applyHomeLocationContext(context = {}) {
  const lat = Number(context.lat)
  const lng = Number(context.lng)
  if (Number.isFinite(lat) && Number.isFinite(lng)) cityStore.setCoords(lat, lng)
  if (context.city) cityStore.setFromLocation(context.city)
}

onMounted(async () => {
  try {
    const sys = uni.getWindowInfo()
    tabBarH.value = ((sys.safeAreaInsets?.bottom || 18) + 56) + 'px'
  } catch (_) {}

  try {
    scenes.value = await api.getScenes()
  } catch (_) {
    uni.showToast({ title: '场景加载失败', icon: 'none' })
  }

  const pending = consumePendingScene()
  if (pending) navigateToResult(pending)

  uni.$on('switchScene', navigateToResult)
  uni.$on('homeLocationContext', applyHomeLocationContext)
})

onShow(() => {
  setTabBarSelected(1)
  const pending = consumePendingScene()
  if (pending) navigateToResult(pending)
})

onUnmounted(() => {
  uni.$off('switchScene', navigateToResult)
  uni.$off('homeLocationContext', applyHomeLocationContext)
})
</script>

<style lang="scss">
@import '../../uni.scss';

.cy-page {
  min-height: 100vh;
  background: $cy-bg;
  font-family: "PingFang SC", "HarmonyOS Sans SC", "Noto Sans SC", -apple-system, system-ui, sans-serif;
}

.cy-scroll { flex: 1; }

.cy-hint-muted {
  padding: 40rpx;
  text-align: center;
  font-size: 26rpx;
  color: $cy-muted;
}

.cy-scenes-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 24rpx;
  padding: 28rpx 24rpx 60rpx;
}
</style>
