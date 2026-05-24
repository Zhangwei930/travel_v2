<template>
  <view class="page">
    <!-- Header -->
    <view class="header" :style="{ paddingTop: statusBarHeight + 'px' }">
      <text class="header-mono mono">§ GENERATE</text>
      <text class="header-title serif">一键生成方案</text>
      <text class="header-sub">告诉我你的偏好 · AI 帮你规划可执行路线</text>
    </view>

    <!-- 加载中态 -->
    <view v-if="loading" class="loading-screen">
      <view class="loading-compass">
        <view class="compass-spin">
          <svg xmlns="http://www.w3.org/2000/svg" width="38" height="38" viewBox="0 0 26 26" fill="none">
            <path d="M3 13l8 4 4 8 7-19-19 7z" fill="#fff"/>
          </svg>
        </view>
      </view>
      <text class="loading-title serif">规划中…</text>
      <text class="loading-progress mono">预计 {{ etaSec }} 秒 · {{ progress }}%</text>
      <text v-if="slowTip" class="loading-slow-tip">AI 正在深度分析，再等一下～</text>

      <view class="steps-card">
        <view
          v-for="(step, i) in steps"
          :key="step.k"
          class="step-row"
          :style="{ opacity: i > currentStep ? 0.4 : 1 }"
        >
          <view class="step-dot" :class="{ done: i < currentStep, doing: i === currentStep }">
            <!-- done -->
            <svg v-if="i < currentStep" width="10" height="10" viewBox="0 0 10 10">
              <path d="M2 5l2 2 4-4" stroke="#fff" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <!-- doing -->
            <view v-else-if="i === currentStep" class="dot-pulse" />
            <!-- pending -->
            <text v-else class="step-no mono">{{ step.k }}</text>
          </view>
          <text class="step-label" :style="{ fontWeight: i === currentStep ? '700' : '500', color: i === currentStep ? '#1A2E2C' : '#8B9594' }">{{ step.t }}</text>
        </view>
      </view>

      <view class="progress-bar-wrap">
        <view class="progress-bar-fill" :style="{ width: progress + '%' }" />
      </view>
    </view>

    <!-- 填写态 -->
    <scroll-view v-else scroll-y class="scroll-body" :show-scrollbar="false">
      <view class="form-wrap">
        <!-- Q1-Q5 in one card -->
        <view class="form-card">
          <view class="q-group" v-for="q in questions" :key="q.no">
            <view class="q-head">
              <text class="q-no mono">Q{{ q.no }}</text>
              <text class="q-label serif">{{ q.label }}</text>
              <text v-if="q.hint" class="q-hint">· {{ q.hint }}</text>
            </view>
            <view class="chips-wrap">
              <view
                v-for="opt in q.options"
                :key="opt"
                class="form-chip"
                :class="{ on: isSelected(q, opt) }"
                @tap="toggle(q, opt)"
              >
                <text>{{ opt }}</text>
              </view>
            </view>
          </view>
        </view>

        <!-- Q6 自然语言 -->
        <view class="form-card q6-card">
          <view class="q-head">
            <text class="q-no mono">Q6</text>
            <text class="q-label serif">还想补充什么？</text>
            <text class="q-hint">· 可选 · 自然语言</text>
          </view>
          <textarea
            class="custom-textarea"
            v-model="customText"
            placeholder="例如：希望钓点风小、人少，孩子可以玩水但要安全"
            placeholder-style="color: #8B9594; font-size: 25rpx;"
            :maxlength="200"
            auto-height
          />
        </view>

        <!-- 汇总条 -->
        <view class="summary-bar">
          <text class="summary-mono mono">※ 我将基于以下条件规划</text>
          <text class="summary-content">
            {{ form.time }} · {{ form.people }} · {{ form.budget }} · {{ form.transport }}
            <text v-if="form.prefs.length" class="summary-prefs"> · {{ form.prefs.join(' / ') }}</text>
          </text>
        </view>

        <!-- 主 CTA -->
        <view class="cta-btn" @tap="startGenerate">
          <text class="cta-text serif">🧭 开始规划出游方案</text>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { api } from '../../api/mock.js'
