// 微信隐私授权：正式版调 getLocation 等隐私接口前，须先让用户同意「用户隐私保护指引」，
// 否则正式环境会直接拒绝（体验版/调试版宽松，所以只在正式版暴露）。
// 后台配好隐私指引并生效后，本流程会弹出官方授权框；同意后定位放行。
export function ensureLocationAuthorize() {
  return new Promise((resolve) => {
    // #ifdef MP-WEIXIN
    if (typeof wx !== 'undefined' && typeof wx.requirePrivacyAuthorize === 'function') {
      wx.requirePrivacyAuthorize({
        // 同意/拒绝/后台未配置 都继续：让后续 getLocation 自然走（成功或回落到定位页），不卡死
        complete: () => resolve(),
      })
      return
    }
    // #endif
    resolve()
  })
}
