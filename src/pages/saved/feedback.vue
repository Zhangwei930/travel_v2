<template>
  <view class="cy-page">
    <cy-nav-bar title="意见反馈" />

    <scroll-view scroll-y class="cy-scroll">
      <!-- 未登录：前置登录引导 -->
      <view v-if="!profile" class="cy-gate-card">
        <text class="cy-gate-title">登录后才能提交反馈</text>
        <text class="cy-gate-sub">反馈与你的账号关联，仅你自己可见提交记录。</text>
        <view class="cy-gate-btn" @tap="goLogin">去登录</view>
      </view>

      <template v-else>
        <!-- 提交表单 -->
        <view class="cy-form-card">
          <text class="cy-label">反馈类型</text>
          <view class="cy-type-row">
            <view
              v-for="t in TYPES"
              :key="t"
              class="cy-type-chip"
              :class="{ active: type === t }"
              @tap="type = t"
            >{{ t }}</view>
          </view>

          <text class="cy-label">具体描述</text>
          <textarea
            class="cy-textarea"
            v-model="content"
            placeholder="请描述你遇到的问题或建议…"
            placeholder-style="color:#9CA3AF"
            :maxlength="500"
          />
          <text class="cy-count">{{ content.length }}/500</text>

          <text class="cy-label">截图（选填，最多 3 张）</text>
          <view class="cy-img-row">
            <view v-for="(img, i) in images" :key="i" class="cy-img-thumb">
              <image :src="img" mode="aspectFill" class="cy-thumb-img" @tap="previewImg(i)" />
              <view class="cy-img-del" @tap.stop="removeImg(i)">×</view>
            </view>
            <view v-if="images.length < 3" class="cy-img-add" @tap="chooseImages">
              <text class="cy-img-add-plus">+</text>
            </view>
          </view>

          <button class="cy-submit-btn" :disabled="!content.trim() || submitting" @tap="submit">
            {{ submitting ? '提交中…' : '提交反馈' }}
          </button>
        </view>

        <!-- 我的反馈历史（本地） -->
        <view v-if="history.length" class="cy-history">
          <view class="cy-history-head">
            <text class="cy-history-title">我的反馈</text>
            <text class="cy-clear" @tap="clearAllFeedback">清空</text>
          </view>
          <view v-for="h in history" :key="h.id" class="cy-hist-card">
            <view class="cy-hist-meta">
              <text class="cy-hist-type">{{ h.type || '反馈' }}</text>
              <text class="cy-hist-date">{{ formatDate(h.created_at) }}</text>
            </view>
            <text class="cy-hist-content">{{ h.content }}</text>
            <view v-if="h.images && h.images.length" class="cy-hist-imgs-row">
              <image
                v-for="(img, k) in h.images"
                :key="k"
                :src="img"
                mode="aspectFill"
                class="cy-hist-thumb"
                @tap="uni.previewImage({ current: img, urls: h.images })"
              />
            </view>
            <view class="cy-hist-foot">
              <text class="cy-hist-status">已提交</text>
              <text class="cy-hist-del" @tap="removeFeedback(h)">删除</text>
            </view>
          </view>
        </view>
      </template>

      <view style="height: 32rpx;" />
    </scroll-view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { api } from '../../api/index.js'
import { ensureDefaultProfile, addMyFeedback, getMyFeedback, removeMyFeedback, clearMyFeedback } from '../../api/storage.js'
import CyNavBar from '../../components/cy/cy-nav-bar.vue'

const TYPES = ['功能异常', '内容纠错', '体验建议', '其他']
const profile    = ref(null)
const type       = ref('体验建议')
const content    = ref('')
const images     = ref([])   // 本地临时路径，仅用于预览
const submitting = ref(false)
const history    = ref([])

onShow(() => {
  profile.value = ensureDefaultProfile()   // 进小程序即有默认档，反馈不再需要登录拦截
  history.value = getMyFeedback()
})

function goLogin() {
  uni.switchTab({ url: '/pages/profile/profile' })
}