import { useCityStore } from '../../store/city.js'

const cityStore = useCityStore()

// 确保有坐标（用户没经过首页直接来 generate 的场景）
async function ensureCoords() {
  if (cityStore.coords?.lat != null) return
  try {
    const r = await new Promise((resolve) => {
      uni.getLocation({ type: 'gcj02', success: resolve, fail: () => resolve({}) })
    })
    if (r.latitude != null && r.longitude != null) {
      cityStore.setCoords(r.latitude, r.longitude)
      try {
        const g = await api.geoCity(r.latitude, r.longitude)
        if (g?.city) cityStore.setFromLocation(g.city)
      } catch (_) {}
    }
  } catch (_) {}
}

const statusBarHeight = ref(44)
const capability = ref(null)  // 后端能力开关：决定显示哪些生成步骤

onMounted(async () => {
  try { statusBarHeight.value = uni.getSystemInfoSync().statusBarHeight || 44 } catch (_) {
    console.warn('getSystemInfoSync failed')
  }
  try { capability.value = await api.getCapability() } catch (e) {
    console.warn('getCapability failed', e)
  }
})
const loading     = ref(false)
const progress    = ref(0)
const currentStep = ref(0)
const slowTip     = ref(false)
const customText  = ref('')

const form = ref({
  time:      '周六清晨',
  people:    '2人',
  budget:    '200元以内',
  transport: '自驾',
  prefs:     ['钓鱼', '自然'],
})

const questions = [
  { no: 1, label: '什么时间',   hint: '今天 / 明天 / 周末…', key: 'time',      multi: false, options: ['今天', '明天', '周六清晨', '周日全天', '晚上'] },
  { no: 2, label: '和谁一起',   hint: '',                    key: 'people',    multi: false, options: ['一人', '情侣', '亲子', '朋友', '带老人', '2人'] },
  { no: 3, label: '预算',       hint: '',                    key: 'budget',    multi: false, options: ['免费', '100元以内', '200元以内', '300元以内', '不限'] },
  { no: 4, label: '出行方式',   hint: '',                    key: 'transport', multi: false, options: ['步行', '自驾', '打车', '公交/地铁'] },
  { no: 5, label: '其他偏好',   hint: '可多选',               key: 'prefs',     multi: true,  options: ['室内', '户外', '钓鱼', '自然', '拍照', '不太累', '美食', '带娃友好', '安静'] },
]

// 步骤根据后端 capability 动态生成，避免误导用户"已启用 AI"但其实是 stub
const steps = computed(() => {
  const c = capability.value || {}
  const list = [{ k: '01', t: '解析你的需求' }]
  if (c.map_amap !== false) list.push({ k: String(list.length + 1).padStart(2, '0'), t: '高德地图 · 查询附近 POI' })
  list.push({ k: String(list.length + 1).padStart(2, '0'), t: '知识库检索 · 路线模板匹配' })
  if (c.websearch) list.push({ k: String(list.length + 1).padStart(2, '0'), t: 'WebSearch · 补充最新信息' })
  if (c.ai) list.push({ k: String(list.length + 1).padStart(2, '0'), t: 'AI · 生成攻略文案' })
  list.push({ k: String(list.length + 1).padStart(2, '0'), t: '质量校验 · 风险检查' })
  return list
})

const etaSec = computed(() => Math.max(0, Math.ceil((100 - progress.value) / 22)))

function isSelected(q, opt) {
  if (q.multi) return form.value[q.key].includes(opt)
  return form.value[q.key] === opt
}

function toggle(q, opt) {
  if (q.multi) {
    const arr = form.value[q.key]
    form.value[q.key] = arr.includes(opt) ? arr.filter(x => x !== opt) : [...arr, opt]
  } else {
    form.value[q.key] = opt
  }
}

let progressTimer, stepTimer, slowTipTimer

const SCENE_MAP = {
  钓鱼: 'fish', 拍照: 'photo', 室内: 'rainy', 带娃友好: 'family', 美食: 'couple', 安静: 'walk',
}

