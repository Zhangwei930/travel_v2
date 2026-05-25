<template>
  <view class="page">
    <u-nav-bar title="出游助手" right-icon="search" />

    <!-- 位置栏 -->
    <view class="loc-bar">
      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none">
        <path d="M12 22s-8-7-8-13a8 8 0 1116 0c0 6-8 13-8 13z" fill="#0D4F4A"/>
        <circle cx="12" cy="9" r="3" fill="#FFFFFF"/>
      </svg>
      <text class="loc-bar-text">{{ locLabel }}</text>
    </view>

    <!-- 消息区 -->
    <scroll-view
      scroll-y
      class="msg-scroll"
      :style="{ height: msgScrollH + 'px' }"
      :scroll-top="scrollTop"
      :show-scrollbar="false"
    >
      <view class="msg-list">
        <view v-for="(msg, i) in messages" :key="i" class="msg-row" :class="msg.role">
          <!-- Bot 头像 -->
          <view v-if="msg.role === 'bot'" class="bot-avatar-wrap">
            <view class="bot-avatar">🤖</view>
          </view>
          
          <view class="bubble-wrap" :class="msg.role">
            <view v-if="msg.text" class="bubble" :class="msg.role">
              <text>{{ msg.text }}</text>
            </view>

            <!-- Bot 快捷回复 - 2列网格 -->
            <view v-if="msg.chips && msg.role === 'bot'" class="chips-grid">
              <view
                v-for="(c, ci) in msg.chips"
                :key="c"
                class="quick-chip"
                :class="{ 'chip-full': msg.chips.length % 2 !== 0 && ci === msg.chips.length - 1 }"
                @tap="sendMsg(c)"
              >{{ c }}</view>
            </view>

            <!-- 数据源 -->
            <view v-if="msg.sources && msg.role === 'bot'" class="sources-row">
              <view v-for="s in msg.sources" :key="s.k" class="source-badge">
                <text class="source-k">[{{ s.k }}]</text>
                <text class="source-v">{{ s.v }}</text>
              </view>
            </view>

            <!-- 推荐卡片：地点 -->
            <view v-if="msg.destinations?.length" class="assistant-cards">
              <view
                v-for="poi in msg.destinations"
                :key="poi.id"
                class="assistant-poi"
                @tap="goPoi(poi.id, poi)"
              >
                <view class="poi-card-inner">
                  <image
                    :src="destinationThumb(poi)"
                    class="assistant-poi-thumb"
                    mode="aspectFill"
                    lazy-load
                    @error="onDestinationImageError(poi)"
                  />
                  <view class="poi-card-text">
                    <text class="poi-card-name">{{ poi.name }}</text>
                    <text class="poi-card-meta">{{ poi.category || '景点' }} · {{ poi.distance }}</text>
                    <text class="poi-card-reason">{{ poi.reason }}</text>
                  </view>
                  <view class="poi-card-nav" @tap.stop="openNav(poi)">
                    <text>导航</text>
                  </view>
                </view>
              </view>
            </view>

            <!-- 推荐卡片：路线 -->
            <view v-if="msg.routes?.length" class="assistant-cards">
              <view
                v-for="route in msg.routes"
                :key="route.id"
                class="assistant-route"
                @tap="openRoute(route)"
              >
                <view class="route-card-inner">
                  <image
                    :src="assistantRouteThumb(route)"
                    class="assistant-route-thumb"
                    mode="aspectFill"
                    lazy-load
                    @error="onAssistantRouteImageError(route)"
                  />
                  <view class="route-card-text">
                    <text class="route-card-title">{{ route.title }}</text>
                    <text class="route-card-meta">{{ route.duration }} · {{ route.stops?.length || 0 }}站</text>
                  </view>
                </view>
              </view>
            </view>
          </view>
        </view>

        <!-- 打字中 -->
        <view v-if="typing" class="msg-row bot">
          <view class="bot-avatar-wrap">
            <view class="bot-avatar">🤖</view>
          </view>
          <view class="bubble bot typing-bubble">
            <view class="typing-dots">
              <view class="dot" /><view class="dot" /><view class="dot" />
            </view>
          </view>
        </view>
      </view>
    </scroll-view>

    <!-- 底部输入区 -->
    <view class="composer" :style="{ bottom: tabBarHeight + 'px' }">
      <!-- 输入栏 -->
      <view class="input-bar">
        <view class="input-wrap">
          <input
            class="msg-input"
            v-model="inputText"
            placeholder="问问附近适合去哪..."
            placeholder-style="color: #9CA3AF;"
            :adjust-position="true"
            confirm-type="send"
            @confirm="sendMsg(inputText)"
          />
          <view class="input-actions">
            <text class="input-emoji">😊</text>
            <view class="send-btn" :class="{ active: inputText.length > 0 }" @tap="sendMsg(inputText)">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" stroke="#0D4F4A" stroke-width="2"/>
                <text x="12" y="17" text-anchor="middle" font-size="14" fill="#0D4F4A">+</text>
              </svg>
            </view>
          </view>
        </view>
      </view>
    </view>

    <z-tab-bar current="assistant" />
  </view>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, onUnmounted, watch } from 'vue'
