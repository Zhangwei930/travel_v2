// 后端接口请求封装 —— BASE_URL 通过 vite.config.js 的 `define` 注入为字面量。
// 不能直接读 import.meta.env：mp-weixin 输出会把 typeof import.meta 编成
// require("url") 的 polyfill，小程序里 require 不到 url 模块会抛错，导致 BASE_URL 兜底为空。
//
// fail-fast：在小程序运行时 BASE_URL 为空（小程序不支持相对 URL）→ 抛错。

// __ZHOUMI_API_BASE__ 由 vite.config.js define 注入为字符串字面量
// eslint-disable-next-line no-undef
export const BASE_URL = String(__ZHOUMI_API_BASE__ || '').replace(/\/+$/, '')

// 小程序场景下 BASE_URL 空 = 配置缺失（小程序没有"相对路径走代理"能力）
// #ifdef MP-WEIXIN || MP-ALIPAY || MP-BAIDU || MP-TOUTIAO || MP-QQ
if (!BASE_URL) {
  console.error('[zhoumi] 小程序构建必须配置 VITE_API_BASE，否则所有 API 都会失败')
}
// #endif

export function request(path, { method = 'GET', data, header } = {}) {
  return new Promise((resolve, reject) => {
    const isAbs = /^https?:\/\//i.test(path)
    if (!isAbs && !BASE_URL) {
      // #ifdef MP-WEIXIN || MP-ALIPAY || MP-BAIDU || MP-TOUTIAO || MP-QQ
      reject(new Error('API_BASE_NOT_CONFIGURED'))
      return
      // #endif
      // H5 dev：空 BASE_URL 表示走 vite.config.js 的 proxy，相对路径直接发即可
    }
    uni.request({
      url: isAbs ? path : (BASE_URL + path),
      method,
      data,
      timeout: 40000,
      header: { 'Content-Type': 'application/json', ...header },
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
        } else {
          reject(new Error(`HTTP ${res.statusCode}`))
        }
      },
      fail: (err) => reject(err),
    })
  })
}
