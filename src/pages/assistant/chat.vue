<template>
  <view class="page">
    <!-- Header -->
    <view class="header" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="header-inner">
        <view class="bot-avatar">🤖<view class="online-dot" /></view>
        <view class="header-text">
          <text class="header-title serif">出游助手</text>
          <text class="header-sub mono">本地知识库 · 在线</text>
        </view>
        <view class="header-clear" @tap="clearHistory">清空</view>
      </view>
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
          <view v-if="msg.role === 'bot'" class="bot-bubble-avatar">🤖</view>
          <view class="bubble-wrap" :class="msg.role">
            <view v-if="msg.text" class="bubble" :class="msg.role">
              <text>{{ msg.text }}</text>
            </view>
            <!-- Bot 快捷 chips -->
            <view v-if="msg.chips" class="chips-row">
              <view v-for="c in msg.chips" :key="c" class="quick-chip" @tap="sendMsg(c)">{{ c }}</view>
            </view>
            <!-- 数据源徽章 -->
            <view v-if="msg.sources" class="sources-row">
              <view v-for="s in msg.sources" :key="s.k" class="source-badge">
                <text class="source-k mono">[{{ s.k }}]</text>
                <text class="source-v">{{ s.v }}</text>
              </view>
            </view>
            <view v-if="msg.destinations?.length" class="assistant-cards">
              <view
                v-for="poi in msg.destinations"
                :key="poi.id"
                class="assistant-poi"
                @tap="openNav(poi)"
              >
                <view class="assistant-poi-main">
                  <text class="assistant-poi-name serif">{{ poi.name }}</text>
                  <text class="assistant-poi-meta">{{ poi.category || '地点' }} · {{ poi.distance }}</text>
                  <text class="assistant-poi-reason">{{ poi.reason }}</text>
                </view>
                <view class="assistant-nav">导航</view>
              </view>
            </view>
            <view v-if="msg.routes?.length" class="assistant-cards">
              <view
                v-for="route in msg.routes"
                :key="route.id"
                class="assistant-route"
                @tap="openRoute(route)"
              >
                <text class="assistant-poi-name serif">{{ route.title }}</text>
                <text class="assistant-poi-meta">{{ route.duration }} · {{ route.stops?.length || 0 }}站</text>
              </view>
            </view>
          </view>
        </view>

        <!-- 打字中 -->
        <view v-if="typing" class="msg-row bot">
          <view class="bot-bubble-avatar">🤖</view>
          <view class="bubble bot typing-bubble">
            <view class="typing-dots">
              <view class="dot" /><view class="dot" /><view class="dot" />
            </view>
          </view>
        </view>
      </view>
    </scroll-view>

    <!-- 底部输入区（fixed 在 tab-bar 上方）-->
    <view class="composer" :style="{ bottom: tabBarHeight + 'px' }">
      <!-- FAQ 快捷条 -->
      <scroll-view scroll-x class="faq-scroll" :show-scrollbar="false">
        <view class="faq-row">
          <view v-for="faq in faqs" :key="faq" class="faq-chip" @tap="sendMsg(faq)">{{ faq }}</view>
        </view>
      </scroll-view>

      <!-- 输入区 -->
      <view class="input-bar">
        <view class="input-wrap">
          <input
            class="msg-input"
            v-model="inputText"
            placeholder="问问附近适合去哪…"
            placeholder-style="color: #8B9594;"
            :adjust-position="true"
            confirm-type="send"
            @confirm="sendMsg(inputText)"
          />
          <view class="send-btn" :class="{ active: inputText.length > 0 }" @tap="sendMsg(inputText)">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 26 26" fill="none">
              <path d="M3 13l8 4 4 8 7-19-19 7z" fill="#fff"/>
            </svg>
          </view>
        </view>
      </view>
    </view>

    <z-tab-bar current="assistant" />
  </view>
</template>