import { onLoad, onShow } from '@dcloudio/uni-app'
import ZTabBar from '../../components/ZTabBar.vue'
import UNavBar from '../../components/UNavBar.vue'
import { api } from '../../api/mock.js'
import { streamAsk } from '../../api/stream.js'
import { useCityStore } from '../../store/city.js'
import { getAssistantContext } from '../../api/storage.js'
import { poiImage, routeImage } from '../../api/assets.js'

const cityStore = useCityStore()

const statusBarHeight = ref(44)
const tabBarHeight    = ref(80)
const msgScrollH      = ref(400)
const scrollTop       = ref(0)
const inputText       = ref('')
const typing          = ref(false)
const brokenDestinationImages = ref({})
const brokenRouteImages = ref({})
const HISTORY_KEY     = 'zhoumi_assistant_messages'
const locLabel = computed(() => {
  const city = cityStore.current || chatContext.value.city || ''
  return city ? `${city}·附近` : '当前位置附近'
})

const chatContext     = ref({
  city: cityStore.current,
  lat: cityStore.coords?.lat ?? null,
  lng: cityStore.coords?.lng ?? null,
  weather: '',
  time_slot: '',
  scene: '',
  intent: '',
})

const defaultMessages = [
  { role: 'bot', text: '你好呀！我是出游助手，有什么可以帮你的吗？' },
  { role: 'bot', chips: ['带孩子2小时内去哪玩？', '雨天室内去哪？', '夜晚适合去哪里？', '低预算去哪？', '附近适合约会吗？'] },
]

function loadMessages() {
  try {
    const cached = uni.getStorageSync(HISTORY_KEY)
    if (Array.isArray(cached) && cached.length) return cached
  } catch (_) {}
  return defaultMessages.map(item => ({ ...item }))
}

const messages = ref(loadMessages())

watch(messages, (val) => {
  try { uni.setStorageSync(HISTORY_KEY, val.slice(-80)) } catch (_) {}
}, { deep: true })

function applyChatContext(options = {}) {
  const cached = getAssistantContext() || {}
  const source = { ...cached, ...options }
  const lat = Number(source.lat) || cityStore.coords?.lat || null
  const lng = Number(source.lng) || cityStore.coords?.lng || null
  const city = source.city || cityStore.current

  if (lat && lng) cityStore.setCoords(lat, lng)
  
  chatContext.value = {
    city, lat, lng,
    weather: source.weather || '',
    time_slot: source.time_slot || '',
    scene: source.scene || '',
    intent: source.intent || '',
  }
}

onLoad((options) => { applyChatContext(options) })

onMounted(() => {
  try {
    const sys = uni.getSystemInfoSync()
    const statusH = sys.statusBarHeight || 44
    const safeB   = Math.max(sys.safeAreaInsets?.bottom || 18, 18)
    const winH    = sys.windowHeight || 600
    statusBarHeight.value = statusH
    const tabH = safeB + 56
    tabBarHeight.value = tabH
    const navH = 44 + statusH
    const composerH = 160 // Estimated
    msgScrollH.value = winH - navH - tabH - composerH
  } catch (_) {}
  uni.$on('assistantContext', applyChatContext)
  scrollToBottom()
})

onShow(() => { applyChatContext() })
onUnmounted(() => { uni.$off('assistantContext', applyChatContext) })