function chooseImages() {
  const remain = 3 - images.value.length
  if (remain <= 0) return
  uni.chooseMedia({
    count: remain,
    mediaType: ['image'],
    sizeType: ['compressed'],
    sourceType: ['album', 'camera'],
    success: (res) => {
      res.tempFiles.forEach(f => { if (f.tempFilePath) images.value.push(f.tempFilePath) })
    },
  })
}

function removeImg(i) { images.value.splice(i, 1) }
function previewImg(i) { uni.previewImage({ current: images.value[i], urls: images.value }) }

// 截图持久化：chooseMedia 的临时路径重启后失效，需 saveFile 转永久路径供本地历史展示
function persistImage(path) {
  return new Promise((resolve) => {
    // #ifdef MP-WEIXIN
    uni.saveFile({
      tempFilePath: path,
      success: (res) => resolve(res.savedFilePath),
      fail: () => resolve(path),
    })
    // #endif
    // #ifndef MP-WEIXIN
    resolve(path)
    // #endif
  })
}

// 读成 base64 data URL，随反馈上传到服务器供开发者查看
function readBase64(path) {
  return new Promise((resolve) => {
    // #ifdef MP-WEIXIN
    uni.getFileSystemManager().readFile({
      filePath: path,
      encoding: 'base64',
      success: (r) => resolve('data:image/jpeg;base64,' + r.data),
      fail: () => resolve(''),
    })
    // #endif
    // #ifndef MP-WEIXIN
    resolve('')
    // #endif
  })
}

async function submit() {
  const text = content.value.trim()
  if (!text || submitting.value) return
  submitting.value = true
  try {
    const who = profile.value?.name ? `（${profile.value.name}）` : ''
    let imgData = []
    // #ifdef MP-WEIXIN
    imgData = (await Promise.all(images.value.map(readBase64))).filter(Boolean)
    // #endif
    await api.sendFeedback({
      target_type: 'app',
      comment: `[${type.value}]${who} ${text}`,
      images: imgData,
    })
    const savedImgs = await Promise.all(images.value.map(persistImage))
    addMyFeedback({ type: type.value, content: text, images: savedImgs })
    uni.showToast({ title: '已提交，感谢反馈', icon: 'success' })
    content.value = ''
    images.value = []
    history.value = getMyFeedback()
  } catch (e) {
    uni.showToast({ title: '提交失败，请稍后重试', icon: 'none' })
  } finally {
    submitting.value = false
  }
}

function removeFeedback(h) {
  uni.showModal({
    title: '删除反馈', content: '确定删除这条反馈记录？（仅删本机记录）',
    success: (r) => {
      if (!r.confirm) return
      removeMyFeedback(h.id)
      history.value = getMyFeedback()
      uni.showToast({ title: '已删除', icon: 'none' })
    },
  })
}
function clearAllFeedback() {
  uni.showModal({
    title: '清空反馈', content: '确定清空全部本机反馈记录？',
    success: (r) => {
      if (!r.confirm) return
      clearMyFeedback()
      history.value = getMyFeedback()
      uni.showToast({ title: '已清空', icon: 'none' })
    },
  })
}

function formatDate(ts) {
  if (!ts) return ''
  const d = new Date(ts)
  if (Number.isNaN(d.getTime())) return ''
  const p = n => String(n).padStart(2, '0')
  return `${d.getMonth() + 1}/${d.getDate()} ${p(d.getHours())}:${p(d.getMinutes())}`
}
</script>

<style lang="scss">
@import '../../uni.scss';

.cy-page {
  min-height: 100vh;
  background: $cy-bg;
  font-family: "PingFang SC", "HarmonyOS Sans SC", "Noto Sans SC", -apple-system, system-ui, sans-serif;
}

.cy-scroll { padding: 20rpx 24rpx 32rpx; box-sizing: border-box; }

// ── 登录前置 ───────────────────────────────────────────────
.cy-gate-card {
  margin-top: 60rpx;
  background: $cy-card;
  border-radius: 24rpx;
  padding: 48rpx 36rpx;
  text-align: center;
  box-shadow: $cy-shadow;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16rpx;
}

.cy-gate-title { font-size: 30rpx; font-weight: 800; color: $cy-text; }
.cy-gate-sub   { font-size: 24rpx; color: $cy-muted; line-height: 1.5; }
.cy-gate-btn {
  margin-top: 16rpx;
  height: 76rpx; padding: 0 56rpx;
  border-radius: 38rpx; background: $cy-green; color: #fff;
  font-size: 28rpx; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
}

