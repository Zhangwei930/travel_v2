<template>
  <view class="cy-page">
    <!-- Header -->
    <view class="cy-chat-header" :style="{ paddingTop: statusBarH + 'px' }">
      <text class="cy-chat-title">出游助手</text>
      <view class="cy-chat-loc">
        <CyIcon name="pin-outline-green" :size="26" />
        <text class="cy-chat-loc-text">{{ locLabel }}</text>
      </view>
    </view>

    <!-- 消息区 -->
    <scroll-view
      scroll-y
      class="cy-msg-scroll"
      :style="{ height: msgScrollH + 'px' }"
      :scroll-top="scrollTop"
      :show-scrollbar="false"
    >
      <view class="cy-msg-list">
        <view v-for="(msg, i) in messages" :key="i" class="cy-msg-row" :class="msg.role">

          <!-- Bot 头像 -->
          <view v-if="msg.role === 'bot'" class="cy-bot-avatar">
            <cy-robot-mascot :size="72" />
          </view>

          <view class="cy-bubble-wrap" :class="msg.role">
            <!-- 图片气泡 -->
            <view v-if="msg.image" class="cy-bubble cy-bubble--user cy-bubble--img">
              <image :src="msg.image" class="cy-msg-image" mode="widthFix" />
            </view>

            <!-- 文字气泡 -->
            <view v-if="msg.text" class="cy-bubble" :class="'cy-bubble--' + msg.role">
              <text user-select>{{ msg.text }}</text>
            </view>

            <view v-if="msg.destinations && msg.destinations.length" class="cy-dest-cards">
              <view
                v-for="poi in msg.destinations"
                :key="imgKey(poi)"
                class="cy-dest-card"
                @tap="goPoi(poi.id, poi)"
              >
                <image
                  class="cy-dest-thumb"
                  :src="destinationThumb(poi)"
                  mode="aspectFill"
                  lazy-load
                  @error="onDestImgError(poi)"
                />
                <view class="cy-dest-info">
                  <text class="cy-dest-name">{{ poi.name }}</text>
                  <text class="cy-dest-meta">{{ poi.distance || poi.category || '附近地点' }}</text>
                  <text class="cy-dest-reason">{{ poi.reason }}</text>
                </view>
                <view class="cy-dest-nav" @tap.stop="openNav(poi)">
                  <text>导航</text>
                </view>
              </view>
            </view>

            <!-- 建议气泡 chips（仅欢迎消息） -->
            <view v-if="msg.chips && msg.isWelcome" class="cy-chips-list">
              <view
                v-for="c in msg.chips"
                :key="c"
                class="cy-quick-chip"
                @tap="sendMsg(c)"
              >{{ c }}</view>
            </view>
          </view>

          <!-- 用户头像 -->
          <view v-if="msg.role === 'user'" class="cy-user-avatar">
            <image v-if="userAvatar" :src="userAvatar" class="cy-user-avatar-img" mode="aspectFill" />
            <view v-else class="cy-user-avatar-default">
              <CyIcon name="user-muted" :size="48" />
            </view>
          </view>
        </view>

        <!-- 打字中 -->
        <view v-if="typing" class="cy-msg-row bot">
          <view class="cy-bot-avatar">
            <cy-robot-mascot :size="72" />
          </view>
          <view class="cy-bubble cy-bubble--bot cy-typing-bubble">
            <view class="cy-dots">
              <view class="cy-dot" /><view class="cy-dot" /><view class="cy-dot" />
            </view>
          </view>
        </view>
      </view>
    </scroll-view>

    <!-- 输入区 -->
    <view class="cy-composer" :style="{ bottom: tabBarH + 'px' }">
      <view class="cy-input-bar">
        <input
          class="cy-msg-input"
          v-model="inputText"
          placeholder="问问附近适合去哪..."
          placeholder-style="color:#9CA3AF;"
          :adjust-position="true"
          confirm-type="send"
          @confirm="sendMsg(inputText)"
        />
        <view class="cy-input-tool" @tap="chooseImage">
          <CyIcon name="camera" :size="44" />
        </view>
        <view class="cy-send-btn" :class="{ 'cy-send-btn--active': inputText.length > 0 }" @tap="sendMsg(inputText)">
          <CyIcon name="send-green" :size="40" />
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, onUnmounted, watch } from 'vue'
import { onLoad, onShow } from '@dcloudio/uni-app'
import { api } from '../../api/index.js'
import { streamAsk } from '../../api/stream.js'
import { useCityStore } from '../../store/city.js'
import { getAssistantContext, getUserProfile } from '../../api/storage.js'
import { poiImage, routeImage } from '../../api/assets.js'
import { setTabBarSelected } from '../../api/tabbar.js'
import CyRobotMascot from '../../components/cy/cy-robot-mascot.vue'
import CyIcon from '../../components/cy/cy-icon.vue'