function sendMsg(text) {
  const q = text?.trim()
  if (!q) return

  const history = messages.value
    .filter(m => m.text && (m.role === 'user' || m.role === 'bot'))
    .slice(-4)
    .map(m => ({ role: m.role, text: m.text }))

  messages.value.push({ role: 'user', text: q })
  inputText.value = ''
  typing.value = true
  scrollToBottom()

  const botMsg = { role: 'bot', text: '', sources: null, chips: null, destinations: null, routes: null }
  let started = false

  const payload = {
    question: q,
    city: chatContext.value.city,
    lat: chatContext.value.lat,
    lng: chatContext.value.lng,
    scene: chatContext.value.scene || undefined,
    intent: chatContext.value.intent || 'assistant',
    weather: chatContext.value.weather || undefined,
    history,
  }

  streamAsk(payload, {
    onMeta: (m) => {
      typing.value = false
      messages.value.push(botMsg)
      botMsg.sources = m.sources
      botMsg.chips = m.chips
      botMsg.destinations = m.destinations
      botMsg.routes = m.routes
      started = true
      scrollToBottom()
    },
    onText: (t) => {
      botMsg.text = t
      scrollToBottom()
    },
    onChunk: (t) => {
      botMsg.text = (botMsg.text || '') + t
      scrollToBottom()
    },
    onDone: () => {
      typing.value = false
      if (!started) fallbackNonStream(payload)
    },
    onError: () => {
      typing.value = false
      if (!started) fallbackNonStream(payload)
    },
  })
}

function fallbackNonStream(payload) {
  api.ask(payload)
    .then((res) => {
      messages.value.push({
        role: 'bot',
        text: res.text,
        sources: res.sources,
        chips: res.chips,
        destinations: res.destinations,
        routes: res.routes,
      })
      scrollToBottom()
    })
    .catch(() => {
      messages.value.push({ role: 'bot', text: '暂时无法连接助手，请稍后再试。' })
      scrollToBottom()
    })
}

function scrollToBottom() {
  nextTick(() => { scrollTop.value = 99999 })
}

function goPoi(id, poi) {
  try { uni.setStorageSync('currentPoiPreview', poi) } catch (_) {}
  uni.navigateTo({ url: `/pages/poi/detail?id=${id}` })
}

function openNav(poi) {
  if (poi.lat && poi.lng) {
    uni.openLocation({
      latitude: Number(poi.lat),
      longitude: Number(poi.lng),
      name: poi.name,
    })
  }
}

function openRoute(route) {
  try { uni.setStorageSync('currentRoute', route) } catch (_) {}
  uni.navigateTo({ url: '/pages/routes/detail' })
}

function imageKey(item) {
  return String(item?.id ?? item?.name ?? item?.title ?? '')
}

function destinationThumb(poi) {
  return poiImage(poi, Boolean(brokenDestinationImages.value[imageKey(poi)]))
}

function onDestinationImageError(poi) {
  brokenDestinationImages.value = {
    ...brokenDestinationImages.value,
    [imageKey(poi)]: true,
  }
}

function assistantRouteThumb(route) {
  return routeImage(route, Boolean(brokenRouteImages.value[imageKey(route)]))
}

function onAssistantRouteImageError(route) {
  brokenRouteImages.value = {
    ...brokenRouteImages.value,
    [imageKey(route)]: true,
  }
}
</script>

<style lang="scss">
@import '../../uni.scss';

.page {
  min-height: 100vh;
  background: $u-bg;
}

// ── 位置栏 ──────────────────────────────────────────────────
.loc-bar {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 10rpx 32rpx;
  background: #FFFFFF;
  border-bottom: 1rpx solid $u-line;
}

.loc-bar-text {
  font-size: 24rpx;
  color: $u-text-sub;
}

.msg-scroll {
  background: $u-bg;
}

.msg-list {
  padding: 32rpx 28rpx;
  display: flex;
  flex-direction: column;
  gap: 32rpx;
}

.msg-row {
  display: flex;
  gap: 20rpx;
  
  &.user { flex-direction: row-reverse; }
}

.bot-avatar-wrap {
  width: 72rpx;
  height: 72rpx;
  flex-shrink: 0;
}

.bot-avatar {
  width: 100%;
  height: 100%;
  border-radius: 20rpx;
  background: $u-bg-soft;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40rpx;
}

.bubble-wrap {
  max-width: 80%;
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  
  &.user { align-items: flex-end; }
}