// ── 表单卡 ─────────────────────────────────────────────────
.cy-form-card {
  background: $cy-card;
  border-radius: 24rpx;
  padding: 28rpx 24rpx 32rpx;
  box-shadow: $cy-shadow;
}

.cy-label {
  display: block;
  font-size: 26rpx;
  font-weight: 700;
  color: $cy-text;
  margin: 8rpx 0 16rpx;
}

.cy-type-row { display: flex; flex-wrap: wrap; gap: 16rpx; margin-bottom: 24rpx; }

.cy-type-chip {
  padding: 12rpx 28rpx;
  border-radius: 32rpx;
  background: $cy-green-ls;
  border: 1rpx solid $cy-border;
  font-size: 26rpx; color: $cy-text-sub;

  &.active {
    background: $cy-green-l;
    border-color: $cy-green;
    color: $cy-green;
    font-weight: 700;
  }
}

.cy-textarea {
  width: 100%;
  height: 200rpx;
  background: $cy-green-ls;
  border: 1rpx solid $cy-border;
  border-radius: 16rpx;
  padding: 20rpx 24rpx;
  box-sizing: border-box;
  font-size: 28rpx;
  color: $cy-text;
  line-height: 1.5;
}

.cy-count { display: block; text-align: right; font-size: 22rpx; color: $cy-muted; margin: 8rpx 0 24rpx; }

// 截图上传
.cy-img-row { display: flex; flex-wrap: wrap; gap: 16rpx; margin-bottom: 32rpx; }

.cy-img-thumb { position: relative; width: 150rpx; height: 150rpx; }
.cy-thumb-img { width: 100%; height: 100%; border-radius: 16rpx; background: $cy-green-ls; }
.cy-img-del {
  position: absolute; top: -12rpx; right: -12rpx;
  width: 40rpx; height: 40rpx; border-radius: 20rpx;
  background: rgba(0,0,0,0.55); color: #fff; font-size: 30rpx;
  display: flex; align-items: center; justify-content: center;
  line-height: 1;
}

.cy-img-add {
  width: 150rpx; height: 150rpx;
  border-radius: 16rpx;
  border: 1rpx dashed $cy-border;
  background: $cy-green-ls;
  display: flex; align-items: center; justify-content: center;
}
.cy-img-add-plus { font-size: 56rpx; color: $cy-muted; line-height: 1; }

.cy-submit-btn {
  width: 100%; height: 92rpx; border-radius: 46rpx;
  background: $cy-green; color: #fff; font-size: 30rpx; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  border: none;
  &[disabled] { opacity: 0.45; }
}

// ── 历史 ───────────────────────────────────────────────────
.cy-history { margin-top: 32rpx; }
.cy-history-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16rpx; }
.cy-history-title { display: block; font-size: 28rpx; font-weight: 800; color: $cy-text; }
.cy-clear { font-size: 24rpx; color: $cy-muted; }

.cy-hist-card {
  background: $cy-card;
  border-radius: 20rpx;
  padding: 24rpx;
  margin-bottom: 16rpx;
  box-shadow: $cy-shadow;
}

.cy-hist-meta { display: flex; justify-content: space-between; margin-bottom: 10rpx; }
.cy-hist-type { font-size: 24rpx; color: $cy-green; font-weight: 700; }
.cy-hist-date { font-size: 22rpx; color: $cy-muted; }
.cy-hist-content { display: block; font-size: 26rpx; color: $cy-text; line-height: 1.55; }
.cy-hist-imgs-row { display: flex; flex-wrap: wrap; gap: 12rpx; margin-top: 14rpx; }
.cy-hist-thumb { width: 120rpx; height: 120rpx; border-radius: 12rpx; background: $cy-green-ls; }
.cy-hist-foot { display: flex; justify-content: space-between; align-items: center; margin-top: 12rpx; }
.cy-hist-status { font-size: 22rpx; color: $cy-green; }
.cy-hist-del { font-size: 22rpx; color: #E0533D; padding: 4rpx 8rpx; }
</style>
