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
      </view>
    </view>

    <!-- 消息区 -->
    <scroll-view
      scroll-y
      class="msg-scroll"
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

    <!-- FAQ 快捷条 -->
    <scroll-view scroll-x class="faq-scroll" :show-scrollbar="false">
      <view class="faq-row">
        <view v-for="faq in faqs" :key="faq" class="faq-chip" @tap="sendMsg(faq)">{{ faq }}</view>
      </view>
    </scroll-view>

    <!-- 输入区 -->
    <view class="input-bar" :style="{ paddingBottom: safeBottom }">
      <view class="input-wrap">
        <input
          class="msg-input"
          v-model="inputText"
          placeholder="问问附近适合去哪…"
          placeholder-style="color: #8B9594;"
          :adjust-position="true"
          @confirm="sendMsg(inputText)"
        />
        <view class="send-btn" :class="{ active: inputText.length > 0 }" @tap="sendMsg(inputText)">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 26 26" fill="none">
            <path d="M3 13l8 4 4 8 7-19-19 7z" fill="#fff"/>
          </svg>
        </view>
      </view>
    </view>

    <z-tab-bar current="assistant" />
  </view>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import ZTabBar from '../../components/ZTabBar.vue'
import { api } from '../../api/mock.js'

const statusBarHeight = ref(44)
const safeBottom      = ref('18px')
const scrollTop       = ref(0)
const inputText       = ref('')
const typing          = ref(false)

const faqs = ['钓点限钓吗？', '需要钓鱼证吗？', '停车方便吗？', '下雨改去哪？', '适合带孩子吗？', '傍晚还能玩什么？']

const messages = ref([
  { role: 'bot', text: '你好👋 我是周密出游助手，可以帮你规划路线、查询地点、解决出游疑问。' },
  { role: 'bot', chips: ['钓点限钓吗？', '需要钓鱼证吗？', '停车方便吗？', '下雨改去哪？'] },
])

onMounted(() => {
  try {
    const sys = uni.getSystemInfoSync()
    statusBarHeight.value = sys.statusBarHeight || 44
    safeBottom.value = Math.max(sys.safeAreaInsets?.bottom || 18, 18) + 'px'
  } catch (_) {}
})

function sendMsg(text) {
  if (!text?.trim()) return
  messages.value.push({ role: 'user', text: text.trim() })
  inputText.value = ''
  typing.value = true

  scrollToBottom()

  api.ask(text.trim())
    .then((res) => {
      typing.value = false
      messages.value.push({
        role: 'bot',
        text: res.text,
        sources: res.sources,
        chips: res.chips,
      })
      scrollToBottom()
    })
    .catch(() => {
      typing.value = false
      messages.value.push({ role: 'bot', text: '网络异常，请稍后重试。' })
      scrollToBottom()
    })
}

function scrollToBottom() {
  nextTick(() => { scrollTop.value = 99999 })
}
</script>

<style lang="scss">
@import '../../uni.scss';

.page {
  height: 100vh;
  display: flex;
  flex-direction: column;
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

.bot-avatar {
  width: 76rpx;
  height: 76rpx;
  border-radius: 38rpx;
  background: linear-gradient(135deg, #0D4F4A 0%, #2A8278 100%);
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
  background: #22C55E;
  border: 2rpx solid #fff;
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
  flex: 1;
  overflow: hidden;
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
  background: linear-gradient(135deg, #0D4F4A 0%, #2A8278 100%);
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
    background: #0D4F4A;
    color: #fff;
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
  color: #0D4F4A;
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
  color: #0D4F4A;
  font-weight: 700;
  letter-spacing: 0.5rpx;
}

.source-v {
  font-size: 20rpx;
  color: $z-muted;
}

// FAQ
.faq-scroll {
  flex-shrink: 0;
  background: $z-card;
  border-top: 1rpx solid $z-line;
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
  border-top: 1rpx solid $z-border;
  padding: 16rpx 24rpx;
  flex-shrink: 0;
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
    background: #0D4F4A;
  }
}
</style>