<script setup>
import { ref, nextTick, onMounted, watch } from 'vue'
import ZTabBar from '../../components/ZTabBar.vue'
import { api } from '../../api/mock.js'
import { streamAsk } from '../../api/stream.js'
import { useCityStore } from '../../store/city.js'

const cityStore = useCityStore()

const statusBarHeight = ref(44)
const tabBarHeight    = ref(80)        // ZTabBar 占用高度（含 safeArea）
const msgScrollH      = ref(400)       // 消息滚动区显式高度，避免被遮挡
const scrollTop       = ref(0)
const inputText       = ref('')
const typing          = ref(false)
const HISTORY_KEY     = 'zhoumi_assistant_messages'

const faqs = ['钓点限钓吗？', '需要钓鱼证吗？', '停车方便吗？', '下雨改去哪？', '适合带孩子吗？', '傍晚还能玩什么？']

const defaultMessages = [
  { role: 'bot', text: '你好👋 我是周密出游助手，可以帮你规划路线、查询地点、解决出游疑问。' },
  { role: 'bot', chips: ['钓点限钓吗？', '需要钓鱼证吗？', '停车方便吗？', '下雨改去哪？'] },
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

function clearHistory() {
  uni.showModal({
    title: '清空对话',
    content: '将删除所有聊天记录，仅保留欢迎语。是否继续？',
    confirmText: '清空',
    confirmColor: '#E55B45',
    success: ({ confirm }) => {
      if (!confirm) return
      try { uni.removeStorageSync(HISTORY_KEY) } catch (_) {}
      messages.value = defaultMessages.map(item => ({ ...item }))
      uni.showToast({ title: '已清空', icon: 'success' })
    },
  })
}

onMounted(() => {
  try {
    const sys = uni.getSystemInfoSync()
    const statusH = sys.statusBarHeight || 44
    const safeB   = Math.max(sys.safeAreaInsets?.bottom || 18, 18)
    const winH    = sys.windowHeight || (sys.screenHeight - statusH) || 600
    statusBarHeight.value = statusH
    // ZTabBar = paddingTop 12rpx(~6px) + icon 行 ~50px + paddingBottom safeArea
    const tabH = safeB + 56
    tabBarHeight.value = tabH
    // header 实际高度：paddingTop(statusH) + 头像行 ~52 + paddingBottom 12 ≈ statusH + 64
    const headerH = statusH + 64
    // composer 高度：faq 行 ~50 + input 行 ~70 + 安全区
    const composerH = 50 + 70 + safeB
    msgScrollH.value = Math.max(200, winH - headerH - tabH - composerH)
  } catch (_) {}
})

function sendMsg(text) {
  const q = text?.trim()
  if (!q) return

  // 取本轮发送前的最近 6 条 user/bot 消息作为多轮上下文（不含本次新问题）
  const history = messages.value
    .filter(m => m.text && (m.role === 'user' || m.role === 'bot'))
    .slice(-6)
    .map(m => ({ role: m.role, text: m.text }))

  messages.value.push({ role: 'user', text: q })
  inputText.value = ''
  typing.value = true
  scrollToBottom()

  // 占位 bot 消息（流式期间逐字追加）
  const botMsg = { role: 'bot', text: '', sources: null, chips: null, destinations: null, routes: null }
  let started = false
  const payload = {
    question: q,
    city: cityStore.current,
    lat: cityStore.coords?.lat,
    lng: cityStore.coords?.lng,
    intent: 'assistant',
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
      // 命中知识库/缓存：一次性显示整段
      botMsg.text = t
      scrollToBottom()
    },
    onChunk: (t) => {
      botMsg.text = (botMsg.text || '') + t
      scrollToBottom()
    },
    onDone: () => {
      typing.value = false
      if (!started) {
        // 流没起来（meta 都没收到）→ 降级
        fallbackNonStream(q)
      }
    },
    onError: () => {
      typing.value = false
      if (!started) {
        fallbackNonStream(q)
      } else {
        botMsg.text = (botMsg.text || '') + '\n[连接中断]'
      }
    },
  })

  function fallbackNonStream(q) {
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
        messages.value.push({ role: 'bot', text: '网络异常，请稍后重试。' })
        scrollToBottom()
      })
  }
}

