// 后端接口请求封装 —— BASE_URL 按平台 + 环境读取
//
// 优先级（高到低）：
//   1. import.meta.env.VITE_API_BASE         (Vite，H5 + 小程序 Vite 模式)
//   2. process.env.VUE_APP_API_BASE          (兼容 vue-cli 模式)
//   3. 空字符串 ''                            (H5 dev 走 vite.config.js 代理)
//
// fail-fast：在小程序运行时 BASE_URL 为空（小程序不支持相对 URL）→ 抛错。

function readEnvBase() {
  try {
    if (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_API_BASE != null) {
      return String(import.meta.env.VITE_API_BASE).replace(/\/+$/, '')
    }
  } catch (_) {}
  try {
    if (typeof process !== 'undefined' && process.env && process.env.VUE_APP_API_BASE != null) {
      return String(process.env.VUE_APP_API_BASE).replace(/\/+$/, '')
    }
  } catch (_) {}
  return ''
}

export const BASE_URL = readEnvBase()

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
      timeout: 20000,
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
