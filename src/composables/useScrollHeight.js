import { ref, nextTick } from 'vue'

// mp-weixin 下 <scroll-view scroll-y> 必须有显式像素高度才能内部滚动并触发 @scrolltolower；
// 仅靠 flex:1 在部分基础库里不生效（列表只显示首屏、下拉加载不出更多）。
// 用 SelectorQuery 测出 scroll-view 顶部偏移，可用高度 = 窗口高 - 顶部偏移。
export function useScrollHeight(selector) {
  const height = ref(0)
  function measure() {
    nextTick(() => {
      try {
        uni.createSelectorQuery().select(selector).boundingClientRect((rect) => {
          const win = uni.getWindowInfo()
          if (rect && win && win.windowHeight) {
            height.value = Math.max(0, Math.round(win.windowHeight - rect.top))
          }
        }).exec()
      } catch (_) {}
    })
  }
  return { height, measure }
}