function scrollToBottom() {
  nextTick(() => { scrollTop.value = 99999 })
}

function openNav(poi) {
  if (!poi?.nav_ready || poi.lat == null || poi.lng == null) {
    uni.showToast({ title: '该地点暂无可用坐标', icon: 'none' })
    return
  }
  uni.openLocation({
    latitude: Number(poi.lat),
    longitude: Number(poi.lng),
    name: poi.name,
    address: poi.address || poi.category || '',
  })
}

function openRoute(route) {
  const stop = (route?.stops || []).find(s => s.lat != null && s.lng != null)
  if (!stop) {
    uni.showToast({ title: '该路线暂无可导航站点', icon: 'none' })
    return
  }
  uni.openLocation({
    latitude: Number(stop.lat),
    longitude: Number(stop.lng),
    name: stop.name,
    address: stop.reason || '',
  })
}
</script>

<style lang="scss">
@import '../../uni.scss';

.page {
  min-height: 100vh;
  background: $z-bg;
}

.header {
  background: $z-card;
  padding: 0 32rpx 24rpx;
  border-bottom: 1rpx solid $z-border;
  flex-shrink: 0;
}

.header-inner {
  display: flex;
  align-items: center;
  gap: 20rpx;
  padding-top: 16rpx;
}

.header-text { flex: 1; min-width: 0; }
.header-clear {
  padding: 8rpx 20rpx;
  border: 1rpx solid $z-border;
  border-radius: 22rpx;
  font-size: 24rpx;
  color: $z-muted;
  background: $z-card;
  flex-shrink: 0;
}