async function startGenerate() {
  await ensureCoords()
  loading.value   = true
  progress.value  = 0
  currentStep.value = 0
  slowTip.value   = false
  slowTipTimer = setTimeout(() => { slowTip.value = true }, 8000)

  // 调用后端生成攻略，结果存入本地缓存供结果页读取
  const scene = form.value.prefs.map(p => SCENE_MAP[p]).find(Boolean) || ''
  const preferences = customText.value.trim()
    ? [...form.value.prefs, customText.value.trim()]
    : form.value.prefs
  progressTimer = setInterval(() => {
    const remaining = 90 - progress.value
    progress.value = Math.min(90, progress.value + remaining * 0.08 + Math.random() * 3)
  }, 320)

  stepTimer = setInterval(() => {
    if (currentStep.value < steps.length - 1) currentStep.value++
  }, 720)

  api.generateTrip({
    city: cityStore.current,
    lat: cityStore.coords?.lat ?? null,   // 真实坐标，后端用于附近知名景点筛选
    lng: cityStore.coords?.lng ?? null,
    time: form.value.time,
    people_type: form.value.people,
    budget: form.value.budget,
    transport: form.value.transport,
    preferences,
    scene,
  }).then((plan) => {
    // 响应结构校验：必须有 stops 数组且非空，必须有 no/title
    if (!plan || !Array.isArray(plan.stops) || plan.stops.length === 0 || !plan.no || !plan.title) {
      throw new Error('plan-invalid')
    }
    uni.setStorageSync('lastPlan', plan)
    cleanupTimers()
    progress.value    = 100
    currentStep.value = steps.length - 1
    setTimeout(() => {
      // URL 携带 plan.no — 支持刷新、深链、换设备打开
      uni.navigateTo({ url: `/pages/result/result?generated=1&no=${encodeURIComponent(plan.no)}` })
      loading.value = false
    }, 500)
  }).catch((err) => {
    cleanupTimers()
    loading.value  = false
    progress.value = 0
    currentStep.value = 0
    const msg = err?.message === 'plan-invalid' ? '生成结果不完整，请重试' : '生成失败，请检查网络后重试'
    uni.showToast({ title: msg, icon: 'none', duration: 2000 })
  })

  function cleanupTimers() {
    clearInterval(progressTimer)
    clearInterval(stepTimer)
    clearTimeout(slowTipTimer)
    slowTip.value = false
  }
}

// 离开时清理
onUnmounted(() => {
  clearInterval(progressTimer)
  clearInterval(stepTimer)
  clearTimeout(slowTipTimer)
})
</script>

<style lang="scss">
@import '../../uni.scss';

.page {
  min-height: 100vh;
  background: $z-bg;
}

.header {
  background: $z-card;
  padding: 0 32rpx 32rpx;
}

.header-mono {
  display: block;
  font-size: 20rpx;
  color: $z-muted;
  letter-spacing: 3rpx;
  margin-bottom: 8rpx;
  padding-top: 16rpx;
}

.header-title {
  display: block;
  font-size: 42rpx;
  font-weight: 900;
  color: $z-text;
  margin-bottom: 6rpx;
}

.header-sub {
  display: block;
  font-size: 24rpx;
  color: $z-muted;
}