.bubble {
  padding: 24rpx 28rpx;
  font-size: 28rpx;
  line-height: 1.6;
  
  &.bot {
    background: $u-bg;
    color: $u-text;
    border-radius: 4rpx 28rpx 28rpx 28rpx;
    box-shadow: $u-shadow;
  }
  
  &.user {
    background: $z-primary;
    color: #fff;
    border-radius: 28rpx 4rpx 28rpx 28rpx;
    box-shadow: 0 4rpx 12rpx rgba(13, 79, 74, 0.15);
  }
}

// Typing
.typing-dots {
  display: flex;
  gap: 8rpx;
  align-items: center;
  height: 32rpx;
}

.dot {
  width: 10rpx;
  height: 10rpx;
  border-radius: 5rpx;
  background: $u-text-mute;
  animation: dotBounce 1.4s infinite;
  &:nth-child(2) { animation-delay: 0.2s; }
  &:nth-child(3) { animation-delay: 0.4s; }
}

@keyframes dotBounce {
  0%, 80%, 100% { transform: scale(1); opacity: 0.4; }
  40% { transform: scale(1.3); opacity: 1; }
}

// Chips 网格
.chips-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.quick-chip {
  flex: 1 1 calc(50% - 6rpx);
  max-width: calc(50% - 6rpx);
  padding: 18rpx 24rpx;
  background: $u-bg;
  border: 1rpx solid rgba(0,0,0,0.08);
  border-radius: 16rpx;
  font-size: 26rpx;
  color: $u-text-sub;
  box-sizing: border-box;

  &.chip-full {
    flex: 1 1 100%;
    max-width: 100%;
  }
}

// Sources
.sources-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.source-badge {
  background: $u-bg-soft;
  padding: 4rpx 12rpx;
  border-radius: 6rpx;
  display: flex;
  align-items: center;
  gap: 6rpx;
}

.source-k { font-size: 18rpx; color: $z-primary; font-weight: 700; }
.source-v { font-size: 18rpx; color: $u-text-mute; }

// Cards
.assistant-cards {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  width: 100%;
}

.assistant-poi, .assistant-route {
  background: $u-bg;
  border-radius: 24rpx;
  box-shadow: $u-shadow;
  overflow: hidden;
  border: 1rpx solid $u-line;
}

.poi-card-inner {
  padding: 24rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16rpx;
}

.assistant-poi-thumb {
  width: 112rpx;
  height: 112rpx;
  border-radius: 16rpx;
  flex-shrink: 0;
  background: $u-bg-soft;
}

.poi-card-text { flex: 1; min-width: 0; }
.poi-card-name { display: block; font-size: 28rpx; font-weight: 800; color: $u-text; margin-bottom: 4rpx; }
.poi-card-meta { display: block; font-size: 22rpx; color: $u-text-mute; margin-bottom: 8rpx; }
.poi-card-reason { display: block; font-size: 24rpx; color: $u-text-sub; line-height: 1.4; }

.poi-card-nav {
  height: 60rpx;
  padding: 0 24rpx;
  background: $u-tint-mint;
  color: $z-primary;
  border-radius: 30rpx;
  display: flex;
  align-items: center;
  font-size: 24rpx;
  font-weight: 700;
  flex-shrink: 0;
}

.route-card-inner {
  padding: 24rpx;
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.assistant-route-thumb {
  width: 112rpx;
  height: 88rpx;
  border-radius: 16rpx;
  flex-shrink: 0;
  background: $u-bg-soft;
}

.route-card-text { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 4rpx; }
.route-card-title { font-size: 28rpx; font-weight: 800; color: $u-text; }
.route-card-meta { font-size: 22rpx; color: $u-text-mute; }

// Composer
.composer {
  position: fixed;
  left: 0;
  right: 0;
  background: #fff;
  border-top: 1rpx solid $u-line;
  z-index: 100;
}

.input-bar {
  padding: 16rpx 28rpx 28rpx;
}

.input-wrap {
  display: flex;
  align-items: center;
  gap: 16rpx;
  background: $u-bg-soft;
  border-radius: 48rpx;
  padding: 14rpx 16rpx 14rpx 32rpx;
}

.msg-input {
  flex: 1;
  font-size: 28rpx;
  color: $u-text;
}

.input-actions {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.input-emoji {
  font-size: 40rpx;
  line-height: 1;
}

.send-btn {
  width: 60rpx;
  height: 60rpx;
  border-radius: 30rpx;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  color: $z-primary;

  &.active {
    background: $z-primary;
    box-shadow: 0 4rpx 12rpx rgba(13, 79, 74, 0.2);
  }
}
</style>