.bot-avatar {
  width: 76rpx;
  height: 76rpx;
  border-radius: 38rpx;
  background: linear-gradient(135deg, $z-primary 0%, $z-primary-l 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36rpx;
  position: relative;
  flex-shrink: 0;
}

.online-dot {
  position: absolute;
  bottom: 2rpx;
  right: 2rpx;
  width: 16rpx;
  height: 16rpx;
  border-radius: 8rpx;
  background: $z-success;
  border: 2rpx solid $z-card;
}

.header-title {
  display: block;
  font-size: 30rpx;
  font-weight: 800;
  color: $z-text;
}

.header-sub {
  display: block;
  font-size: 20rpx;
  color: $z-muted;
  letter-spacing: 1rpx;
  margin-top: 4rpx;
}

.msg-scroll {
  background: $z-bg;
}

.msg-list {
  padding: 24rpx 24rpx 24rpx;
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.msg-row {
  display: flex;
  align-items: flex-start;
  gap: 12rpx;

  &.user {
    flex-direction: row-reverse;
  }
}

.bot-bubble-avatar {
  width: 60rpx;
  height: 60rpx;
  border-radius: 30rpx;
  background: linear-gradient(135deg, $z-primary 0%, $z-primary-l 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26rpx;
  flex-shrink: 0;
}

.bubble-wrap {
  max-width: 75%;
  display: flex;
  flex-direction: column;
  gap: 10rpx;

  &.user { align-items: flex-end; }
}

.bubble {
  padding: 20rpx 24rpx;
  border-radius: 24rpx;
  font-size: 26rpx;
  line-height: 1.55;

  &.bot {
    background: $z-card;
    color: $z-text;
    border-bottom-left-radius: 6rpx;
    box-shadow: 0 2rpx 8rpx rgba(13, 79, 74, 0.06);
  }

  &.user {
    background: $z-primary;
    color: $z-card;
    border-bottom-right-radius: 6rpx;
  }
}

.typing-bubble {
  padding: 20rpx 28rpx;
}

.typing-dots {
  display: flex;
  gap: 10rpx;
  align-items: center;
}

.dot {
  width: 10rpx;
  height: 10rpx;
  border-radius: 5rpx;
  background: $z-muted;
  animation: dotBounce 1.4s ease-in-out infinite;

  &:nth-child(2) { animation-delay: 0.2s; }
  &:nth-child(3) { animation-delay: 0.4s; }
}

@keyframes dotBounce {
  0%, 80%, 100% { transform: scale(1); opacity: 0.5; }
  40%            { transform: scale(1.4); opacity: 1; }
}

.chips-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx;
}

.quick-chip {
  padding: 10rpx 20rpx;
  background: rgba(13, 79, 74, 0.08);
  border: 1rpx solid rgba(13, 79, 74, 0.2);
  border-radius: $radius-pill;
  font-size: 23rpx;
  color: $z-primary;
  cursor: pointer;
}

.sources-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8rpx;
}

.source-badge {
  display: flex;
  align-items: center;
  gap: 6rpx;
  background: $z-bg;
  border-radius: 8rpx;
  padding: 6rpx 12rpx;
}

.source-k {
  font-size: 18rpx;
  color: $z-primary;
  font-weight: 700;
  letter-spacing: 0.5rpx;
}

.source-v {
  font-size: 20rpx;
  color: $z-muted;
}

// Composer（FAQ + 输入栏一起 fixed 在 TabBar 上方）
.composer {
  position: fixed;
  left: 0;
  right: 0;
  z-index: 1000;
  background: $z-card;
  border-top: 1rpx solid $z-border;
  box-shadow: 0 -4rpx 16rpx rgba(0, 0, 0, 0.05);
}

// FAQ
.faq-scroll {
  background: $z-card;
  border-bottom: 1rpx solid $z-line;
  padding: 12rpx 0;
}

.faq-row {
  display: flex;
  gap: 12rpx;
  padding: 0 24rpx;
  white-space: nowrap;
}

.faq-chip {
  display: inline-block;
  padding: 10rpx 22rpx;
  background: $z-bg;
  border-radius: $radius-pill;
  font-size: 23rpx;
  color: $z-text2;
  cursor: pointer;
  flex-shrink: 0;
}

// 输入区
.input-bar {
  background: $z-card;
  padding: 16rpx 24rpx 24rpx;
}

.input-wrap {
  display: flex;
  align-items: center;
  gap: 16rpx;
  background: $z-bg;
  border-radius: $radius-pill;
  padding: 12rpx 16rpx 12rpx 28rpx;
}

.msg-input {
  flex: 1;
  font-size: 26rpx;
  color: $z-text;
  background: transparent;
  border: none;
}

.send-btn {
  width: 64rpx;
  height: 64rpx;
  border-radius: 32rpx;
  background: $z-muted;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: background 0.2s;

  &.active {
    background: $z-primary;
  }
}

.assistant-cards {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.assistant-poi,
.assistant-route {
  background: $z-card;
  border: 1rpx solid $z-border;
  border-radius: 16rpx;
  padding: 18rpx;
  box-shadow: 0 2rpx 8rpx rgba(13, 79, 74, 0.06);
}

.assistant-poi {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.assistant-poi-main {
  flex: 1;
  min-width: 0;
}

.assistant-poi-name {
  display: block;
  font-size: 25rpx;
  font-weight: 800;
  color: $z-text;
  margin-bottom: 4rpx;
}

.assistant-poi-meta,
.assistant-poi-reason {
  display: block;
  font-size: 21rpx;
  color: $z-muted;
  line-height: 1.4;
}

.assistant-poi-reason {
  color: $z-text2;
  margin-top: 6rpx;
}

.assistant-nav {
  height: 54rpx;
  padding: 0 18rpx;
  border-radius: 12rpx;
  background: $z-primary;
  color: $z-card;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22rpx;
  font-weight: 800;
  flex-shrink: 0;
}
</style>
