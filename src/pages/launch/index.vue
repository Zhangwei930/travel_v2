<template>
  <view class="cy-launch">
    <image src="/static/images/splash-map.png" class="cy-splash" mode="aspectFit" />
  </view>
</template>

<script setup>
import { onShow } from '@dcloudio/uni-app'
import { useCityStore } from '../../store/city.js'

const cityStore = useCityStore()

// 用 onShow 代替 onMounted，确保页面栈已稳定再发起导航
let bootstrapped = false
let guard = null
onShow(() => {
  if (bootstrapped) return
  bootstrapped = true
  bootstrap()
})

function gotoHome()     { uni.reLaunch({ url: '/pages/index/index' }) }
function gotoLocation() {
  if (guard) {
    clearTimeout(guard)
    guard = null
  }
  uni.reLaunch({ url: '/pages/location/index' })
}

function navigate(dest) {
  // 套一层 nextTick 再导航，彻底避免 appLaunch 阶段的页面栈冲突
  // #ifdef MP-WEIXIN
  wx.nextTick(dest)
  // #endif
  // #ifndef MP-WEIXIN
  dest()
  // #endif
}

async function bootstrap() {
  // 等框架完成 appLaunch 渲染周期
  await new Promise(r => setTimeout(r, 600))

  let settled = false

  guard = setTimeout(() => {
    if (settled) return
    settled = true
    navigate(gotoLocation)
  }, 5000)

  uni.getLocation({
    type: 'gcj02',
    success: (r) => {
      if (settled) return
      settled = true
      clearTimeout(guard)
      cityStore.setCoords(r.latitude, r.longitude)
      cityStore.locationDenied = false
      navigate(gotoHome)
    },
    fail: () => { gotoLocation() },
  })
}
</script>

<style lang="scss">
.cy-launch {
  width: 100%;
  height: 100vh;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cy-splash {
  width: 100%;
  height: 100vh;
}
</style>