// ── 加载态 ───────────────────────────────────────────────────
.loading-screen {
  padding: 60rpx 44rpx 40rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.loading-compass {
  width: 168rpx;
  height: 168rpx;
  border-radius: 84rpx;
  background: linear-gradient(135deg, $z-primary 0%, $z-primary-l 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 16rpx 56rpx rgba(13, 79, 74, 0.33);
  margin-bottom: 32rpx;
}

.compass-spin {
  animation: spinCompass 3s linear infinite;
  display: flex;
  align-items: center;
  justify-content: center;
}

@keyframes spinCompass {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}

.loading-title {
  font-size: 38rpx;
  font-weight: 900;
  color: $z-text;
  margin-bottom: 8rpx;
}

.loading-progress {
  font-size: 22rpx;
  color: $z-muted;
  letter-spacing: 1rpx;
  margin-bottom: 16rpx;
}

.loading-slow-tip {
  font-size: 22rpx;
  color: $z-muted;
  margin-bottom: 24rpx;
  opacity: 0.7;
}

.steps-card {
  width: 100%;
  background: $z-card;
  border-radius: $radius-card;
  padding: 28rpx;
  box-shadow: 0 4rpx 20rpx rgba(13, 79, 74, 0.06);
  margin-bottom: 32rpx;
}

.step-row {
  display: flex;
  align-items: center;
  gap: 20rpx;
  padding: 12rpx 0;
  transition: opacity 0.3s;
}

.step-dot {
  width: 44rpx;
  height: 44rpx;
  border-radius: 22rpx;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: $z-border;

  &.done {
    background: $z-primary;
  }

  &.doing {
    background: rgba(255, 107, 53, 0.13);
  }
}

.dot-pulse {
  width: 16rpx;
  height: 16rpx;
  border-radius: 8rpx;
  background: $z-accent;
  animation: pulse 0.9s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50%       { transform: scale(0.5); opacity: 0.5; }
}

.step-no {
  font-size: 19rpx;
  color: $z-muted;
  font-weight: 700;
}

.step-label {
  font-size: 25rpx;
  color: $z-text;
}

.progress-bar-wrap {
  width: 100%;
  background: $z-border;
  border-radius: $radius-pill;
  height: 10rpx;
  overflow: hidden;
}

.progress-bar-fill {
  height: 10rpx;
  border-radius: $radius-pill;
  background: linear-gradient(90deg, $z-primary 0%, $z-mint 100%);
  transition: width 0.4s ease;
}

// ── 表单态 ───────────────────────────────────────────────────
.scroll-body {
  height: calc(100vh - 200rpx);
}

.form-wrap {
  padding: 24rpx 32rpx 120rpx;
  display: flex;
  flex-direction: column;
  gap: 22rpx;
}

.form-card {
  background: $z-card;
  border-radius: $radius-card;
  padding: 28rpx;
  box-shadow: 0 2rpx 10rpx rgba(13, 79, 74, 0.05);
}

.q-group {
  margin-bottom: 28rpx;

  &:last-child {
    margin-bottom: 0;
  }
}

.q-head {
  display: flex;
  align-items: baseline;
  gap: 14rpx;
  margin-bottom: 16rpx;
}

.q-no {
  font-size: 20rpx;
  color: $z-accent;
  font-weight: 700;
  letter-spacing: 1rpx;
}

.q-label {
  font-size: 26rpx;
  font-weight: 800;
  color: $z-text;
}

.q-hint {
  font-size: 21rpx;
  color: $z-muted;
}

.chips-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 14rpx;
}

.form-chip {
  padding: 12rpx 24rpx;
  border-radius: $radius-pill;
  background: $z-card;
  color: $z-text;
  font-size: 24rpx;
  font-weight: 600;
  cursor: pointer;
  border: 2rpx solid $z-border;
  transition: all 0.2s;

  &.on {
    background: $z-primary;
    color: $z-card;
    border-color: $z-primary;
  }
}

.q6-card {}

.custom-textarea {
  width: 100%;
  min-height: 116rpx;
  border: none;
  background: $z-bg;
  border-radius: 18rpx;
  padding: 18rpx 22rpx;
  font-size: 25rpx;
  color: $z-text;
  font-family: -apple-system, 'PingFang SC', sans-serif;
  box-sizing: border-box;
}

.summary-bar {
  background: rgba(13, 79, 74, 0.055);
  border-left: 6rpx solid $z-primary;
  border-radius: 8rpx 22rpx 22rpx 8rpx;
  padding: 20rpx 24rpx;
}

.summary-mono {
  display: block;
  font-size: 20rpx;
  color: $z-muted;
  letter-spacing: 1rpx;
  margin-bottom: 6rpx;
}

.summary-content {
  font-size: 24rpx;
  color: $z-text;
  line-height: 1.65;
}

.summary-prefs {
  color: $z-primary;
  font-weight: 700;
}

.cta-btn {
  background: linear-gradient(135deg, $z-accent 0%, $z-accent-l 100%);
  box-shadow: 0 12rpx 36rpx rgba(255, 107, 53, 0.44);
  border-radius: 22rpx;
  height: 100rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.cta-text {
  color: $z-card;
  font-size: 30rpx;
  font-weight: 800;
}
</style>
