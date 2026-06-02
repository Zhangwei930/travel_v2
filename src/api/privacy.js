// 微信隐私授权：调 getLocation 等隐私接口前，须先让用户同意「用户隐私保护指引」。
//
// ⚠ 启用顺序很重要：必须先在 MP 后台配好「用户隐私保护指引」并审核生效，
// 才能开启 manifest 的 "__usePrivacyCheck__": true + 下面的 requirePrivacyAuthorize。
// 否则在后台没配指引时，__usePrivacyCheck__ 会把 getLocation 直接拦掉（连真机预览也走兜底）。
//
// 当前：后台指引未生效，本函数空转（不拦定位）。后台配好后，把下面 PRIVACY_READY 改 true
// 并在 manifest mp-weixin 加回 "__usePrivacyCheck__": true 即可启用。
const PRIVACY_READY = true

export function ensureLocationAuthorize() {
  return new Promise((resolve) => {
    // #ifdef MP-WEIXIN
    if (PRIVACY_READY && typeof wx !== 'undefined' && typeof wx.requirePrivacyAuthorize === 'function') {
      wx.requirePrivacyAuthorize({ complete: () => resolve() })
      return
    }
    // #endif
    resolve()
  })
}