const cityStore = useCityStore()
const statusBarH  = ref(44)
const tabBarH     = ref(80)
const msgScrollH  = ref(400)
const scrollTop   = ref(0)
const inputText   = ref('')
const typing      = ref(false)
const brokenDest  = ref({})
const brokenRouteImgs = ref({})
const HISTORY_KEY = 'zhoumi_assistant_messages'

// 用 ref + onShow 刷新，避免登录后返回助手页头像不更新（computed 读非响应式 storage 不会重算）
const userAvatar = ref(getUserProfile()?.avatar || '')

const locLabel = computed(() => {
  const city = cityStore.current || chatContext.value.city || ''
  if (!city) return '当前位置附近'
  return cityStore.landmark ? `${city} · ${cityStore.landmark}附近` : `${city} · 附近`
})

const chatContext = ref({
  city: cityStore.current,
  lat: cityStore.coords?.lat ?? null,
  lng: cityStore.coords?.lng ?? null,
  weather: '', time_slot: '', scene: '', intent: '',
})

const defaultMessages = [
  { role: 'bot', text: '你好呀！我是出游助手，有什么可以帮你的吗？' },
  { role: 'bot', chips: ['带孩子2小时内去哪玩？', '雨天室内去哪？', '夜晚适合去哪里？', '低预算去哪？', '附近适合约会吗？'], isWelcome: true },
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
  chatContext.value = { city, lat, lng, weather: source.weather || '', time_slot: source.time_slot || '', scene: source.scene || '', intent: source.intent || '' }
}

onLoad((options) => { applyChatContext(options) })

onMounted(() => {
  try {
    const sys = uni.getWindowInfo()
    const statusH = sys.statusBarHeight || 44
    const safeB = Math.max(sys.safeAreaInsets?.bottom || 18, 18)
    const winH = sys.windowHeight || 600
    statusBarH.value = statusH
    tabBarH.value = safeB + 56
    const navH = 44 + statusH
    const composerH = 120
    msgScrollH.value = winH - navH - tabBarH.value - composerH
  } catch (_) {}
  uni.$on('assistantContext', applyChatContext)
  scrollToBottom()
})

onShow(() => { setTabBarSelected(2); applyChatContext(); userAvatar.value = getUserProfile()?.avatar || '' })
onUnmounted(() => { uni.$off('assistantContext', applyChatContext) })

function chooseImage() {
  uni.chooseMedia({
    count: 1,
    mediaType: ['image'],
    sourceType: ['album', 'camera'],
    success: (res) => {
      const tempPath = res.tempFiles[0]?.tempFilePath
      if (!tempPath) return
      // 显示图片气泡
      messages.value.push({ role: 'user', image: tempPath })
      scrollToBottom()
      typing.value = true
      // 读取 base64 发送给后端视觉接口
      const fs = uni.getFileSystemManager()
      fs.readFile({
        filePath: tempPath,
        encoding: 'base64',
        success: (fileRes) => {
          const botMsg = { role: 'bot', text: '', sources: null, chips: null, destinations: null, routes: null }
          messages.value.push(botMsg)
          api.askVision({
            image_base64: fileRes.data,
            city: chatContext.value.city,
            lat: chatContext.value.lat,
            lng: chatContext.value.lng,
          }).then(r => {
            botMsg.text = r?.answer || '图片已收到，暂时无法识别，请用文字描述你看到的地点。'
            botMsg.sources = r?.sources || null
            botMsg.destinations = r?.destinations || null
          }).catch(() => {
            botMsg.text = '图片识别失败，请用文字描述你想去的地方。'
          }).finally(() => {
            typing.value = false
            scrollToBottom()
          })
        },
        fail: () => {
          typing.value = false
          messages.value.push({ role: 'bot', text: '图片读取失败，请重试。' })
          scrollToBottom()
        },
      })
    },
  })
}

function sendMsg(text) {
  const q = text?.trim()
  if (!q) return
  const history = messages.value
    .filter(m => m.text && (m.role === 'user' || m.role === 'bot'))
    .slice(-12)
    .map(m => ({ role: m.role, text: m.text }))
  messages.value.push({ role: 'user', text: q })
  inputText.value = ''
  typing.value = true
  scrollToBottom()

  const botMsg = { role: 'bot', text: '' }
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

  // #ifdef MP-WEIXIN
  // 微信小程序的分块流式（无原生 fetch、onChunkReceived 时序不稳）经常拿不到内容 → 空气泡。
  // 直接走非流式接口，确保有回复（H5 仍用流式打字机效果）。
  fallbackNonStream(payload)
  return
  // #endif

  streamAsk(payload, {
    onMeta: (meta) => {
      botMsg.sources = meta?.sources || null
      botMsg.destinations = meta?.destinations || null
      botMsg.routes = meta?.routes || null
      typing.value = false
      messages.value.push(botMsg)
      started = true
      scrollToBottom()
    },
    onText: (t) => { botMsg.text = t; scrollToBottom() },
    onChunk: (t) => { botMsg.text = (botMsg.text || '') + t; scrollToBottom() },
    onDone: () => { typing.value = false; if (!started) fallbackNonStream(payload) },
    onError: () => { typing.value = false; if (!started) fallbackNonStream(payload) },
  })
}

function fallbackNonStream(payload) {
  api.ask(payload)
    .then((res) => {
      typing.value = false
      messages.value.push({
        role: 'bot',
        text: res.text || '抱歉，这次没有获取到回复，请换个说法再试。',
        sources: res.sources || null,
        destinations: res.destinations || null,
        routes: res.routes || null,
      })
      scrollToBottom()
    })
    .catch(() => {
      typing.value = false
      messages.value.push({ role: 'bot', text: '暂时无法连接助手，请稍后再试。' })
      scrollToBottom()
    })
}

function scrollToBottom() { nextTick(() => { scrollTop.value = 99999 }) }

function goPoi(id, poi) {
  try { uni.setStorageSync('currentPoiPreview', poi) } catch (_) {}
  uni.navigateTo({ url: `/pages/poi/detail?id=${id}` })
}

function openNav(poi) {
  if (poi.lat && poi.lng) {
    uni.openLocation({ latitude: Number(poi.lat), longitude: Number(poi.lng), name: poi.name })
  }
}

function openRoute(route) {
  try { uni.setStorageSync('currentRoute', route) } catch (_) {}
  uni.navigateTo({ url: '/pages/routes/detail' })
}

function imgKey(item) { return String(item?.id ?? item?.name ?? item?.title ?? '') }
function destinationThumb(poi) { return poiImage(poi, brokenDest.value[imgKey(poi)] || 0) }
function onDestImgError(poi) { const k = imgKey(poi); brokenDest.value = { ...brokenDest.value, [k]: (brokenDest.value[k] || 0) + 1 } }
function assistantRouteThumb(route) { return routeImage(route, Boolean(brokenRouteImgs.value[imgKey(route)])) }
function onRouteImgError(route) { brokenRouteImgs.value = { ...brokenRouteImgs.value, [imgKey(route)]: true } }
</script>

<style lang="scss">
@import '../../uni.scss';

.cy-page {
  min-height: 100vh;
  background: $cy-bg;
  font-family: "PingFang SC", "HarmonyOS Sans SC", "Noto Sans SC", -apple-system, system-ui, sans-serif;
}

// ── Header ─────────────────────────────────────────────────
.cy-chat-header {
  background: #fff;
  padding: 12rpx 28rpx 16rpx;
  border-bottom: 1rpx solid $cy-border;
}

.cy-chat-title {
  display: block;
  font-size: 34rpx;
  font-weight: 800;
  color: $cy-green-d;
}

.cy-chat-loc {
  display: flex;
  align-items: center;
  gap: 4rpx;
  margin-top: 4rpx;
}

.cy-chat-loc-text {
  font-size: 24rpx;
  color: $cy-green;
  font-weight: 500;
}

// ── 消息区 ─────────────────────────────────────────────────
.cy-msg-scroll { flex: 1; }

.cy-msg-list {
  display: flex;
  flex-direction: column;
  padding: 16rpx 0 24rpx;
}

.cy-msg-row {
  display: flex;
  align-items: flex-end;
  gap: 12rpx;
  padding: 0 24rpx;
  margin-bottom: 20rpx;

  &.user { flex-direction: row-reverse; }
}

.cy-bot-avatar {
  width: 72rpx;
  height: 72rpx;
  flex-shrink: 0;
}

.cy-bubble-wrap {
  max-width: 75%;
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}

.cy-bubble {
  border-radius: 24rpx;
  padding: 20rpx 24rpx;
  font-size: 28rpx;
  line-height: 1.6;

  &--bot {
    background: #F0EDE6;
    color: $cy-text;
    border-bottom-left-radius: 6rpx;
  }

  &--user {
    background: $cy-green-l;
    color: $cy-green-d;
    border-bottom-right-radius: 6rpx;
  }

  &--img {
    padding: 0;
    overflow: hidden;
    background: transparent;
  }
}

.cy-msg-image {
  width: 360rpx;
  max-width: 100%;
  border-radius: 24rpx;
  border-bottom-right-radius: 6rpx;
  display: block;
}

// ── 建议 chips ──────────────────────────────────────────────
.cy-chips-list {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}

.cy-quick-chip {
  background: $cy-green-l;
  color: $cy-green-d;
  border-radius: 20rpx;
  padding: 14rpx 24rpx;
  font-size: 26rpx;
  font-weight: 500;
  cursor: pointer;
}

// ── 数据源 ──────────────────────────────────────────────────
.cy-sources-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8rpx;
}

.cy-source-badge {
  background: #F3F4F6;
  border-radius: 8rpx;
  padding: 4rpx 12rpx;
  font-size: 20rpx;
  color: $cy-muted;
}

// ── 推荐卡 ─────────────────────────────────────────────────
.cy-dest-cards {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
  background: #F0EDE6;
  border-radius: 28rpx;
  padding: 24rpx;
}

.cy-dest-card,
.cy-route-card {
  background: #fff;
  border-radius: 16rpx;
  padding: 16rpx;
  display: flex;
  gap: 16rpx;
  align-items: center;
  cursor: pointer;
}

.cy-dest-thumb {
  width: 112rpx;
  height: 100rpx;
  border-radius: 12rpx;
  flex-shrink: 0;
  background: $cy-green-ls;
}

.cy-dest-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}

.cy-dest-name  { font-size: 28rpx; font-weight: 700; color: $cy-text; }
.cy-dest-meta  { font-size: 22rpx; color: $cy-muted; }
.cy-dest-reason {
  font-size: 22rpx;
  color: $cy-text-sub;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cy-dest-nav {
  padding: 14rpx 28rpx;
  border-radius: 16rpx;
  background: $cy-green-d;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26rpx;
  font-weight: 600;
  flex-shrink: 0;
}

// ── 打字中 ──────────────────────────────────────────────────
.cy-typing-bubble { padding: 24rpx 32rpx; }

.cy-dots {
  display: flex;
  gap: 8rpx;
  align-items: center;
}

.cy-dot {
  width: 12rpx;
  height: 12rpx;
  border-radius: 6rpx;
  background: $cy-muted;
  animation: cy-dot-bounce 1.4s infinite ease-in-out;

  &:nth-child(2) { animation-delay: 0.2s; }
  &:nth-child(3) { animation-delay: 0.4s; }
}

@keyframes cy-dot-bounce {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-8rpx); }
}

// ── 用户头像 ───────────────────────────────────────────────
.cy-user-avatar {
  width: 72rpx;
  height: 72rpx;
  border-radius: 36rpx;
  overflow: hidden;
  flex-shrink: 0;
  background: #F3F4F6;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cy-user-avatar-img { width: 100%; height: 100%; }
.cy-user-avatar-default { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; }

// ── 输入区 ─────────────────────────────────────────────────
.cy-composer {
  position: fixed;
  left: 0;
  right: 0;
  background: rgba(255,255,255,0.97);
  backdrop-filter: blur(12px);
  padding: 12rpx 24rpx;
  border-top: 1rpx solid $cy-border;
  z-index: 98;
}

.cy-input-bar {
  background: #F3F4F6;
  border-radius: 50rpx;
  height: 88rpx;
  display: flex;
  align-items: center;
  padding: 0 16rpx;
  gap: 8rpx;
}

.cy-msg-input {
  flex: 1;
  height: 100%;
  font-size: 28rpx;
  color: $cy-text;
  background: transparent;
  padding: 0 8rpx;
}

.cy-input-tool {
  width: 56rpx;
  height: 56rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cy-send-btn {
  width: 64rpx;
  height: 64rpx;
  border-radius: 32rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  transition: background 0.15s;

  &--active { background: $cy-green-l; }
}
</style>
